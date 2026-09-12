# Calibrated Transition Module

**Author:** Kevin Michael Lent (“Mike”)  
**Copyright:** (c) 2026 Kevin Michael Lent  
**License:** [TSG Source-Available License v1.1](LICENSE)  
**Official source:** https://github.com/M1k3-5674/calibrated-transition-module

CTM routes a batch of numbers into **admit**, **quarantine**, or **reject**.  
The Transition Layer v3.0 contract is the same three-way gate for AI output: **ALLOW / MARK / REJECT**.

You do not need to be a trained coder to run the demo.

## License in one page

| Allowed | Not allowed without a commercial grant |
|---|---|
| View, clone, study | Sell this pack or a product whose main value is this software |
| Run and modify for personal, research, evaluation, internal non-commercial use | Paid hosted service, paid seats, paid support contracts for this software |
| Share copies that keep LICENSE, NOTICE, and credit | Rebrand the work as yours |
| Send pull requests | Own the project name or future paid versions |

Public forks and ports must open an issue titled **Derivative notice** on this repo.  
Paid use: open an issue titled **Commercial grant**. See [COMMERCIAL.md](COMMERCIAL.md).

This is not MIT. Continuation is allowed. The product and future money stay with the author.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python integration_example.py --quiet
pytest tests/test_calibrated_transition.py -q
```

Windows: `python -m venv .venv` then `.\.venv\Scripts\Activate.ps1`.

See [USAGE.txt](USAGE.txt).

## Files

- `calibrated_transition.py` — the module
- `integration_example.py` — demo
- `harness.py` — scale check
- `tests/` — unit tests (58 passed at 1.0.0)
- `docs/TRANSITION_LAYER_v3.md` — locked interface contract
- `LICENSE` `NOTICE` `CONTRIBUTING.md` `COMMERCIAL.md`

## Version

1.0.0 — 2026-09-12
