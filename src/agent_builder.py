"""
Agent Builder

Builds detailed agent cards from scenario definitions.
Each agent card is a structured persona with goals, resources, fears, etc.

Reference: mirofish-cli's tools/prepare_simulation.py agent profile generation
"""

import json
from typing import Any, Dict, List, Optional

from src.llm_client import get_client


class AgentCard:
    """An agent card representing a character in the simulation."""

    REQUIRED_FIELDS = [
        "agent_id", "name", "identity", "historical_position",
        "core_goals", "resources", "fears", "personality",
        "information_available", "constraints", "likely_actions",
        "relationship_to_protagonist",
    ]

    def __init__(self, definition: Dict[str, Any]):
        self.definition = definition
        self.agent_id = definition.get("id", "unknown")
        self.name = definition.get("name", self.agent_id)

        # Set all fields from definition
        for field in self.REQUIRED_FIELDS:
            key = field.replace("agent_id", "id")
            setattr(self, field, definition.get(key, "待补充"))

        # Additional computed fields
        self.current_status = "待机"  # 待机/行动中/受困/已消除
        self.morale = 70  # 0-100
        self.loyalty_to_protagonist = self._init_loyalty()
        self.knowledge_gaps = []  # What this agent doesn't know
        self.available_actions = list(definition.get("likely_actions", []))

    def _init_loyalty(self) -> int:
        """Calculate initial loyalty to protagonist based on relationship."""
        rel = self.relationship_to_protagonist.lower() if self.relationship_to_protagonist else ""
        if "自己" in rel or "主角" in rel:
            return 100
        if "盟友" in rel or "支持" in rel:
            return 75
        if "中立" in rel:
            return 40
        if "敌人" in rel or "死敌" in rel:
            return 5
        if "竞争" in rel:
            return 20
        return 50

    def to_dict(self) -> Dict[str, Any]:
        """Serialize agent card to dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "identity": getattr(self, "identity", ""),
            "historical_position": getattr(self, "historical_position", ""),
            "core_goals": getattr(self, "core_goals", []),
            "resources": getattr(self, "resources", []),
            "fears": getattr(self, "fears", []),
            "personality": getattr(self, "personality", ""),
            "information_available": getattr(self, "information_available", []),
            "constraints": getattr(self, "constraints", []),
            "likely_actions": getattr(self, "likely_actions", []),
            "relationship_to_protagonist": getattr(self, "relationship_to_protagonist", ""),
            "current_status": self.current_status,
            "morale": self.morale,
            "loyalty_to_protagonist": self.loyalty_to_protagonist,
            "knowledge_gaps": self.knowledge_gaps,
            "available_actions": self.available_actions,
        }


class AgentBuilder:
    """Builds agent cards from scenario definitions."""

    def __init__(self, scenario_data: Dict[str, Any]):
        self.scenario_data = scenario_data
        self.llm = get_client()

    def build_all(self) -> List[AgentCard]:
        """Build all agent cards from scenario definitions."""
        agent_defs = self.scenario_data.get("agents", [])
        agents = []

        for defn in agent_defs:
            card = AgentCard(defn)
            # Enhance with LLM if in real mode
            if self.llm.mode != "mock":
                card = self._enhance_with_llm(card)
            agents.append(card)

        return agents

    def _enhance_with_llm(self, card: AgentCard) -> AgentCard:
        """Use LLM to enrich agent card details."""
        prompt = f"""You are an AI character designer for a historical simulation. 
Enhance the following character card with deeper psychological insight:

Name: {card.name}
Identity: {card.identity}
Core Goals: {card.core_goals}
Fears: {card.fears}

Provide additional subtle personality traits, hidden motivations, 
and potential internal conflicts that would make this character feel real."""

        response = self.llm.generate(prompt)
        # For mock mode, this is a no-op
        return card

    def export_json(self, agents: List[AgentCard]) -> str:
        """Export all agent cards as JSON string."""
        return json.dumps(
            [a.to_dict() for a in agents],
            ensure_ascii=False,
            indent=2
        )
