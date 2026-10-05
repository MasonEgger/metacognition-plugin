# Session: Step 10, Compile and Calibrate Read the New Archive and Use the Estimate Script

## Summary

The archive can now hold batteries, evidence entries, open research, and exports, and compile had no instructions for any of them.
Both compile and calibrate also recomputed the token estimate with an inline one-liner.
Step 10 teaches compile to read the new archive material and points both skills at `update_token_estimate.py`.
Whole-file word counts went from 2,166 to 2,465 for compile and from 1,986 to 2,068 for calibrate.

## What Changed

- `metacognition/skills/compile/SKILL.md`: compile reads batteries, evidence entries, open research, and exports.
- Meta-rules are routed to the existing `decision_rules`, `communication_laws`, and `usage` sections; no section was added.
- `compile-log.md` is defined only in the compile skill, so the Exports heading rule lives there and no reference or docs page changed.
- `metacognition/skills/calibrate/SKILL.md`: calibrate uses the script for the estimate.
- Compile writes `profile.md` with a `token_estimate` line, and the script then corrects it.
- The script prints `<path>: updated <old> -> <new>` or `<path>: current (<n>)`.
- The old one-liner is kept verbatim as the by-hand fallback and yields the same number.
- `tools/sync_skills.py` and `tests/test_sync_manifest.py`: the manifest gives compile and calibrate the script.
- The manifest tests were seen failing before the skills named the file.
- New synced copies: `metacognition/skills/compile/scripts/update_token_estimate.py` and `metacognition/skills/calibrate/scripts/update_token_estimate.py`.
- The synced file count is 41.
- `CLAUDE.md` and `todo.md` updated.

## Verification

- `uv run pytest -q`: 504 passed.
- `just check` exits 0.
- The validator verdict was clean at iteration 1 with no findings.

## Deviations from Plan

None recorded.

## Observations

- For the later docs step: running a script from inside a skill directory leaves a gitignored `__pycache__` there, which the packager excludes.
