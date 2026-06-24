"""
Worst-Case Chain Rule. Reference implementation of OWASP AISVS C9.2.10.

When an agent composes multiple actions in a chain, the worst-case action
class across the chain governs the whole chain. A read followed by a write
is a write. An external-reversible step followed by an irreversible step
is irreversible. The gate evaluates the chain against the worst-case class,
not against the average or the most-recent class.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence

from .deterministic_gate import ActionClass, CLASS_SEVERITY, DeterministicGate


def worst_case_class(action_names: Sequence[str], gate: DeterministicGate) -> ActionClass:
    """Return the worst-case action class across a chain of actions."""
    if not action_names:
        raise ValueError("Cannot evaluate an empty action chain.")
    classes: List[ActionClass] = [gate.evaluate(name) for name in action_names]
    return max(classes, key=lambda c: CLASS_SEVERITY[c])


def chain_requires_approval(action_names: Sequence[str], gate: DeterministicGate) -> bool:
    """The chain requires approval if its worst-case class is external_reversible or irreversible."""
    worst = worst_case_class(action_names, gate)
    return worst in (ActionClass.EXTERNAL_REVERSIBLE, ActionClass.IRREVERSIBLE)


def explain_chain(action_names: Sequence[str], gate: DeterministicGate) -> str:
    """Produce a human-readable explanation of the chain evaluation."""
    if not action_names:
        return "Empty chain. Nothing to evaluate."
    lines = []
    for name in action_names:
        cls = gate.evaluate(name)
        lines.append(f"  {name}: {cls.value}")
    worst = worst_case_class(action_names, gate)
    out = "Chain actions and declared classes:\n" + "\n".join(lines)
    out += f"\n\nWorst-case class for entire chain: {worst.value}"
    out += "\nRequires human-in-the-loop approval: " + (
        "yes" if chain_requires_approval(action_names, gate) else "no"
    )
    return out
