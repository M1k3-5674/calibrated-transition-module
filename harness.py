"""Light scale check. python harness.py --suite normal"""
from __future__ import annotations

import argparse
import time

import numpy as np

from calibrated_transition import make_ctm


def run(suite: str) -> None:
    ctm = make_ctm()
    sizes = [10, 50, 100, 200] if suite in (None, "normal", "scale") else [50]
    print(f"{'n':>6}  {'admit':>7}  {'quar':>7}  {'reject':>7}  {'ms':>8}")
    rng = np.random.default_rng(0)
    for n in sizes:
        signals = rng.uniform(0, 1, n)
        t0 = time.perf_counter()
        result = ctm.route(signals)
        ms = (time.perf_counter() - t0) * 1000
        print(
            f"{n:6d}  {len(result.admitted_idx):7d}  "
            f"{len(result.quarantine_idx):7d}  {len(result.rejected_idx):7d}  {ms:8.2f}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="normal")
    args = parser.parse_args()
    run(args.suite)
