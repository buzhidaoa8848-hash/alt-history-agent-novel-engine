"""
World State Manager

Manages the evolving state of the simulated world.
Each simulation round produces a world state update.

The world state captures:
- Political/military variables
- Character relationships
- Information control
- Risk levels
"""

import copy
import json
from typing import Any, Dict, List, Optional


class WorldState:
    """Mutable world state that evolves through simulation rounds."""

    DEFAULT_STATE = {
        "current_year": "秦始皇三十七年（公元前210年）",
        "current_season": "七月，盛夏",
        "current_location": "上郡，秦边军大营",
        "emperor_status": "秦始皇已崩，密不发丧",
        "succession_legitimacy": 30,  # 0-100, how legitimate the succession is perceived
        "fusu_military_power": 40,  # 0-100, Fu Su's actual control over military
        "zhao_gao_information_control": 70,  # 0-100, how much Zhao Gao controls information
        "li_si_commitment_to_conspiracy": 80,  # 0-100, how committed Li Si is to the plot
        "meng_tian_loyalty": 85,  # 0-100, loyalty to Fu Su/protagonist
        "meng_tian_willingness_to_rebel": 10,  # 0-100, willingness to openly rebel
        "border_army_stability": 75,  # 0-100, how stable the border army is
        "xianyang_control": 60,  # 0-100, how much control Zhao Gao has over Xianyang
        "public_unrest": 40,  # 0-100, level of civil unrest
        "six_states_restoration_risk": 50,  # 0-100, risk of six states rebellion
        "protagonist_survival_risk": 90,  # 0-100, immediate survival risk
        "wang_li_reliability": 50,  # 0-100, Wang Li's reliability (lower = more pro-Zhao Gao)
        "meng_yi_safety": 60,  # 0-100, Meng Yi's safety in Xianyang
        "truth_about_decree": 5,  # 0-100, how much truth about the forged decree is known
        "time_pressure": 80,  # 0-100, urgency/time pressure
        "protagonist_identity_integration": 20,  # 0-100, Li Shimin's integration with Fu Su's identity
        "narrative_tension": 70,  # 0-100, narrative tension level
        "round_number": 0,
    }

    def __init__(self, initial_state: Optional[Dict[str, Any]] = None):
        self.state = copy.deepcopy(self.DEFAULT_STATE)
        if initial_state:
            self.state.update(initial_state)
        self._history: List[Dict[str, Any]] = []

    def get(self, key: str, default: Any = None) -> Any:
        """Get a world state variable."""
        return self.state.get(key, default)

    def set(self, key: str, value: Any):
        """Set a world state variable."""
        self.state[key] = value

    def update(self, updates: Dict[str, Any]):
        """Apply multiple updates at once."""
        self.state.update(updates)

    def snapshot(self) -> Dict[str, Any]:
        """Get a copy of the current state."""
        return copy.deepcopy(self.state)

    def record_round(self, round_number: int, round_data: Dict[str, Any]):
        """Record a round's state for history."""
        self._history.append({
            "round": round_number,
            "state_before": self.snapshot() if not self._history else
                           self._history[-1].get("state_after", {}),
            "events": round_data.get("events", []),
            "key_decisions": round_data.get("key_decisions", []),
            "state_after": copy.deepcopy(self.state),
        })

    def get_history(self) -> List[Dict[str, Any]]:
        """Get the full history of state changes."""
        return self._history

    def get_latest_changes(self) -> Dict[str, Any]:
        """Get the most recent state changes."""
        if not self._history:
            return {}
        return self._history[-1]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize full world state with history."""
        return {
            "current_state": self.state,
            "rounds_simulated": len(self._history),
            "change_history": [{
                "round": h["round"],
                "key_decisions": h.get("key_decisions", []),
                "events": h.get("events", []),
            } for h in self._history],
        }


def create_initial_world_state(scenario_data: Dict) -> WorldState:
    """Create world state from scenario definition."""
    ws = WorldState()

    # Apply scenario-specific initial values if present
    setting = scenario_data.get("setting", {})
    divergence = scenario_data.get("divergence_point", {})

    ws.update({
        "current_year": setting.get("year", ws.get("current_year")),
        "current_season": setting.get("season", ws.get("current_season")),
        "current_location": setting.get("location", ws.get("current_location")),
        "round_number": 0,
        "protagonist_survival_risk": 90,  # Starts at max risk
        "narrative_tension": 85,  # Life-or-death opening
    })

    return ws
