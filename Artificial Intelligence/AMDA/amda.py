"""
Agentic Micro-Decision Advisor (AMDA) - Fuzzy Logic Enhanced
A lightweight, single-agent AI system that recommends micro-actions 
based on user context and fuzzy utility-based decision making.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import random
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl 

# ENUMS AND DATA STRUCTURES


class BeliefLabel(Enum):
    """Symbolic labels for discrete beliefs."""
    LOW = 0.0
    MEDIUM = 0.5
    HIGH = 1.0


class Action(Enum):
    """Action space: micro-actions the agent can recommend."""
    STUDY = "study"
    DO_EASY_TASK = "do_easy_task"
    GYM = "gym"
    SHORT_BREAK = "short_break"
    DEEP_REST = "deep_rest"
    RELAX_ACTIVITY = "relax_activity"
    AVOID_DISTRACTIONS = "avoid_distractions"
    PLAN_NEXT_STEPS = "plan_next_steps"


@dataclass
class Belief:
    """Represents a single belief with symbolic and numeric value."""
    name: str
    value: str  # symbolic: 'low', 'medium', 'high', or numeric string
    numeric_strength: float  # [0.0, 1.0]
    
    def __repr__(self):
        return f"Belief({self.name}={self.value})"


@dataclass
class Rule:
    """
    Production rule: preconditions → utility deltas.
    Preconditions must now return the FUZZY ACTIVATION STRENGTH [0.0, 1.0].
    """
    name: str
    preconditions: callable  # function(beliefs_dict) -> float (activation strength)
    effects: Dict[Action, float]  # action -> delta contribution
    weight: float = 1.0  # priority for tie-breaking
    description: str = ""


@dataclass
class UtilityScore:
    """Result of utility computation for an action."""
    action: Action
    base_utility: float
    contributions: Dict[str, float]  # rule_name -> delta
    total_utility: float
    
    def __repr__(self):
        return f"{self.action.value}: {self.total_utility:.2f}"


# ============================================================================
# AGENTIC MICRO-DECISION ADVISOR
# ============================================================================

class AMDA:
    """Main AMDA Agent: perceive → reason → act → explain."""
    
    def __init__(self):
        """Initialize the agent with base utilities, rules, and state."""
        self.beliefs: Dict[str, Belief] = {}
        self.last_action: Optional[Action] = None
        self.iteration: int = 0
        
        # Base utilities for each action (neutral priors)
        self.base_utilities: Dict[Action, float] = {
            Action.STUDY: 0.3,
            Action.DO_EASY_TASK: 0.4,
            Action.GYM: 0.35,
            Action.SHORT_BREAK: 0.5,
            Action.DEEP_REST: 0.2,
            Action.RELAX_ACTIVITY: 0.25,
            Action.AVOID_DISTRACTIONS: 0.15,
            Action.PLAN_NEXT_STEPS: 0.5,
        }
        
        # NEW: Setup fuzzy logic components (must run before initializing rules)
        self.fuzzy_antecedents = self._setup_fuzzy_control()

        # Initialize rule set
        self.rules: List[Rule] = self._initialize_rules()
    
    # ========================================================================
    # FUZZY LOGIC SETUP
    # ========================================================================
    
    def _setup_fuzzy_control(self):
        """
        Defines the universe of discourse and membership functions (MFs) 
        for all input variables.
        """
        # All beliefs are scaled [0.0, 1.0]. We use a universe of [0, 10] for better MF definition.
        
        # Generic Antecedent for level-based inputs (Energy, Stress, Fatigue, Focus, Mood)
        level_universe = np.arange(0, 11, 1)
        level = ctrl.Antecedent(level_universe, 'level')
        
        # Time Available (e.g., [0, 120] minutes, normalized to [0, 10])
        time_universe = np.arange(0, 11, 1)
        time_norm = ctrl.Antecedent(time_universe, 'time_norm')
        
        # Deadline Status
        deadline_universe = np.arange(0, 11, 1)
        deadline = ctrl.Antecedent(deadline_universe, 'deadline')

        # Mood (separate antecedent to support bad/okay/good labels)
        mood_universe = np.arange(0, 11, 1)
        mood = ctrl.Antecedent(mood_universe, 'mood')

        # Membership Functions for Level
        level['low'] = fuzz.trimf(level_universe, [0, 0, 5])
        level['medium'] = fuzz.trimf(level_universe, [0, 5, 10])
        level['high'] = fuzz.trimf(level_universe, [5, 10, 10])

        # Membership Functions for Time Available
        time_norm['short'] = fuzz.trimf(time_universe, [0, 0, 3])
        time_norm['medium'] = fuzz.trimf(time_universe, [2, 5, 8])
        time_norm['long'] = fuzz.trimf(time_universe, [7, 10, 10])
        
        # Membership Functions for Deadline Status
        deadline['none'] = fuzz.trimf(deadline_universe, [0, 0, 4])
        deadline['near'] = fuzz.trimf(deadline_universe, [2, 5, 8])
        deadline['urgent'] = fuzz.trimf(deadline_universe, [6, 10, 10])

        # Membership Functions for Mood
        mood['bad'] = fuzz.trimf(mood_universe, [0, 0, 5])
        mood['okay'] = fuzz.trimf(mood_universe, [0, 5, 10])
        mood['good'] = fuzz.trimf(mood_universe, [5, 10, 10])

        return {
            'level': level,
            'time_norm': time_norm,
            'deadline': deadline,
            'mood': mood
        }

    def _get_fuzz_mem(self, b_name: str, f_set_name: str, belief_dict: Dict[str, float]) -> float:
        """
        Computes the degree of membership for a belief value in a specific fuzzy set.
        Returns a float [0.0, 1.0].
        """
        # Scale belief value from [0.0, 1.0] to [0.0, 10.0] for the MFs
        val = belief_dict.get(b_name, 0.0) * 10 
        
        if b_name in ['physical_fatigue', 'energy_level', 'stress_level', 'mental_focus', 'mood']:
            antecedent = self.fuzzy_antecedents['level'] if b_name != 'mood' else self.fuzzy_antecedents['mood']
        elif b_name == 'time_available_norm':
            antecedent = self.fuzzy_antecedents['time_norm']
        elif b_name == 'deadline_status':
            antecedent = self.fuzzy_antecedents['deadline']
        else:
            return 0.0

        # `fuzz.interp_membership` calculates the degree of membership (µ)
        return fuzz.interp_membership(antecedent.universe, antecedent[f_set_name].mf, val)

    # ========================================================================
    # RULE DEFINITIONS (FUZZY PRECONDITIONS)
    # ========================================================================
    
    def _initialize_rules(self) -> List[Rule]:
        """Define all production rules that shape utilities using Fuzzy Activation."""
        rules = []
        
        # Local helper for cleaner rule definition lambdas
        def _mem(b_name, f_set_name, b):
            return self._get_fuzz_mem(b_name, f_set_name, b)

        # Rule 1: Deadline urgency
        rules.append(Rule(
            name="deadline_urgency",
            # FUZZY ACTIVATION: Degree to which deadline is 'near' OR 'urgent' (T-conorm / max)
            preconditions=lambda b: np.fmax(_mem('deadline_status', 'near', b), 
                                             _mem('deadline_status', 'urgent', b)),
            effects={Action.STUDY: +0.8, Action.PLAN_NEXT_STEPS: +0.3},
            weight=2.0,
            description="Urgent deadlines favor focused study (Fuzzy)"
        ))
        
        # Rule 2: High fatigue
        rules.append(Rule(
            name="high_fatigue",
            # FUZZY ACTIVATION: Degree to which fatigue is 'high'
            preconditions=lambda b: _mem('physical_fatigue', 'high', b),
            effects={Action.DEEP_REST: +0.9, Action.STUDY: -0.4},
            weight=2.0,
            description="High fatigue prioritizes recovery (Fuzzy)"
        ))
        
        # Rule 3: Low energy + short time (FUZZY AND: T-norm / min)
        rules.append(Rule(
            name="low_energy_short_time",
            preconditions=lambda b: np.fmin(
                _mem('energy_level', 'low', b),
                _mem('time_available_norm', 'short', b)
            ),
            effects={Action.DO_EASY_TASK: +0.7, Action.STUDY: -0.5},
            weight=1.5,
            description="Short windows with low energy suit easy tasks (Fuzzy)"
        ))
        
        # Rule 4: High focus + available time (FUZZY AND: T-norm / min)
        rules.append(Rule(
            name="high_focus_time",
            preconditions=lambda b: np.fmin(
                _mem('mental_focus', 'high', b),
                np.fmax(_mem('time_available_norm', 'medium', b),
                        _mem('time_available_norm', 'long', b))
            ),
            effects={Action.STUDY: +0.6},
            weight=1.5,
            description="High focus windows leverage study productivity (Fuzzy)"
        ))
        
        # Rule 5: High stress mitigation
        rules.append(Rule(
            name="stress_mitigation",
            preconditions=lambda b: _mem('stress_level', 'high', b),
            effects={Action.SHORT_BREAK: +0.5, Action.AVOID_DISTRACTIONS: +0.3, 
                    Action.RELAX_ACTIVITY: +0.4},
            weight=1.5,
            description="High stress suggests breaks and relaxation (Fuzzy)"
        ))
        
        # Rule 6: Physical exercise readiness (FUZZY AND: T-norm / min)
        rules.append(Rule(
            name="exercise_readiness",
            preconditions=lambda b: np.fmin(
                _mem('energy_level', 'high', b),
                np.fmin(
                    _mem('physical_fatigue', 'low', b),
                    _mem('time_available_norm', 'long', b)
                )
            ),
            effects={Action.GYM: +0.8},
            weight=1.3,
            description="Good energy and time enable exercise (Fuzzy)"
        ))
        
        # Rule 7: Good mood → relaxation
        rules.append(Rule(
            name="good_mood_relax",
            preconditions=lambda b: _mem('mood', 'good', b),
            effects={Action.RELAX_ACTIVITY: +0.4, Action.AVOID_DISTRACTIONS: -0.2},
            weight=1.0,
            description="Good mood supports enjoyable activities (Fuzzy)"
        ))
        
        # Rule 8: Bad mood → rest or gentle activity
        rules.append(Rule(
            name="bad_mood_care",
            # Mood uses bad/okay/good MFs; use 'bad' instead of the previous 'low'
            preconditions=lambda b: _mem('mood', 'bad', b),
            effects={Action.DEEP_REST: +0.3, Action.RELAX_ACTIVITY: +0.3, 
                    Action.STUDY: -0.3},
            weight=1.5,
            description="Low mood calls for self-care (Fuzzy)"
        ))
        
        # Rule 9: Planning when uncertain (FUZZY AND: T-norm / min)
        rules.append(Rule(
            name="planning_clarity",
            preconditions=lambda b: np.fmin(
                _mem('deadline_status', 'none', b),
                _mem('mental_focus', 'low', b)
            ),
            effects={Action.PLAN_NEXT_STEPS: +0.5},
            weight=1.0,
            description="Low clarity benefits from planning (Fuzzy)"
        ))
        
        return rules
    
    # ========================================================================
    # PERCEPTION: INPUT → BELIEFS (UNCHANGED MAPPING)
    # ========================================================================
    
    def perceive(self, user_input: Dict[str, str]) -> None:
        """Convert user inputs into internal belief representation."""
        self.beliefs.clear()
        
        # Map string inputs to numeric beliefs [0.0, 1.0]
        belief_mapping = {
            'energy_level': self._map_level,
            'stress_level': self._map_level,
            'mental_focus': self._map_level,
            'mood': self._map_mood,
            'physical_fatigue': self._map_level,
            'deadline_status': self._map_deadline,
        }
        
        # Process time_available: normalize to [0.0, 1.0] (max 120 min)
        time_val = float(user_input.get('time_available', 30))
        time_norm = min(time_val / 120.0, 1.0)
        
        for key, value in user_input.items():
            if key in belief_mapping:
                numeric = belief_mapping[key](value)
                self.beliefs[key] = Belief(
                    name=key,
                    value=value,
                    numeric_strength=numeric
                )
        
        # Add normalized time as belief
        self.beliefs['time_available_norm'] = Belief(
            name='time_available_norm',
            value=str(time_val),
            numeric_strength=time_norm
        )
    
    # NOTE: The mapping functions are kept for the string-to-numeric conversion
    # They return crisp values [0.0, 1.0], which the fuzzy system then uses.
    def _map_level(self, label: str) -> float:
        """Map 'low'/'medium'/'high' to [0.0, 1.0]."""
        mapping = {'low': 0.0, 'medium': 0.5, 'high': 1.0}
        return mapping.get(label.lower(), 0.5)
    
    def _map_mood(self, label: str) -> float:
        """Map mood labels to numeric strength."""
        mapping = {'bad': 0.0, 'okay': 0.5, 'good': 1.0}
        return mapping.get(label.lower(), 0.5)
    
    def _map_deadline(self, label: str) -> float:
        """Map deadline urgency."""
        mapping = {'none': 0.0, 'near': 0.5, 'urgent': 1.0}
        return mapping.get(label.lower(), 0.0)
    
    # ========================================================================
    # INFERENCE: FUZZY ACTIVATION → UTILITY DELTAS
    # ========================================================================
    
    def _compute_utilities(self) -> Dict[Action, UtilityScore]:
        """
        Apply all rules to compute utility for each action using Fuzzy Activation.
        U(a) = U₀(a) + Σ (Activation_r * δ_r(a))
        """
        scores = {}
        
        # Build numeric belief dict for rule evaluation (values are [0.0, 1.0])
        belief_dict = {b.name: b.numeric_strength for b in self.beliefs.values()}
        
        for action in Action:
            # Start with base utility
            total = self.base_utilities[action]
            contributions = {}
            
            # Apply each rule
            for rule in self.rules:
                try:
                    # 1. Calculate Fuzzy Activation Strength (a value in [0.0, 1.0])
                    activation_strength = rule.preconditions(belief_dict)

                    # 2. Check if the rule is significantly activated
                    if activation_strength > 0.001: 
                        # 3. Apply the effect, weighted by the activation strength
                        delta = rule.effects.get(action, 0.0) * activation_strength
                        
                        if delta != 0.0:
                            total += delta
                            contributions[rule.name] = delta
                except Exception as e:
                    # Graceful failure if rule evaluation errors
                    print(f"Error evaluating rule {rule.name}: {e}")
                    pass
            
            scores[action] = UtilityScore(
                action=action,
                base_utility=self.base_utilities[action],
                contributions=contributions,
                total_utility=total
            )
        
        return scores
    
    # ========================================================================
    # DECISION: ARGMAX WITH TIE-BREAKING (UNCHANGED)
    # ========================================================================
    

    def _resolve_decision(self, scores: Dict[Action, UtilityScore]) -> Tuple[Action, UtilityScore]:
        """
        Select action: argmax U(a) with deterministic tie-breaking.
        """
        sorted_scores = sorted(scores.values(), key=lambda s: s.total_utility, reverse=True)
        
        best = sorted_scores[0]
        
        # Check for near-tie (within ε=0.1)
        epsilon = 0.1
        contenders = [s for s in sorted_scores if abs(s.total_utility - best.total_utility) <= epsilon]
        
        if len(contenders) > 1:
            # Apply tie-breakers
            # Priority 1: Health/rest actions
            health_priority = [Action.DEEP_REST, Action.SHORT_BREAK, Action.RELAX_ACTIVITY]
            health_contenders = [s for s in contenders if s.action in health_priority]
            if health_contenders:
                best = sorted(health_contenders, key=lambda s: s.total_utility, reverse=True)[0]
                return best.action, best
            
            # Priority 2: Deadline actions
            deadline_priority = [Action.STUDY, Action.PLAN_NEXT_STEPS]
            deadline_contenders = [s for s in contenders if s.action in deadline_priority]
            if deadline_contenders:
                best = sorted(deadline_contenders, key=lambda s: s.total_utility, reverse=True)[0]
                return best.action, best
            
            # Priority 3: Avoid repeating last action
            if self.last_action:
                non_repeated = [s for s in contenders if s.action != self.last_action]
                if non_repeated:
                    best = sorted(non_repeated, key=lambda s: s.total_utility, reverse=True)[0]
        
        return best.action, best

    
    # =ITICAL SECTIONS (UNCHANGED)
    
    def _generate_explanation(self, action: Action, score: UtilityScore) -> str:
        """Generate human-readable explanation for chosen action."""
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"RECOMMENDED ACTION: {action.value.upper()}")
        lines.append(f"{'='*70}")
        
        # Base utility
        lines.append(f"\nBase utility for this action: {score.base_utility:.2f}")
        
        # Top contributing rules (sorted by absolute contribution)
        if score.contributions:
            sorted_contrib = sorted(
                score.contributions.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            lines.append("\nTop contributing factors (Weighted by Fuzzy Activation):")
            for rule_name, delta in sorted_contrib[:3]:
                rule = next((r for r in self.rules if r.name == rule_name), None)
                if rule:
                    sign = "+" if delta > 0 else ""
                    lines.append(f"  • {rule.description} ({sign}{delta:.2f})")
        else:
            lines.append("\nNo specific rules significantly triggered; base utility selected this action.")
        
        # Current beliefs (context)
        lines.append("\nYour current state:")
        for name, belief in sorted(self.beliefs.items()):
            if not name.endswith('_norm'):
                lines.append(f"  • {name.replace('_', ' ').title()}: {belief.value}")
        
        # Actionable suggestion
        suggestions = {
            Action.STUDY: "Focus on deep work; minimize distractions for 45+ minutes.",
            Action.DO_EASY_TASK: "Tackle a small, low-barrier task to build momentum.",
            Action.GYM: "Hit the gym or exercise for 30–60 minutes. Great timing!",
            Action.SHORT_BREAK: "Step away for 5–10 minutes. Stretch, hydrate, reset.",
            Action.DEEP_REST: "Prioritize sleep or deep rest. Your body needs recovery.",
            Action.RELAX_ACTIVITY: "Engage in something enjoyable: music, reading, hobby.",
            Action.AVOID_DISTRACTIONS: "Silence notifications and work in a focused space.",
            Action.PLAN_NEXT_STEPS: "Spend 10–15 minutes clarifying your next 3 priorities.",
        }
        lines.append(f"\nSuggestion: {suggestions.get(action, 'Take the recommended action.')}")
        lines.append(f"{'='*70}\n")
        
        return "\n".join(lines)
    
    # ========================================================================
    # MAIN AGENT LOOP (UNCHANGED)
    # ========================================================================
    
    def decide(self, user_input: Dict[str, str]) -> Tuple[Action, str]:
        """
        Full agent loop: perceive → reason → decide → explain.
        """
        self.iteration += 1
        
        # Perceive: normalize inputs to beliefs
        self.perceive(user_input)
        
        # Reason: compute utilities via fuzzy-activated rules
        utility_scores = self._compute_utilities()
        
        # Decide: argmax with tie-breaking
        chosen_action, score = self._resolve_decision(utility_scores)
        self.last_action = chosen_action
        
        # Explain: generate XAI narrative
        explanation = self._generate_explanation(chosen_action, score)
        
        return chosen_action, explanation
    
    # ========================================================================
    # UTILITY: DEBUG AND ANALYSIS (UNCHANGED)
    # ========================================================================
    
    def print_utility_table(self, user_input: Dict[str, str]) -> None:
        """Print detailed utility breakdown for all actions (for analysis)."""
        self.perceive(user_input)
        scores = self._compute_utilities()
        
        print(f"\n{'='*70}")
        print("UTILITY ANALYSIS TABLE (Fuzzy Activated)")
        print(f"{'='*70}")
        print(f"{'Action':<20} {'Base':<8} {'Total':<8} {'Contributing Rules':<30}")
        print("-" * 70)
        
        for action in sorted(scores.values(), key=lambda s: s.total_utility, reverse=True):
            base = f"{action.base_utility:.2f}"
            total = f"{action.total_utility:.2f}"
            if action.contributions:
                rules_str = ", ".join([f"{k}({v:+.1f})" for k, v in list(action.contributions.items())[:2]])
            else:
                rules_str = "(no rules)"
            print(f"{action.action.value:<20} {base:<8} {total:<8} {rules_str:<30}")
        print(f"{'='*70}\n")


# ============================================================================
# DEMO & INTERACTIVE LOOP (UNCHANGED)
# ============================================================================

def get_user_input() -> Dict[str, str]:
    """Prompt user for beliefs interactively."""
    print("\n" + "="*70)
    print("AMDA: AGENTIC MICRO-DECISION ADVISOR")
    print("="*70)
    print("\nEnter your current state (or press Enter for defaults):\n")
    
    defaults = {
        'energy_level': 'medium',
        'stress_level': 'low',
        'time_available': '45',
        'deadline_status': 'none',
        'mental_focus': 'medium',
        'mood': 'okay',
        'physical_fatigue': 'low',
    }
    
    result = {}
    
    prompts = [
        ('energy_level', 'Energy level (low/medium/high): '),
        ('stress_level', 'Stress level (low/medium/high): '),
        ('time_available', 'Time available (minutes): '),
        ('deadline_status', 'Deadline status (none/near/urgent): '),
        ('mental_focus', 'Mental focus (low/medium/high): '),
        ('mood', 'Mood (bad/okay/good): '),
        ('physical_fatigue', 'Physical fatigue (low/medium/high): '),
    ]
    
    for key, prompt in prompts:
        val = input(prompt).strip()
        result[key] = val if val else defaults[key]
    
    return result


def run_demo():
    """Run predefined demo scenarios."""
    agent = AMDA()
    
    scenarios = [
        {
            'name': 'Normal Productive State',
            'input': {
                'energy_level': 'high',
                'stress_level': 'low',
                'time_available': '120',
                'deadline_status': 'near',
                'mental_focus': 'high',
                'mood': 'good',
                'physical_fatigue': 'low',
            }
        },
        {
            'name': 'Health Priority: Exhausted',
            'input': {
                'energy_level': 'low',
                'stress_level': 'medium',
                'time_available': '30',
                'deadline_status': 'none',
                'mental_focus': 'low',
                'mood': 'bad',
                'physical_fatigue': 'high',
            }
        },
        {
            'name': 'Short Window: Low Energy',
            'input': {
                'energy_level': 'low',
                'stress_level': 'low',
                'time_available': '15',
                'deadline_status': 'none',
                'mental_focus': 'medium',
                'mood': 'okay',
                'physical_fatigue': 'medium',
            }
        },
        {
            'name': 'Conflict: Urgent Deadline + High Stress',
            'input': {
                'energy_level': 'medium',
                'stress_level': 'high',
                'time_available': '60',
                'deadline_status': 'urgent',
                'mental_focus': 'medium',
                'mood': 'okay',
                'physical_fatigue': 'low',
            }
        },
        {
            'name': 'Good State: Exercise Ready',
            'input': {
                'energy_level': 'high',
                'stress_level': 'low',
                'time_available': '75',
                'deadline_status': 'none',
                'mental_focus': 'high',
                'mood': 'good',
                'physical_fatigue': 'low',
            }
        },
    ]

    # Pick one scenario at random for a concise demo
    scenario = random.choice(scenarios)

    print(f"\n\n{'#'*70}")
    print(f"# SCENARIO: {scenario['name']}")
    print(f"{'#'*70}")

    action, explanation = agent.decide(scenario['input'])
    print(explanation)

    # Show utility table for the showcased scenario
    agent.print_utility_table(scenario['input'])


def run_interactive():
    """Run in interactive mode."""
    agent = AMDA()
    
    print("\n" + "="*70)
    print("AMDA: INTERACTIVE MODE")
    print("="*70)
    print("\nType 'demo' to run predefined scenarios.")
    print("Type 'quit' to exit.")
    print("Otherwise, enter your state for a recommendation.\n")
    
    while True:
        cmd = input("\nCommand (demo/input/quit): ").strip().lower()
        
        if cmd == 'quit':
            print("Goodbye!")
            break
        elif cmd == 'demo':
            run_demo()
        elif cmd == 'input':
            user_input = get_user_input()
            action, explanation = agent.decide(user_input)
            print(explanation)
        else:
            print("Unknown command. Try 'demo', 'input', or 'quit'.")


def main():
    """Entry point: choose demo or interactive mode."""
    import sys
    
    print("\n" + "="*70)
    print("AGENTIC MICRO-DECISION ADVISOR (AMDA) v1.1 (FUZZY LOGIC)")
    print("="*70)
    print("\nChoose mode:")
    print("  1. Demo (run predefined scenarios)")
    print("  2. Interactive (enter your own state)")
    print("  3. Quick demo + exit")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == '1':
        run_demo()
        run_interactive()
    elif choice == '2':
        run_interactive()
    elif choice == '3':
        run_demo()
    else:
        print("Invalid choice. Running demo...")
        run_demo()


if __name__ == '__main__':
    # Check for library presence before running
    try:
        main()
    except ImportError:
        print("\n" + "="*70)
        print("ERROR: Missing Required Libraries")
        print("The fuzzy logic implementation requires 'numpy' and 'scikit-fuzzy'.")
        print("Please install them using:")
        print("  pip install numpy scikit-fuzzy")
        print("="*70)