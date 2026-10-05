# Session Summary: archive_append.py for a Single Entry

**Date**: 2026-10-05
**Duration**: not measured
**Conversation Turns**: 4 executor dispatches (implement, validate, fix, finalize)
**Estimated Cost**: not measured
**Model**: not recorded

## Key Actions

- Wrote `src/scripts/archive_append.py`, which appends one single-probe entry to an extraction's `archive.md` and updates every counter in one call.
- The script assigns the next `Qnn`, appends the heading and the two-line body, raises `questions_asked` and the category's `asked`, and recomputes the README interview cell.
- The README cell is recomputed from the archive's category counts, not incremented.
- Writes go through temporary files and rename, and both temporaries are written before either rename.
- Wrote `tests/test_archive_append.py`, including a validator round trip, three appends in a row, and a subprocess run from another directory.
- The iteration 1 validator pass raised four warns, all fixed in one pass.
- Literal dash and curly-quote codepoints in the script and the tests became `\u` escapes.
- A line break inside a question or answer is now refused with exit 2, because it broke the two-line entry body.
- A write-phase OSError now exits 2 with one line, and the archive can no longer end up ahead of the README.
- Iteration 2 came back clean.
- Added a CLAUDE.md note and checked off Step 4 in `todo.md`.
- The script lives in `src/scripts/` only. It joins the interview slice in Step 8.

## Prompt Inventory

| Prompt/Command | Action Taken | Outcome |
|---|---|---|
| Mode: implement | Wrote tests first, then the script and CLI | RED run was a collection error before the script existed; then green |
| Mode: validate (iter 1) | Checked the diff against the spec fences and prose | Four warns, one info |
| Mode: fix | Fixed the four warns | Added 7 tests that failed first |
| Mode: validate (iter 2) | Re-checked | Clean |
| Mode: finalize | Final test pass, `just check`, summary, one signed commit, push | Step 4 committed |

## Deviations from Plan

- Plan said: GREEN, then RED integration tests, then CLI wiring, then REFACTOR as separate passes.
- Deviated: wrote the integration tests in the first test file and wrote the script once in its final shape (three pure functions plus one disk function, with the CLI entry point). The RED run was a collection error (`1 error in 0.21s`, ModuleNotFoundError) before the script existed.
- Impact: none on behavior; all 25 tests passed on the first green run.
- Plan said: probe types as in the archive format. Deviated: no allowlist, since the format reference does not close the list and the plan calls the default "open"; only brackets, newlines, and battery are refused.

## Efficiency Insights

**What went well:**
- The suite went from 404 to 437 tests; the 7 tests added in the fix pass each failed before the fix.
- Writing both temporaries before either rename keeps the archive and README from disagreeing after a failed write.

**What could improve:**
- The prose gate did not flag literal dash and quote codepoints inside the new .py files; the validator did.
- The first version relied on a validator round trip to prove entries were well formed, and the validator does not check the two-line body.

**Course corrections:**
- The fix pass described above.

## Process Improvements

- Search for the literal dash and quote codepoints in any script that handles those characters, since the prose gate skips them.
- A writer must enforce every format rule itself, not lean on the validator.

## Observations

- A multi-line answer is refused, so the interview skill text in Step 8 must say what the interviewer does when an answer arrives in several lines.
- The script accepts any probe type except battery; the archive format does not close the list.
- Step 5 adds batteries, closing questions, and section lines.

## Suggested Skills for Next Session

- `python:python`: Step 5 extends the same script.
