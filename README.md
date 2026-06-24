# AISVS Action-Class Reference

Reference implementation for the **OWASP AISVS v1.0 action-class controls**: **C9.2.3** (reversibility classification, implemented here as a publisher-declared manifest), **C9.2.4** (runtime enforcement by class, implemented here as a deterministic gate), and **C9.2.10** (worst-case reversibility class governs across a multi-step or multi-agent chain).

These controls shipped in OWASP AISVS v1.0 (C9 Orchestration & Agentic Security): C9.2.3 reversibility classification, C9.2.4 runtime enforcement by class, and C9.2.10 worst-case across multi-step chains.

## What this repo provides

- **`schema/action-class.schema.json`**: JSON Schema for the action-class manifest declared by the agent publisher.
- **`schema/examples/`**: sample manifests covering read-only, reversible, external-reversible, and irreversible action classes.
- **`gate/deterministic_gate.py`**: minimal reference deterministic gate. Reads the manifest at startup. Refuses any action not declared in the manifest. Does not derive the class from agent runtime output.
- **`gate/worst_case_chain.py`**: reference implementation of the C9.2.10 worst-case chain rule. Given a sequence of actions, returns the worst-case action class for the entire chain.
- **`tests/`**: pytest test cases covering both rules.

## The architectural cut

Two-line summary:

1. **C9.2.3** (enforced by **C9.2.4**): The reversibility classification is trusted, implemented here as a class declared by the publisher in a manifest. The gate evaluates the action class against that manifest. The gate is code the agent cannot reach. The class is not derived from runtime model output.
2. **C9.2.10**: When an agent composes multiple actions in a chain, the worst-case action class across the chain governs the whole chain. A read followed by a write is a write. An external-reversible step followed by an irreversible step is irreversible.

Together these specify the architectural floor for the write side of agentic AI: investigation (read) is reversible and can run on capability-based autonomy, but actuation (write) must pass a deterministic gate evaluating manifest-declared classification.

## Why a reference implementation

The spec text is short on purpose. A reference implementation crystallizes the rule into runnable code, so:

- Implementers can `git clone` and adapt the gate to their policy engine (OPA, Cedar, Rego, whatever).
- Reviewers can see exactly what compliance looks like.
- Future revisions of the spec can point at this repo as a concrete example.

## Action classes (per AISVS C9.2.3)

| Class | Meaning | Example |
|---|---|---|
| `read_only` | The action only reads data. It does not change state. | `read_calendar`, `query_logs`, `fetch_document` |
| `reversible` | The action changes state, but it can be cleanly undone by the same agent or operator. | `create_draft`, `set_label`, `cache_token` |
| `external_reversible` | The action reaches outside the system. Undo is possible but requires external coordination (notification, request, manual rollback). | `send_email`, `post_to_channel`, `create_calendar_invite` |
| `irreversible` | Once executed, the action cannot be cleanly undone. | `delete_database`, `transfer_funds`, `revoke_certificate` |

## Quick start

```bash
git clone https://github.com/Mayur021/aisvs-action-class-reference.git
cd aisvs-action-class-reference
python3 -m pytest tests/
```

Then look at:

- `schema/examples/calendar-agent.json` for a realistic manifest
- `gate/deterministic_gate.py` for the gate
- `gate/worst_case_chain.py` for the chain rule

## License

CC-BY-4.0. You can use, adapt, and ship this reference implementation. Attribution appreciated.

## Citation

If you cite this work, see `CITATION.cff` for the structured citation.

## Related work

- [Action-Class Authority for AI Agents: A Verification-Side Reference](https://github.com/Mayur021/action-class-authority): Whitepaper v1.0 (June 2026). The full architectural reference this implementation operationalizes: four-class reversibility taxonomy, manifest-declared classification, worst-case chain rule, applied to DFIR / SOC workflows.
- OWASP AISVS v1.0 C9 Orchestration & Agentic Security (C9.2.3 / C9.2.4 / C9.2.10, shipped).
- OWASP SPVS V1.3.7 (companion NHI runtime decision-rights work).
- Christodorescu et al. "Agent Security is a Systems Problem" (arxiv 2605.18991) on why an LLM checking another LLM is not a trusted computing base.

## Author

Mayur Agnihotri. LinkedIn: [linkedin.com/in/mayuragnihotri](https://www.linkedin.com/in/mayuragnihotri/). GitHub: [@Mayur021](https://github.com/Mayur021).
