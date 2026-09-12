"""Minimal demo. python integration_example.py --quiet"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from calibrated_transition import CalibratedTransitionModule, make_ctm


def run_demo(signals, ledger_path: str, theta_low: float, theta_high: float, quiet: bool) -> None:
    sig_arr = np.array(signals, dtype=np.float64)
    ctm = make_ctm(theta_low=theta_low, theta_high=theta_high)
    result = ctm.route(sig_arr, metadata={"theta_low": theta_low, "theta_high": theta_high})
    print("CalibratedTransitionModule — demo")
    print(f"signals: {sig_arr.tolist()}")
    print(f"theta_low={theta_low}  theta_high={theta_high}")
    print()
    for i, (sig, q, decision) in enumerate(zip(result.signals, result.q, result.decisions)):
        mark = {"admit": "ALLOW", "quarantine": "MARK", "reject": "REJECT"}[decision]
        print(f"  [{mark:<6}] signal[{i}]={sig:.3f}  q={q:.4f}  -> {decision}")
    print()
    print(result.summary())
    print(f"C_max (off-diag): {CalibratedTransitionModule.C_max_masked(result.C):.4f}")
    path = Path(ledger_path)
    rows = [{"signal_index": i, "signal_value": float(sig), "q": float(q), "decision": decision}
            for i, (sig, q, decision) in enumerate(zip(result.signals, result.q, result.decisions))]
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    print(f"ledger: {path.resolve()}")
    if not quiet:
        print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CTM demo")
    parser.add_argument("--signals", type=float, nargs="+", default=None)
    parser.add_argument("--ledger-path", default="evidence_ledger.jsonl")
    parser.add_argument("--theta-low", type=float, default=0.3)
    parser.add_argument("--theta-high", type=float, default=0.7)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    run_demo(
        signals=args.signals or [0.05, 0.15, 0.42, 0.48, 0.55, 0.71, 0.88, 0.95],
        ledger_path=args.ledger_path,
        theta_low=args.theta_low,
        theta_high=args.theta_high,
        quiet=args.quiet,
    )
