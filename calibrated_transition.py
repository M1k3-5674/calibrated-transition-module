"""
calibrated_transition.py
========================
Production-ready, numerically hardened implementation of the
CalibratedTransitionModule (CTM).

Routing decision
----------------
  admit      : q_i < theta_low
  quarantine : theta_low <= q_i < theta_high
  reject     : q_i >= theta_high

Author: Mike / CalibratedTransitionModule dev-package
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple, Union

import numpy as np
from numpy.typing import ArrayLike, NDArray

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

ThresholdSpec = Union[float, ArrayLike]
TauSpec = Union[float, Callable[[NDArray], NDArray]]


@dataclass
class RoutingResult:
    """Structured output returned by :meth:`CalibratedTransitionModule.route`."""
    signals: NDArray
    q: NDArray
    C: NDArray
    A: NDArray
    decisions: List[str]
    admitted_idx: NDArray
    quarantine_idx: NDArray
    rejected_idx: NDArray
    latency_s: float
    metadata: Dict = field(default_factory=dict)

    def summary(self) -> str:
        n = len(self.signals)
        return (
            f"RoutingResult | n={n} | "
            f"admit={len(self.admitted_idx)} "
            f"quarantine={len(self.quarantine_idx)} "
            f"reject={len(self.rejected_idx)} | "
            f"latency={self.latency_s*1000:.2f} ms"
        )


class CalibratedTransitionModule:
    """Routes signals based on calibrated uncertainty scores."""

    def __init__(
        self,
        theta_low: ThresholdSpec = 0.3,
        theta_high: ThresholdSpec = 0.7,
        tau: TauSpec = 1.0,
        eps: float = 1e-8,
        min_signals: int = 2,
    ) -> None:
        self.theta_low = theta_low
        self.theta_high = theta_high
        self.tau = tau
        self.eps = float(eps)
        self.min_signals = int(min_signals)
        logger.info(
            "CTM initialised | theta_low=%s theta_high=%s tau=%s eps=%s",
            theta_low, theta_high, tau, eps,
        )

    def route(
        self,
        signals: ArrayLike,
        C: Optional[ArrayLike] = None,
        *,
        metadata: Optional[Dict] = None,
    ) -> RoutingResult:
        t0 = time.perf_counter()
        signals = np.asarray(signals, dtype=np.float64)
        n = signals.shape[0]
        self._validate_signals(signals)
        if C is None:
            C_mat = self.build_C(signals)
        else:
            C_mat = np.asarray(C, dtype=np.float64)
            self._validate_C(C_mat, n)
        A = self._compute_A(C_mat)
        q = self._compute_q(signals, A)
        theta_low = np.broadcast_to(np.asarray(self.theta_low, dtype=np.float64), (n,))
        theta_high = np.broadcast_to(np.asarray(self.theta_high, dtype=np.float64), (n,))
        decisions, admitted, quarantined, rejected = self._decide(q, theta_low, theta_high)
        latency = time.perf_counter() - t0
        return RoutingResult(
            signals=signals, q=q, C=C_mat, A=A, decisions=decisions,
            admitted_idx=admitted, quarantine_idx=quarantined,
            rejected_idx=rejected, latency_s=latency, metadata=metadata or {},
        )

    @staticmethod
    def build_C(signals: NDArray) -> NDArray:
        s = np.asarray(signals, dtype=np.float64)
        diff = np.abs(s[:, None] - s[None, :])
        return np.exp(-diff)

    def _compute_A(self, C: NDArray) -> NDArray:
        n = C.shape[0]
        mask = ~np.eye(n, dtype=bool)
        raw = np.where(mask, C, 0.0).sum(axis=1)
        tau = self._resolve_tau(C)
        scaled = raw / (tau + self.eps)
        scaled -= scaled.max()
        exp_scaled = np.exp(scaled)
        return exp_scaled / (exp_scaled.sum() + self.eps)

    def _resolve_tau(self, C: NDArray) -> NDArray:
        if callable(self.tau):
            tau = np.asarray(self.tau(C), dtype=np.float64)
            return np.clip(tau, self.eps, None)
        return float(self.tau)

    def _compute_q(self, signals: NDArray, A: NDArray) -> NDArray:
        _ = signals
        deviation = A - A.mean()
        q = 1.0 / (1.0 + np.exp(-deviation / (A.std() + self.eps)))
        return np.clip(q, self.eps, 1.0 - self.eps)

    @staticmethod
    def _decide(q: NDArray, theta_low: NDArray, theta_high: NDArray):
        admit_mask = q < theta_low
        reject_mask = q >= theta_high
        quarantine_mask = ~admit_mask & ~reject_mask
        decisions = [""] * len(q)
        for i in range(len(q)):
            if admit_mask[i]:
                decisions[i] = "admit"
            elif reject_mask[i]:
                decisions[i] = "reject"
            else:
                decisions[i] = "quarantine"
        return decisions, np.where(admit_mask)[0], np.where(quarantine_mask)[0], np.where(reject_mask)[0]

    @staticmethod
    def C_max_masked(C: NDArray) -> float:
        n = C.shape[0]
        mask = ~np.eye(n, dtype=bool)
        return float(C[mask].max())

    def _validate_signals(self, signals: NDArray) -> None:
        if signals.ndim != 1:
            raise ValueError(f"signals must be 1-D, got shape {signals.shape}")
        if signals.shape[0] < self.min_signals:
            raise ValueError(f"At least {self.min_signals} signals required, got {signals.shape[0]}")
        if not np.all(np.isfinite(signals)):
            raise ValueError("signals contain NaN or Inf")

    @staticmethod
    def _validate_C(C: NDArray, n: int) -> None:
        if C.shape != (n, n):
            raise ValueError(f"C must be ({n},{n}), got {C.shape}")
        if not np.allclose(C, C.T, atol=1e-6):
            raise ValueError("C must be symmetric")
        if not np.all(np.isfinite(C)):
            raise ValueError("C contains NaN or Inf")
        if C.min() < 0.0 or C.max() > 1.0 + 1e-6:
            raise ValueError("C values must be in [0, 1]")


def make_ctm(theta_low: float = 0.3, theta_high: float = 0.7, tau: float = 1.0, dynamic_tau: bool = False) -> CalibratedTransitionModule:
    if dynamic_tau:
        def _dynamic(C: NDArray) -> NDArray:
            return np.clip(C.std(axis=1), 0.1, 10.0)
        tau_spec: TauSpec = _dynamic
    else:
        tau_spec = tau
    return CalibratedTransitionModule(theta_low=theta_low, theta_high=theta_high, tau=tau_spec)
