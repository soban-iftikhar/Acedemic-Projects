# AMDA: Agentic Micro-Decision Advisor

## Prerequisites
- Python 3.10+
- Dependencies: `numpy`, `scikit-fuzzy`

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
### Non-interactive modes
Run without prompts using CLI flags:
```bash
# Quick demo and exit
python amda.py --mode quick

# Demo (predefined scenarios)
python amda.py --mode demo

# Interactive mode directly
python amda.py --mode interactive
```
If using a virtualenv, you can run explicitly via its Python:
```bash
./.venv/bin/python amda.py --mode quick
```
Interactive menu appears on start:
python amda.py
```
- Enter `3` for a quick demo.
- Enter `1` for full demo then interactive.
- Enter `2` for interactive mode.

## Troubleshooting
- If you see `ModuleNotFoundError: No module named 'skfuzzy'`, you are likely using system Python.
  - Activate the virtualenv: `source .venv/bin/activate`
  - Or run explicitly: `./.venv/bin/python amda.py`
