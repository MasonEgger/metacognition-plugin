# Session: Step 5, Batteries, Closing Questions, and Section Lines

## Summary

Extended `src/scripts/archive_append.py` so one call covers everything the interview writes per turn: a probe, a battery, or a closing question, an optional saturation flip, and ledger, research, and export lines.
The SECTIONS table drives the flags, creation order, IDs, and insertion for all three sections.
A scripted short-interview round trip through `validate_artifacts.py` passes.

## Test Counts

The RED run showed 27 failed and 45 passed before the script was extended.
The suite went from 437 to 476 tests.
`uv run pytest -q` and `just check` both exit 0.

## Deviations from Plan

- Plan said: RED for the unit tests, then Document, GREEN, then a separate RED for the integration test.
- Deviated: the scripted-interview round-trip test was written with the first RED batch, so one failing run covered both (27 failed, 45 passed).
- Impact: none; the round trip passed once the script was extended.
- Plan said: the Step 4 test that refuses --probe battery stays.
- Deviated: it became a test that a battery without --items is refused, since batteries are now supported.
- Impact: the only revised existing assertion.

## Observations

Step 8 (the interview skill rewrite) must account for these.
The same six points are in CLAUDE.md.

1. The section-line contract: the caller passes everything after the ID, starting with "(", for example `--research "(Q73): <text>. Status: unresolved"`, `--export "(Q92): <topic> -> <destination>"`, `--ledger '(Q07 vs Q23): "A" vs "B". Resolution: <text>'`. The script supplies the `- L01 `, `- R01 `, or `- E01 ` prefix.
2. A section line cannot be added without logging an entry in the same call.
3. The script never edits an existing line, so marking an Open research line "resolved in Qnn" is a by-hand edit the skill must describe.
4. `--closing` replaces `--category`, and is refused together with `--category`, `--saturated`, or a battery.
5. A battery's question is a stem line plus items numbered `1.` through `n.`, and its answer is lines numbered `1.` through `n.`; `1)` is refused.
6. A line break in a non-battery question or answer is refused, so the skill must say what the interviewer does with an answer given in several lines.

## Info Finding From Validation

The append script can only add section lines, never edit one, so an Open research line's "Status: unresolved" can never be flipped by the script.
This is consistent with the append-only rule in spec Component K.
