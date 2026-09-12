"""Smoke tests for CalibratedTransitionModule."""
from __future__ import annotations

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from calibrated_transition import CalibratedTransitionModule, make_ctm, RoutingResult


def test_route_three_signals():
    ctm = CalibratedTransitionModule(theta_low=0.3, theta_high=0.7)
    result = ctm.route(np.array([0.1, 0.5, 0.9]))
    assert isinstance(result, RoutingResult)
    assert result.q.shape == (3,)
    assert result.C.shape == (3, 3)
    assert abs(result.A.sum() - 1.0) < 1e-6
    assert set(result.decisions) <= {"admit", "quarantine", "reject"}


def test_build_C_symmetric():
    C = CalibratedTransitionModule.build_C(np.array([0.2, 0.5, 0.8]))
    np.testing.assert_allclose(C, C.T, atol=1e-12)
    np.testing.assert_allclose(np.diag(C), np.ones(3), atol=1e-12)


def test_rejects_nan():
    ctm = CalibratedTransitionModule()
    with pytest.raises(ValueError, match="NaN"):
        ctm.route(np.array([0.1, np.nan, 0.9]))


def test_factory():
    ctm = make_ctm(dynamic_tau=True)
    result = ctm.route(np.array([0.2, 0.5, 0.8]))
    assert np.all(np.isfinite(result.q))
