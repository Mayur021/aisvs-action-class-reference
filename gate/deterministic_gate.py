"""
Deterministic Gate. Reference implementation of OWASP AISVS C9.2.6.

The gate reads a manifest at startup. For any action the agent attempts,
the gate looks up the action in the manifest and returns the declared class.
Actions not present in the manifest are refused. The class is never derived
from agent runtime output. The gate is code the agent cannot reach.

This is a minimal reference. Production deployments will plug this into a
policy engine (OPA, Cedar, Rego) and add audit logging, signing of the
manifest, replay protection, etc.
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable


class ActionClass(Enum):
    READ_ONLY = "read_only"
    REVERSIBLE = "reversible"
    EXTERNAL_REVERSIBLE = "external_reversible"
    IRREVERSIBLE = "irreversible"


CLASS_SEVERITY: Dict[ActionClass, int] = {
    ActionClass.READ_ONLY: 0,
    ActionClass.REVERSIBLE: 1,
    ActionClass.EXTERNAL_REVERSIBLE: 2,
    ActionClass.IRREVERSIBLE: 3,
}


class ActionRefused(Exception):
    """Raised when the gate refuses an action."""


class DeterministicGate:
    def __init__(self, manifest_path: str | Path) -> None:
        manifest_path = Path(manifest_path)
        with manifest_path.open("r", encoding="utf-8") as f:
            self.manifest = json.load(f)
        self.agent_id: str = self.manifest["agent_id"]
        self.manifest_version: str = self.manifest["manifest_version"]
        self._action_index: Dict[str, dict] = {
            action["name"]: action for action in self.manifest["actions"]
        }

    def declared_actions(self) -> Iterable[str]:
        return self._action_index.keys()

    def get_action_class(self, action_name: str) -> ActionClass:
        if action_name not in self._action_index:
            raise ActionRefused(
                f"Action '{action_name}' is not declared in manifest for agent "
                f"'{self.agent_id}'. The gate refuses any action not declared."
            )
        declared = self._action_index[action_name]
        return ActionClass(declared["class"])

    def evaluate(self, action_name: str) -> ActionClass:
        """Public evaluation API. Returns the action class declared in the manifest."""
        return self.get_action_class(action_name)

    def requires_approval(self, action_name: str) -> bool:
        action = self._action_index.get(action_name)
        if action is None:
            raise ActionRefused(
                f"Action '{action_name}' not declared in manifest. Refused."
            )
        if "requires_approval" in action:
            return bool(action["requires_approval"])
        cls = ActionClass(action["class"])
        return cls in (ActionClass.EXTERNAL_REVERSIBLE, ActionClass.IRREVERSIBLE)


def describe(cls: ActionClass) -> str:
    descriptions = {
        ActionClass.READ_ONLY: "Read-only. No state change. Reversible by definition.",
        ActionClass.REVERSIBLE: "State change, cleanly undoable by the agent or operator.",
        ActionClass.EXTERNAL_REVERSIBLE: "Reaches outside the system. Undo requires external coordination.",
        ActionClass.IRREVERSIBLE: "Cannot be cleanly undone after execution.",
    }
    return descriptions[cls]
