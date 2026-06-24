"""Tests for the deterministic gate (AISVS C9.2.3 and C9.2.4)."""

import sys
from pathlib import Path

import pytest

# Allow running tests from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gate import ActionClass, ActionRefused, DeterministicGate  # noqa: E402

EXAMPLES = Path(__file__).resolve().parents[1] / "schema" / "examples"


def test_calendar_agent_read_only():
    gate = DeterministicGate(EXAMPLES / "calendar-agent.json")
    assert gate.evaluate("read_calendar") == ActionClass.READ_ONLY


def test_calendar_agent_external_reversible():
    gate = DeterministicGate(EXAMPLES / "calendar-agent.json")
    assert gate.evaluate("send_invite") == ActionClass.EXTERNAL_REVERSIBLE


def test_calendar_agent_irreversible():
    gate = DeterministicGate(EXAMPLES / "calendar-agent.json")
    assert gate.evaluate("delete_event") == ActionClass.IRREVERSIBLE


def test_undeclared_action_is_refused():
    gate = DeterministicGate(EXAMPLES / "calendar-agent.json")
    with pytest.raises(ActionRefused):
        gate.evaluate("transfer_funds")


def test_log_investigator_all_read_or_reversible():
    gate = DeterministicGate(EXAMPLES / "log-investigator-agent.json")
    for action in gate.declared_actions():
        cls = gate.evaluate(action)
        assert cls in (ActionClass.READ_ONLY, ActionClass.REVERSIBLE), (
            f"Investigator agent must never declare write actions. "
            f"Found '{action}' as {cls.value}."
        )


def test_incident_responder_has_irreversible_actions():
    gate = DeterministicGate(EXAMPLES / "incident-responder-agent.json")
    assert gate.evaluate("revoke_token") == ActionClass.IRREVERSIBLE
    assert gate.evaluate("block_user") == ActionClass.IRREVERSIBLE


def test_requires_approval_default_for_irreversible():
    gate = DeterministicGate(EXAMPLES / "incident-responder-agent.json")
    assert gate.requires_approval("revoke_token") is True


def test_requires_approval_false_for_read_only():
    gate = DeterministicGate(EXAMPLES / "incident-responder-agent.json")
    assert gate.requires_approval("fetch_alert") is False
