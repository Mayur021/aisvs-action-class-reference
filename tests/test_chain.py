"""Tests for the worst-case chain rule (AISVS C9.2.10)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gate import (  # noqa: E402
    ActionClass,
    DeterministicGate,
    chain_requires_approval,
    explain_chain,
    worst_case_class,
)

EXAMPLES = Path(__file__).resolve().parents[1] / "schema" / "examples"


def calendar_gate():
    return DeterministicGate(EXAMPLES / "calendar-agent.json")


def responder_gate():
    return DeterministicGate(EXAMPLES / "incident-responder-agent.json")


def test_read_followed_by_write_is_write():
    gate = calendar_gate()
    chain = ["read_calendar", "send_invite"]
    assert worst_case_class(chain, gate) == ActionClass.EXTERNAL_REVERSIBLE


def test_chain_of_reads_stays_read_only():
    gate = calendar_gate()
    chain = ["read_calendar", "read_calendar", "read_calendar"]
    assert worst_case_class(chain, gate) == ActionClass.READ_ONLY


def test_external_reversible_followed_by_irreversible_is_irreversible():
    gate = calendar_gate()
    chain = ["send_invite", "delete_event"]
    assert worst_case_class(chain, gate) == ActionClass.IRREVERSIBLE


def test_irreversible_anywhere_in_chain_governs():
    gate = responder_gate()
    chain = ["fetch_alert", "enrich_with_threat_intel", "revoke_token"]
    assert worst_case_class(chain, gate) == ActionClass.IRREVERSIBLE


def test_chain_with_undeclared_action_raises():
    gate = calendar_gate()
    from gate.deterministic_gate import ActionRefused

    chain = ["read_calendar", "transfer_funds"]
    with pytest.raises(ActionRefused):
        worst_case_class(chain, gate)


def test_empty_chain_raises():
    gate = calendar_gate()
    with pytest.raises(ValueError):
        worst_case_class([], gate)


def test_chain_requires_approval_when_worst_is_irreversible():
    gate = responder_gate()
    chain = ["fetch_alert", "revoke_token"]
    assert chain_requires_approval(chain, gate) is True


def test_chain_does_not_require_approval_when_all_read_only():
    gate = responder_gate()
    chain = ["fetch_alert", "enrich_with_threat_intel"]
    assert chain_requires_approval(chain, gate) is False


def test_explain_chain_returns_string():
    gate = responder_gate()
    chain = ["fetch_alert", "quarantine_host", "revoke_token"]
    out = explain_chain(chain, gate)
    assert "irreversible" in out
    assert "Requires human-in-the-loop approval: yes" in out
