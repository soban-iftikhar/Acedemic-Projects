# AMDA: Agentic Micro-Decision Advisor (Fuzzy Utility Agent)

The Agentic Micro-Decision Advisor (AMDA) recommends the single best micro-action to take next (study, rest, exercise, plan, and more). It blends classic Utility Theory with a Fuzzy Logic Inference System to avoid brittle, rule-only behavior and to reason smoothly over vague human inputs.

## Table of Contents
1. [Project Summary](#1-project-summary)
2. [Core Methods](#2-core-methods)
3. [Inputs and Actions](#3-inputs-and-actions)
4. [Architecture](#4-architecture)
5. [Setup](#5-setup)
6. [How to Run](#6-how-to-run)
7. [Interpreting the Output](#7-interpreting-the-output)
8. [Extending the Agent](#8-extending-the-agent)

---

## 1. Project Summary

Traditional crisp rules like "IF stress > 0.7" break down when user inputs sit near boundaries or are imprecise. AMDA replaces those cliffs with fuzzy membership functions and weighted utility deltas, so recommendations change gradually and stay intuitive.

## 2. Core Methods

- **Utility selection:** choose $a^*$ that maximizes total utility $U_{\text{total}}(a) = U_{\text{base}}(a) + \sum_{r \in R} \Delta U_r(a)$.
- **Fuzzy activation:** each rule computes an activation strength $\alpha_r \in [0,1]$ via membership functions and t-norms; its contribution is $\Delta U_r = \alpha_r \times \text{Effect}_r$.
- **Tie-breaking:** when utilities are close (within $\varepsilon=0.1$), health-rest actions lead, then deadline-focused actions, then avoid repeating the last action.

## 3. Inputs and Actions

- **Inputs (all normalized to [0, 1]):** energy, stress, mental focus, physical fatigue, mood, deadline status, time available (normalized to 0-120 minutes).
- **Action space:** study, do_easy_task, gym, short_break, deep_rest, relax_activity, avoid_distractions, plan_next_steps.

## 4. Architecture

1. **Perceive:** map user inputs to numeric beliefs and fuzzy sets (low/medium/high, short/medium/long time, none/near/urgent deadline).
2. **Reason:** evaluate fuzzy rule activations and weight their utility effects.
3. **Decide:** argmax with deterministic tie-breaking to keep health-first and reduce action repetition.
4. **Explain:** print the winning action, top contributing rules, and a concise suggestion.

## 5. Setup

Python 3.9+ is recommended.

```bash
# (optional) create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install dependencies for the fuzzy agent
pip install numpy scikit-fuzzy
```

## 6. How to Run

### Full fuzzy agent
The main agent lives in AMDA/amda.py.

```bash
cd AMDA
python amda.py
```

You will be prompted to choose a mode:
- **Demo:** runs one of several predefined scenarios and prints the full explanation plus a utility table.
- **Interactive:** enter your current state repeatedly; type `demo` inside the loop to preview scenarios or `quit` to exit.

### Simplified rules-only demo
For a lightweight, beginner-friendly version without fuzzy logic, use AMDA/amda_simple.py.

```bash
cd AMDA
python amda_simple.py
```

It asks for feelings (energy, stress 1-10, time, deadline, mood) and shows which rules fired and why the suggested action wins.

## 7. Interpreting the Output

- **Recommended action:** the chosen micro-action plus a short suggestion.
- **Top contributing rules:** rules sorted by absolute impact, scaled by their activation strength $\alpha_r$.
- **Utility table (demo mode):** base utility, total utility, and top rule deltas for every action to visualize trade-offs.

## 8. Extending the Agent

- Add a new fuzzy rule: extend `_initialize_rules()` in AMDA/amda.py with a new Rule that computes an activation strength and effects.
- Adjust base priors: tweak `self.base_utilities` in the AMDA constructor to change neutral preferences.
- Change inputs: update `get_user_input()` and the membership functions in `_setup_fuzzy_control()` if you add new signals.
