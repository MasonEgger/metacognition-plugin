# Calibrate

```text
/metacognition:calibrate [domain-slug]
```

Calibrate runs one round against the compiled profile, takes your redlines, and folds every correction back into the file.
An interview only seeds a profile.
Calibration is what earns the profile the right to be trusted.

## Arguments

- `[domain-slug]`: the extraction to calibrate. Optional, and defaults to the only extraction under the root.
- `--task <path>`: supplies the task material instead of picking from the task bank.
- `--corrections <path>`: supplies your redlines as a file instead of taking them in chat.
- `--extractions-root <dir>`: overrides the extraction root for this run.

## What It Asks of You

Calibrate picks a task, states it back to you, and then generates a probe artifact using only `profile.md`.
It never opens the archive, because the point is to test the compressed file the way a consumer skill will load it.
The artifact is labeled a probe and never ships.

You redline it, in chat or by editing the artifact and passing the file with `--corrections`.
A reason for each correction helps, and a bare "no" is accepted.
When a correction contradicts a rule already in the profile, calibrate asks you which rule wins.
It does not decide that for you.

Task sources, in order: the file you passed with `--task`, then the existing skill's `evals/` directory when the spec names a target skill, then the task bank.
The bank has five tasks in each of six families: writing, code, architecture, review, selection, and product.
When no entry fits, calibrate builds a task that produces something you can redline, exercises judgment instead of recall, and uses real material where it exists.

## What It Produces

- `<root>/<slug>/calibration/round-NN.md`. See [Calibration Round Files](../formats/calibration-round.md).
- Edits to `profile.md`, each changed line marked with `<!-- calibrated: round N, YYYY-MM-DD -->`, a restamped `version`, and an updated `<calibration_state>` section.
- The `calibrate rounds, last count` cell of the extraction README.

Calibrate sets the profile's `calibrated` field.
No other stage does.

## How Long It Takes

No source gives a duration.
Each run is exactly one round and then stops.
The number of rounds depends on how the corrections trend.
The profile is calibrated when three consecutive rounds show non-increasing correction counts and the latest round is at or under the `calibration_threshold` in the interview spec, which defaults to 3.
So three rounds is the minimum, and more are likely when corrections do not fall.

## What Done Looks Like

For one round: the round file is written, `profile.md` carries the folded-back edits, the structure check is clean, and calibrate reports the correction-count trend across rounds so far.
For the stage: `calibrated: true` in the profile.
Calibrate names `round-NN.md`, `profile.md`, and `/metacognition:skillify <slug>`, and then stops.
It never runs another round on its own.
Redlining happens in chat or through a corrections file, and there is no HTML page for it.
