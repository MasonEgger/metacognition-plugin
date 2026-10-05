# Session: Step 7, Practice Lookup in the Research Contract

## Summary

The research contract described one request, a domain survey.
The interview needs to research a deferral in the same turn, so the contract and the agent now describe a second shape, the practice lookup.
It takes one practice question plus the person's stated lean and returns up to five cited bottom lines, with a fixed no-results line.

`src/references/research-contract.md` gained a "Request Shapes" section.
It tells the two shapes apart by whether the prompt carries a domain statement.
The domain survey shape is unchanged.
The contract block in `metacognition/agents/domain-research.md` was updated to match, along with the agent description and body.
The synced copy under `metacognition/skills/design/references/` was regenerated.
The interview slice does not ship the contract until Step 8.

## Test Counts

The RED run showed 6 failed and 6 passed before the reference changed.
Editing only the reference made the equality test fail, which proved the guard covers the new text.
The suite went from 498 to 504 tests.
`uv run pytest -q` and `just check` both exit 0, and the validator verdict was clean at iteration 1 with no findings.

## Deviations from Plan

None.

## Observations

- The validator noted that the agent-development skill lists a model field as required, while this project's invariant forbids model pins.
  The invariant governs, so the agent has no `model:` line.
- For Step 8: the interview skill's research dispatch passes one practice question plus the person's stated lean and NO domain statement.
  The presence of a domain statement is what selects the survey shape.

## Files Changed

- `src/references/research-contract.md` and its synced copy under `metacognition/skills/design/references/`.
- `metacognition/agents/domain-research.md`.
- `tests/test_research_contract.py`.
- `CLAUDE.md` (one line on the two request shapes) and `todo.md`.
