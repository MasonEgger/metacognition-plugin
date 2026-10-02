# Session Summary: Step 16, Doctrine Invariants and Skill-Version Tests

**Date**: 2026-10-01
**Duration**: about 1 hour (implement, validator, finalize)
**Conversation Turns**: not tracked
**Estimated Cost**: not tracked
**Model**: Sonnet 5.5

## Goal Context

- **Condition**: `/bpe:goal` run over plan.md, one step per dispatch
- **Mode**: step
- **Outcome**: converged for Step 16 (validator verdict clean at iteration 1)
- **Subagent dispatches**: implement, validator x1, finalize
- **Steps completed**: Step 16 of 22

## Key Actions

- Added `tests/test_doctrine_invariants.py`, the spec's Component I guard.
  It scans `metacognition/`, `src/`, `evals/`, `tests/fixtures/`, and `docs/` for the ten private tokens the spec lists, with case-sensitive substring matching.
  The only exemption is the plugin manifest, which carries the author name by design.
  It checks that no SKILL.md or agent frontmatter carries a `model:` or `disable-model-invocation:` key, and that no file in any skill directory contains `../`.
  On the real tree it scans 116 files and finds nothing.
- Added `tests/test_skill_versions.py`.
  It reads the version from the five SKILL.md frontmatters, `plugin.json`, and `marketplace.json` (`metadata.version`).
  It asserts each is present, matches the beta shape (SemVer with major 0), and that all are equal.
  All seven read 0.1.0.
  The shape pattern carries a comment that it flips to the CalVer shape at 1.0.
- Added `tests/tree_helpers.py`, the shared scoped file walker, token matcher, model-key check, and version reader.
  It is not collected as a test.
- 46 new tests; the suite is 290.
  mypy now checks 17 source files.
- No shipped file needed a fix: every earlier port step had already left the tree clean for these guards.
- The guards have teeth.
  Tests plant tokens, model keys, and `../` under `tmp_path` and assert each is reported with file, line, and token.
  The validator also built scratch trees outside the repo; the guard caught a token in an eval JSON string, a synced reference copy, a docs page, a fixture, and a script comment.
  Nothing was ever planted in the real tree.
- Test-first, as it applies to guard tests: the detection tests were written before the helper module existed (two collection errors), then the helpers, then the real-tree tests.

## Prompt Inventory

| Prompt/Command | Action Taken | Outcome |
|---|---|---|
| implement Step 16 | Detection tests first, helpers, then real-tree guards | Green, 290 tests |
| validate iter 1 | Checked fences, teeth, and scope | Clean; one info finding (duplicated litter rule) |
| finalize | Test run, sync check, summary, commit, push | See commit |

## Deviations from Plan

- Plan said: the "../" guard covers skill bodies.
- Deviated: it also covers every file under each skill directory (references/, scripts/); all clean today.
- Impact: stricter than the spec's text, matching the Invariant that each skill reaches its own files by relative path.
- Plan said: tests import helpers directly.
- Deviated: added tests/tree_helpers.py (not collected by pytest) shared by both modules; undecodable files in scope are findings, not skips.
- Impact: none on shipped files.

## Efficiency Insights

**What went well:**
- Writing detection tests against planted input under `tmp_path` gave a real RED phase for a guard that cannot fail on a clean tree.
- The validator's scratch trees outside the repo confirmed the guard's reach without touching the real tree.

**What could improve:**
- The litter rule in `tests/tree_helpers.py` is a copy of the one in `tools/sync_skills.py`, and nothing binds the two.

**Course corrections:**
- None.

## Process Improvements

- Bind the duplicated litter rule: import `LITTER_DIRS`, `LITTER_NAMES`, `LITTER_SUFFIXES`, and `is_litter` from `sync_skills` (tools/ is already on `sys.path` through `tests/conftest.py`), or add a test asserting the two definitions match.
- When a guard fails later, fix the offending file at its source in `src/` and re-sync; never loosen the guard.

## Observations

- Open item for the maintainer, and it affects Step 20: `docs/` is inside the token guard's scope, and the token list includes the name in the README credit line.
  Spec goal G8 says the docs Home page carries "the credit line", while the Invariants say the only personal references are the author fields, the license, and the README credit line.
  A Home page with the full credit line would fail this guard.
  The planned resolution, unless the maintainer rules otherwise: the credit stays in the README only and the Home page links to it.
  That changes no spec fence.

## Suggested Skills for Next Session

- `python:python`: Step 17 writes `tools/build_zips.py` and its tests.
