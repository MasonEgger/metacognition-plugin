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
The runner watches the session output for the first turn the stage asks (one open probe or one battery), checks it against the eval's assertions, then ends the session.
Nothing after that first question is answered.
Design writes nothing until its final step.
Interview writes its archive skeleton before Q01, so a session ended after Q01 leaves a valid, resumable `archive.md` in the scratch copy.

## Design

`design-first-question-smoke` runs `/metacognition:design` against an empty scratch extraction root and stops at the first scoping question.
It checks that preflight states the extraction root and the derived slug, that the first question is the domain-in-one-sentence prompt asked alone, that no research agent is dispatched yet, and that no file is written.
It needs no fixture copy beyond the empty scratch root.

`design-artifact-check-and-register-coverage` runs the whole design session against a scratch root, with the runner playing the person.
The prompt creates an empty skeleton directory under the scratch root, so no fixture is added, and names it and a folder that does not exist as the artifacts.
It checks that both paths are reported as unavailable at design time and recorded as such in the artifact plan, and that every register is targeted by at least one row of the category map.

## Interview

`interview-first-question-smoke` runs `/metacognition:interview` against a scratch directory holding only the woodworking fixture's `interview-spec.md`.
It stops at the register check and the first question, and checks that the question comes from the spec's seeds and that no Q01 entry is logged before it is asked.

`interview-resume-truncated-reconstructs-ledger` runs `/metacognition:interview --resume` against a scratch copy of `tests/fixtures/extractions/woodworking-truncated`, whose archive ends mid-question.
It checks that the Resume Procedure rebuilds the ledger and category counts from the frontmatter, reports Q07 as next, and leaves Q01 through Q06 byte for byte unchanged.

`interview-battery-once-shape-is-known` runs `/metacognition:interview --resume` against a scratch copy of `tests/fixtures/extractions/woodworking-battery`, with the runner telling the session it wants concrete questions.
It checks that the next turn is one battery of three to six closed items in one category, logged as a `[probe: battery]` entry with the items tag, counted as that many probes, and written through `scripts/archive_append.py` or its by-hand fallback.

`interview-deferral-researched-same-turn` runs the same scratch copy, with the runner deferring to standard practice.
It checks that the deferral is researched in the same turn and that either documented path passes: bottom lines with sources, ratification, and an `evidence` entry, or a one-line no-web statement and an Open research line marked `unresolved`.
It never depends on live web results.

## Compile

`compile-woodworking-scratch-profile` runs `/metacognition:compile` against a scratch copy of `tests/fixtures/extractions/woodworking` with `profile.md` and `compile-log.md` removed.
It checks the written profile against `profile-format.md`: seventeen sections in order, the fixed priority text, complete golden examples, the ledger entry kept as a tension, and a token estimate at or under the 10,000 ceiling.
It also checks that the token estimate came from `scripts/update_token_estimate.py` or its by-hand fallback, that `compile-log.md` logs each cut with its source question, and that `python3 scripts/validate_artifacts.py` exits 0 on the scratch extraction.

`compile-battery-evidence-export-open-research` runs `/metacognition:compile` against a scratch copy of `tests/fixtures/extractions/woodworking-battery`.
The battery fixture's archive is in progress, which compile refuses, so the prompt flips `status` to complete in the copy only and appends one unresolved Open research line, since the fixture's own line is resolved.
It checks that the Exports list sits under its own heading in `compile-log.md` and not in the profile body, that the ratified evidence entry compiles to the written practice with its citation, and that the unresolved line is listed in `do_not_infer`.

## Calibrate

`calibrate-round-02-fold-back` runs `/metacognition:calibrate` against a scratch copy of the full woodworking fixture, which already carries `calibration/round-01.md`.
The round's redlines come from `tests/fixtures/calibration/corrections-round-02.md` through `--corrections`, so no live chat turn is needed.
That file holds two scripted redlines, each with a reason, and is a committed fixture, never a real calibration round.
The assertions check the written `round-02.md` against the round file format, the `<!-- calibrated: round 2, ... -->` marker on the edited profile, a token estimate refreshed by `scripts/update_token_estimate.py` or its by-hand fallback, and a clean validator pass, which also proves the rounds are contiguous.

## Skillify

Four skillify evals use `--dry-run`, so they write nothing; the other stops at a question.
Each records a checksum before the run and compares it after.

`skillify-dry-run-greenfield-writes-nothing` runs the greenfield path against a scratch copy of the woodworking fixture with no `--into`.
It checks that the proposed four-file layout appears under the default target `<root>/woodworking/skill/woodworking/`, and that the whole scratch extraction is unchanged.

`skillify-dry-run-augment-writes-nothing` runs the augment path against a scratch copy of `tests/fixtures/extractions/woodworking-augment`.
This eval needs a second scratch copy, of `tests/fixtures/plugins/woodshop`, made with its own `mktemp -d`.
The harness rewrites the extraction's `target_skill` to the absolute path of that plugin copy in both `interview-spec.md` and `profile.md`, so augment mode never touches the committed fixture plugin.
It checks that the structural assessment comes first, that the proposed `SKILL.md` diff, a profile-load step plus a conflict table, is printed after it, and that the scratch skill stays byte for byte unchanged.

`skillify-augment-assessment-comes-before-the-diff` runs the augment path against the same scratch copy of `tests/fixtures/plugins/woodshop`, with the extraction's `target_skill` rewritten the same way.
It checks that a structural assessment is printed before any diff, that either verdict path passes (one line and then the diff path, or findings with the alternative layout beside keep-as-is), that a configured exemplar path that does not exist produces no message, and that the finish message recommends installing `plugin-dev` when the baseline could not be loaded.
The woodshop fixture skill is a minimal stub, so the eval does not assume which verdict the assessment reaches; the verdict paths are pinned by the two evals below.
It does not depend on whether `plugin-dev` is installed.

`skillify-augment-poor-structure-offers-a-choice` points augment mode at a scratch copy of `tests/fixtures/plugins/woodshop-sprawl` and runs without `--dry-run`, then stops at the first prompt.
It checks that the findings name the vague description, the oversized single file, and the missing references directory, that an alternative layout is presented beside keep-as-is, and that no diff, profile-load step, or conflict table appears before the person chooses.
The scratch plugin copy must be byte for byte unchanged.

`skillify-dry-run-augment-well-structured-holds` runs the augment path with `--dry-run` against a scratch copy of `tests/fixtures/plugins/woodshop-tidy`, with the extraction's `target_skill` rewritten to that copy's `joinery-review` skill.
It checks that the structural assessment comes before the diff, that the verdict is the one line saying the structure holds, that no alternative layout or choice appears, that the diff path (a profile-load step plus a conflict table) follows, and that the scratch plugin copy is byte for byte unchanged.
Either documented baseline path passes.

## Fixture Plugins

`tests/fixtures/plugins/woodshop/` is the minimal augment target.
`tests/fixtures/plugins/woodshop-sprawl/` is a second target whose one skill is badly structured on purpose: a one-line description with no trigger phrases, a single `SKILL.md` of about 1,600 words that holds everything, and no `references/` directory.
Its defects are deliberate, so nobody should fix them, and its README says the same.
`tests/fixtures/plugins/woodshop-tidy/` is the opposite: its one skill, `joinery-review`, is well structured on purpose, with a third-person description that names trigger phrases, a file of about 220 words, and one file under `references/`.
It is the target for the "structure holds" verdict, and nobody should degrade it.
