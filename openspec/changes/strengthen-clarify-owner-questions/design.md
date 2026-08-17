## Context

The consolidated workflow already preserves older accepted input, records unresolved product decisions, and blocks downstream stages. It does not require the agent to turn each unresolved decision into a focused owner question, so a compliant response can stop with a vague request or a passive unresolved marker.

This is a spec-governed instruction change. The question UI differs between supported agents and collaboration modes, so the contract must govern the interaction outcome without depending on one tool name.

## Goals / Non-Goals

**Goals:**

- Make clarification actively resolve rather than merely record owner decisions.
- Keep question batches focused and small enough for an owner to answer directly.
- Preserve equivalent behavior when a structured question mechanism is unavailable.
- Require explicit owner answers and complete contract reconciliation before convergence.

**Non-Goals:**

- Add a CLI command, runtime question adapter, hook, BDD scenario, or unit test.
- Ask the owner about matters current repository evidence already settles.
- Allow automatic progression, a recommendation, or a default choice to answer an unresolved product decision.

## Decisions

### Evidence precedes questions

The workflow first reconciles current specifications, accepted input, proposal and deltas, checkpoints, and repository evidence. It asks only for remaining outcome-changing owner decisions. This prevents unnecessary questions and keeps owner authority distinct from discoverable facts.

### One to three focused questions per batch

Each question identifies the exact missing decision and its meaningful consequences. When bounded alternatives exist, it presents concrete mutually exclusive choices; otherwise it asks one precise open question. A generic request such as “can you clarify?” is not a completed clarification action.

### Mechanism-independent delivery

The workflow uses the active agent's structured user-question mechanism when available. When unavailable, it asks the same focused question directly and waits. Requiring one named tool would make governance weaker in environments that do not expose that tool.

### Unresolved records do not replace interaction

`Unresolved — Do Not Assume` records why clarification is blocked and protects downstream artifacts, but the workflow must also ask the owner how to resolve each entry. After every explicit answer, it reconciles the complete agreement and repeats until no owner decision remains.

## Risks / Trade-offs

- **Over-questioning discoverable facts** → Require repository and contract reconciliation before forming a question.
- **Question batches overwhelm the owner** → Limit each batch to one through three focused questions.
- **Agent-specific question tools differ** → Govern the interaction and fallback rather than one tool name.
- **A suggested option is mistaken for confirmation** → Require an explicit owner answer; recommendations and defaults remain non-authoritative.
