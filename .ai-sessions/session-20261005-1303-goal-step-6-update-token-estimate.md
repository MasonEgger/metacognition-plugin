# Session: Step 6, update_token_estimate.py

## Summary

Added `src/scripts/update_token_estimate.py`, which recomputes a profile's `token_estimate` and rewrites that one frontmatter line when it is stale.
`--check` reports a stale profile and writes nothing.
Each path is handled on its own, and a current profile is left byte-identical.

`validate_artifacts.py` gained two shared functions, `estimate_tokens` and `split_frontmatter`.
The new script imports both, and the validator imports nothing from the script.
The three synced copies under `metacognition/skills/{interview,compile,calibrate}/scripts/` were regenerated.
The script accepts exactly what the validator's split accepts, including a file with a byte-order mark or text before the first delimiter.
The rewritten file takes default permissions, which the validator noted as immaterial.
The script joins the compile and calibrate slices in Step 10.

## Test Counts

The RED run was a collection error, because the script did not exist yet.
Validation iteration 1 raised one warn: the script decoded raw bytes while the validator reads text with universal newlines, so they disagreed on CRLF profiles and the script refused CRLF and byte-order-mark files the validator accepts.
The fix pass added six parity tests, five of which failed first, and counted through the validator's own `split_frontmatter` and `estimate_tokens`.
The suite went from 476 to 498 tests.
`uv run pytest -q` and `just check` both exit 0, and the validator verdict was clean at iteration 2.

## Deviations from Plan

- Plan said: tests first, then the script.
- Deviated: the first draft of the multi-byte arithmetic assertion was off by one (3,999 plus one character is 4,000, not 3,999); fixed the test at the GREEN run, not the code.
- Impact: none.

## Files Changed

- `src/scripts/update_token_estimate.py` and `tests/test_update_token_estimate.py` (new).
- `src/scripts/validate_artifacts.py` and its three synced copies.
- `CLAUDE.md` (one line on the new script) and `todo.md`.
