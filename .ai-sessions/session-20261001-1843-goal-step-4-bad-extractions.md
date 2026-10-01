# Session Summary: Goal Step 4 Port the Bad-Extraction Cases

**Date**: 2026-10-01
**Duration**: short, one finalize dispatch after implement and one fix pass
**Conversation Turns**: 1
**Estimated Cost**: not measured
**Model**: Sonnet 5.5

## Key Actions

- Ported 31 files under `tests/fixtures/extractions-bad/` from the private source at 2806854, read through git only.
- The five cases are `bad-yaml`, `missing-section`, `noncontiguous-rounds`, `numbering-gap`, and `oversize-profile`.
- Each case is byte-faithful except two port-rule edits.
- README.md lost the trailing "sync date" column (port rule 7).
- In profile.md, line 25 "preserve Mason's deeper judgment over surface style." became "preserve the person's deeper judgment over surface style." (rules 3 and 5).
- The `token_estimate` frontmatter is unchanged, and each case's single deliberate defect is intact.
- Corrected a miss in Step 3 (commit a151e2a).
  Step 3 ported the three good extraction READMEs with the "sync date" column still present, because it only checked the top-level `extractions/README.md`, which has no table.
  Step 3's port was therefore not complete against rule 7.
- The Step 4 implement pass noticed the mismatch and a grep confirmed it.
  A fix pass then dropped the column from `woodworking`, `woodworking-augment`, and `woodworking-truncated`, so the good and bad tables match.
- After the fix, `grep -rn -i sync tests/fixtures` prints nothing, and the doctrine token grep over `tests/fixtures` prints nothing.
- Checked off Step 4 in `todo.md`.
- Final test run through the exit-5-tolerant wrapper returned 0 (no tests collected yet).
- CLAUDE.md needed no edit; nothing in it became false.

## Prompt Inventory

| Prompt/Command | Action Taken | Outcome |
|---|---|---|
| Mode: finalize for Step 4 | Ran tests, wrote summary and lesson, committed, pushed | One signed commit on `port-from-private-main` |

## Efficiency Insights

**What went well:**
- The implement pass caught the Step 3 gap by comparing the new bad READMEs against the good ones.

**What could improve:**
- Step 3 checked one README when the rule targeted every extraction README.
- This section declares Tools: none, so no validator pass was there to catch it.

**Course corrections:**
- A fix pass edited three Step 3 files inside Step 4's commit.

## Process Improvements

- When a port rule names a kind of file, grep the whole ported tree for that target before finalizing.

## Observations

- The private source was read only through git; no file in it was modified.
- Its filesystem path is not recorded in this repo.

## Suggested Skills for Next Session

- `python:python`: Section 3 starts the YAML subset parser, built test-first.
