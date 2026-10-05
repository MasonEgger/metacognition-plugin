# Session: Step 12, Update the Evals

## Summary

The skills changed in Steps 8 to 11, and the evals still described the old behavior.
Skillify's augment path now returns one of two verdicts, and each verdict needs a fixture that reliably produces it.
Step 12 adds evals for the new behavior, rewords the existing ones, and adds two fixture plugins that pin the two verdicts.

## What Changed

- Evals added per stage: interview ids 3 and 4, design id 2, compile id 2, one calibrate assertion, and skillify ids 3, 4, and 5.
- Existing evals were reworded where the skills now behave differently, including an "assessment before the diff" assertion on skillify eval 2.
- `tests/fixtures/plugins/woodshop-sprawl/` is a deliberately badly structured plugin (vague description, one oversized SKILL.md, no references). The skillify augment verdict for it is "challenged".
- `tests/fixtures/plugins/woodshop-tidy/` is a deliberately well-structured plugin (skill `joinery-review`, a file of about 220 words, one references file). The augment verdict for it is "structure holds".
- Two eval files were re-serialized, a formatting-only change the validator confirmed lost nothing.
- Every new expectation was traced to the text of the skill it tests.
- `evals/README.md`, `CLAUDE.md`, and `todo.md` updated.

## Verification

- `uv run pytest -q`: 506 passed (up from 504).
- `just check` exits 0.
- The prose gate exits 0.
- The validator raised one warn at iteration 1: no skillify eval pinned the "structure holds" verdict, so goal R12 was half covered. One fix pass added woodshop-tidy and skillify eval 5. Iteration 2 was clean.

## Deviations from Plan

- Plan said: the woodshop skillify eval expects the one-line "structure holds" verdict, then the diff path.
- Deviated: the woodshop fixture skill is a 63-word stub with no trigger phrases in its description, so it would likely not hold up under the skill-development guidance. It was not edited. Eval 3 accepts either verdict path and asserts only that an assessment precedes the diff. Existing eval 2 also gained an "assessment before the diff" assertion and wording for the challenged-structure case.
- Impact: none on the gate; the evals do not assume a verdict for woodshop.
- Plan said: the compile eval runs on a scratch copy of woodworking-battery.
- Deviated: that fixture's archive is status in-progress (compile refuses it) and its only Open research line is already resolved. The eval prompt flips status to complete and appends an unresolved research line in the scratch copy only.
- Impact: fixture untouched; the validator verified a clean result on such a copy.
- Plan said: the "structure holds" verdict path would be exercised through the existing woodshop fixture.
- Deviated: that path needed its own well-structured fixture (woodshop-tidy) because the existing woodshop skill is a stub. Eval 5 uses it. Together with woodshop-sprawl, the two new fixtures pin the two verdicts.
- Impact: existing fixtures untouched; both augment verdict paths are now pinned deterministically.

## Observations

- Evals that target the original woodshop fixture accept either verdict on purpose.
- The final README wording says the woodshop-tidy skill file is about 220 words; the body alone is about 180.
