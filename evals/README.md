# Metacognition Pipeline Evals

One `evals.json` per stage lives beside this file: `design/`, `interview/`, `compile/`, `calibrate/`, and `skillify/`.
This README is the single place that explains how to run them.
Evals sit at the top level of the repo and never ship inside a skill bundle.

Running an eval against a live model is a manual check, not a gate.
The only automated check is `tests/test_evals.py`, which confirms every `evals.json` parses and every `tests/fixtures/` path an eval names exists.

## File Format

Each `evals.json` holds a `skill_name` and a list of `evals`.
Each eval carries an `id`, an `eval_name`, a `prompt`, an `expected_output`, a `files` list, and a list of `assertions`.
The `prompt` is what a runner hands to the model.
The `assertions` are what a reader checks afterward.
Every path in a prompt is relative to the repo root.

## Why A Scratch Copy

Every pipeline stage writes into the extraction it is pointed at: `profile.md`, `archive.md`, `calibration/round-NN.md`, and the extraction README's status cells.
Running an eval straight against `tests/fixtures/extractions/woodworking/` would change a committed fixture on every run, and a later run would see a fixture an earlier run had already altered.
The `--extractions-root` flag every pipeline stage accepts exists for this: point it at a throwaway copy and the committed fixture never moves.

## The Procedure

1. Make a scratch directory: `SCRATCH=$(mktemp -d)`.
2. Copy the extraction fixture into it, keeping the slug as the copy's directory name: `cp -r tests/fixtures/extractions/<slug> "$SCRATCH/<slug>"`.
   `--extractions-root` resolves against the directory that holds the slug directory, never the slug directory itself, so `$SCRATCH` is the value passed to the flag, not `$SCRATCH/<slug>`.
3. When an eval needs a file absent (compile's profile, for example), remove it from the scratch copy only, after the copy step, never from the fixture.
4. Run the stage under test with `--extractions-root "$SCRATCH"` and any other flags the eval needs.
5. After the run, confirm the committed fixtures are untouched: `git status --short tests/fixtures/` must print nothing.

Every eval ends its assertions with that last check.
A scratch-copy eval that fails it has a harness bug, not a skill bug, and the bug should be fixed before the other assertions are trusted.

## Running Against A Scratch Install

Evals are not part of the plugin, so a runner needs both pieces side by side.
Install the plugin in a scratch Claude Code session, or load the five skill folders into a scratch conversation, then open that session from the repo root so the relative fixture paths in each prompt resolve.
Start each skill with its slash command, for example `/metacognition:compile woodworking --extractions-root "$SCRATCH"`.
For the closing self-check, the skill runs `python3 scripts/validate_artifacts.py` from its own directory against the scratch extraction, the same way it does in real use.

## Stop At The First Question

The design and interview smoke evals watch only the first question, since no human interview happens in an eval run.
The runner watches the session output for the first question the stage asks, checks it against the eval's assertions, then ends the session.
Nothing after that first question is answered.
Design writes nothing until its final step.
Interview writes its archive skeleton before Q01, so a session ended after Q01 leaves a valid, resumable `archive.md` in the scratch copy.

## Design

`design-first-question-smoke` runs `/metacognition:design` against an empty scratch extraction root and stops at the first scoping question.
It checks that preflight states the extraction root and the derived slug, that the first question is the domain-in-one-sentence prompt asked alone, that no research agent is dispatched yet, and that no file is written.
It needs no fixture copy beyond the empty scratch root.

## Interview

`interview-first-question-smoke` runs `/metacognition:interview` against a scratch directory holding only the woodworking fixture's `interview-spec.md`.
It stops at the register check and the first question, and checks that the question comes from the spec's seeds and that no Q01 entry is logged before it is asked.

`interview-resume-truncated-reconstructs-ledger` runs `/metacognition:interview --resume` against a scratch copy of `tests/fixtures/extractions/woodworking-truncated`, whose archive ends mid-question.
It checks that the Resume Procedure rebuilds the ledger and category counts from the frontmatter, reports Q07 as next, and leaves Q01 through Q06 byte for byte unchanged.

## Compile

`compile-woodworking-scratch-profile` runs `/metacognition:compile` against a scratch copy of `tests/fixtures/extractions/woodworking` with `profile.md` and `compile-log.md` removed.
It checks the written profile against `profile-format.md`: seventeen sections in order, the fixed priority text, complete golden examples, the ledger entry kept as a tension, and a token estimate at or under the 10,000 ceiling.
It also checks that `compile-log.md` logs each cut with its source question, and that `python3 scripts/validate_artifacts.py` exits 0 on the scratch extraction.

## Calibrate

`calibrate-round-02-fold-back` runs `/metacognition:calibrate` against a scratch copy of the full woodworking fixture, which already carries `calibration/round-01.md`.
The round's redlines come from `tests/fixtures/calibration/corrections-round-02.md` through `--corrections`, so no live chat turn is needed.
That file holds two scripted redlines, each with a reason, and is a committed fixture, never a real calibration round.
The assertions check the written `round-02.md` against the round file format, the `<!-- calibrated: round 2, ... -->` marker on the edited profile, and a clean validator pass, which also proves the rounds are contiguous.

## Skillify

Both skillify evals use `--dry-run`, so neither writes anything.
Each records a checksum before the run and compares it after.

`skillify-dry-run-greenfield-writes-nothing` runs the greenfield path against a scratch copy of the woodworking fixture with no `--into`.
It checks that the proposed four-file layout appears under the default target `<root>/woodworking/skill/woodworking/`, and that the whole scratch extraction is unchanged.

`skillify-dry-run-augment-writes-nothing` runs the augment path against a scratch copy of `tests/fixtures/extractions/woodworking-augment`.
This eval needs a second scratch copy, of `tests/fixtures/plugins/woodshop`, made with its own `mktemp -d`.
The harness rewrites the extraction's `target_skill` to the absolute path of that plugin copy in both `interview-spec.md` and `profile.md`, so augment mode never touches the committed fixture plugin.
It checks that the proposed `SKILL.md` diff, a profile-load step plus a conflict table, is printed while the scratch skill stays byte for byte unchanged.
