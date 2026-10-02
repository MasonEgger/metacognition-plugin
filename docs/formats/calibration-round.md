# Calibration Round Files

[Calibrate](../stages/calibrate.md) runs `profile.md` against a task, hands the result to you for redlines, and folds every correction back into the file.
Each round writes one file, `<root>/<slug>/calibration/round-NN.md`.
Calibration reads `profile.md` only, never the archive, because a round tests the compressed file the way a consumer skill will load it.

## Template

```markdown
---
domain: <slug>
round: NN
date: YYYY-MM-DD
task: <id or path>
corrections: N
---
## Task
## Generated artifact (probe; never ships)
## Corrections (verbatim)
## Fold-back decisions
| # | Correction | Decision (a/b/c) | Profile edit |
```

## Frontmatter Fields

- `domain`: matches the extraction's slug.
- `round`: the zero-padded round number, contiguous from `01`.
  The structure check fails a gap or a repeat.
- `date`: the day the round ran.
- `task`: the task bank id, or the path to the supplied task material.
- `corrections`: the count of corrections you made this round, the figure the calibrated-state test tracks.

## Sections

The body has four sections, in order.

- **Task.** What was asked: the task bank entry or the constructed prompt, verbatim.
- **Generated artifact (probe; never ships).** What the profile produced, unedited.
  The heading carries the probe label, so no separate disclaimer line is needed.
- **Corrections (verbatim).** Your redlines exactly as given, in chat or through `--corrections`, with a reason per correction where you gave one.
- **Fold-back decisions.** One table row per correction: its number, the correction itself, the decision (`a`, `b`, or `c`), and the specific edit made to `profile.md`.

## The Fold-Back Decision Tree

Every correction resolves to exactly one of three decisions.
Calibrate records the decision in the Fold-back decisions table and edits `profile.md`, marking every changed line with `<!-- calibrated: round N, YYYY-MM-DD -->`.

**(a) The profile has the rule, but the generated artifact misapplied it.**
Strengthen the existing rule's wording, or add a golden example that makes the correct application concrete.
The rule is not wrong.
The profile did not state it forcefully enough to survive generation.

**(b) The profile lacks the rule entirely.**
Add a new law or refusal, citing the round that surfaced it.
This is the ordinary growth path: a gap the interview did not reach, now closed by a concrete miss.

**(c) The correction contradicts a rule already in the profile.**
Surface the conflict instead of picking a winner silently, and ask you which rule wins in this case.
The answer is encoded either as a `<tension>` entry, when both readings are valid and depend on context, or as a replacement of the losing rule.

## The Probe Rule

Every round's Generated artifact heading states that what follows is a probe and never ships, regardless of domain.
This holds even in a domain whose eventual skill is forbidden from authoring on its own.
Calibration still needs a generated artifact to redline, so the stage produces one, labeled as a probe.
The never-author boundary applies to the produced skill's own operation, not to this diagnostic step.

## Calibrated State

Each round's report states the trend across the rounds run so far.
The test that flips a profile's `calibrated` field to `true` is defined once, in the `calibrated` entry on the [profile.md](profile.md) page.

## Example

Frontmatter and the Fold-back decisions table from the synthetic woodworking fixture:

```markdown
---
domain: woodworking
round: 1
date: 2026-09-21
task: Recommend a fence-to-base attachment for a new router table jig, and justify the call.
corrections: 2
---
```

```markdown
| # | Correction | Decision (a/b/c) | Profile edit |
|---|---|---|---|
| 1 | Pocket screws on the jig read correctly, no edit needed. | a | None; confirms the existing register-dependent tension entry needs no change. |
| 2 | Recommendation stopped at a comparison instead of naming what ships. | a | Strengthened the first `domain_laws` entry's example clause to state explicitly that the butt-jointed, pinned option ships, not merely that it survives better, so a generated recommendation states a call rather than only a comparison. |
```
