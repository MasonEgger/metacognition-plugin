# interview-spec.md

`interview-spec.md` is the pipeline's input artifact.
[Design](../stages/design.md) writes it after a scoping conversation with you.
[Interview](../stages/interview.md) reads it and runs the interview against it.
Nothing downstream reopens design's scoping conversation.
Every decision the interview needs lives in this one file: categories, floors, artifact locations, and the forced-choice bank.

## Template

```markdown
---
domain: <slug>
title: <human title>
registers: [<register>, ...]
consumer: <what the future skill must do with this>
target_skill: <plugin>:<skill> | <repo-relative skill dir> | null   # null means greenfield
artifacts_available: true|false
calibration_threshold: 3
created: YYYY-MM-DD
---

# Interview spec: <title>

## Starting context
[The person's scoping answers, verbatim]

## Research findings
[Confirmed dimensions, schools, quality/failure vocabulary, with sources]

## Unknown-unknowns surfaced
[3-5, each marked engaged/declined]

## Category map
| Category | Maps to generic slot | Floor | Saturation rule |

## Question seeds
### <Category>
- Seed: <question>  Probe: <forced-choice|ladder|contrast|artifact|critical-incident|triad>

## Artifact plan
[paths, selection instructions, how each artifact is used; in augment mode the target skill's files come first]

## Forced-choice bank
### FC-01
Option A: ...
Option B: ...
Probe: which, why, and what would flip your answer

## Closing questions
[the three fixed closers plus any domain-specific]
```

## Frontmatter Fields

- `domain`: a slug, lowercase and hyphenated, matching the extraction directory name under the extraction root.
- `title`: the human-readable title, used in headings and in the README status table.
- `registers`: the list of contexts the profile must cover, decided during the scoping conversation per [rule 9](../method.md#9-register-separation).
  A domain with one register still carries the field as a single-item list.
- `consumer`: a plain-language statement of what the future skill must be able to do with the profile, for example "review pull requests the way the person would" or "pick a joinery approach the way the person would."
  This drives the `judgment_fingerprint` section of the eventual profile.
- `target_skill`: the augment-or-greenfield signal, in one of three forms.
  `<plugin>:<skill>` names an existing skill inside an installed plugin, the normal augment case.
  A repo-relative skill directory (for example `woodshop/skills/woodworking`) names a skill still inside this checkout.
  An absolute directory path names a skill directory outside the checkout and is used directly with no further resolution.
  `null` means greenfield: no existing skill claims this domain, and skillify creates a new skill instead of proposing a diff against one.
  Design sets this field from your answer to "who consumes the profile."
  Every later stage reads it, but only skillify acts on it.
- `artifacts_available`: whether you have real artifacts (repositories, past reviews, decision logs) to ground the interview against, per [rule 7](../method.md#7-artifact-grounding).
  `false` does not skip the Artifact plan section.
  It records that the interview leans harder on hypotheticals and contrast probing instead.
- `calibration_threshold`: the correction count calibrate treats as acceptable for a round to count toward the calibrated state, which the [profile.md](profile.md) page defines.
  The default is `3`.
  A domain can raise or lower it in the spec, but the field must be present and explicit.
- `created`: the date design wrote the spec, `YYYY-MM-DD`.

## Section Reference

**Starting context.**
Your scoping answers, recorded verbatim per [rule 11](../method.md#11-verbatim-capture) and never summarized by design.
This is the raw material every later section derives from.
If a category map decision cannot be traced back to something said here or in Research findings, it does not belong in the spec.

**Research findings.**
The research output, folded in: confirmed dimensions, schools of thought, and the quality and failure vocabulary practitioners use, each with a source.
Design does not invent findings.
It cites what the research returned, and drops what turned out to be irrelevant to your scope.

**Unknown-unknowns surfaced.**
Per [rule 13](../method.md#13-unknown-unknowns-pass), 3 to 5 dimensions you likely have real taste about but would not raise unprompted.
Each is marked `engaged` or `declined`.
Engaged means you confirmed it belongs in the interview, and it earns a category or a question seed.
Declined means you ruled it out of scope for this extraction, and the decision is recorded so a later design run does not re-surface the same question without cause.

**Category map.**
A table naming every category the interview will cover, the generic interview slot it feeds, a floor, and the saturation rule.
The generic slots are the seven below, or a sanctioned domain-specific addition:

| Generic slot | Default floor |
|---|---|
| Beliefs and contrarian takes | 10 |
| Mechanics | 15 |
| Aesthetic crimes | 12 |
| Voice and posture | 10 |
| Structural preferences | 10 |
| Hard nos | 8 |
| Red flags | 8 |

A domain may rename a slot or add slots, but every one of the seven must map to something in the final table.
A category maps to a generic interview slot, never to a `profile.md` section.
Compile turns an answered category into the matching profile section later.
The floor is the minimum question count per [rule 10](../method.md#10-saturation-not-quotas), and the saturation rule lets interview stop asking early when three consecutive answers add no new constraint.

**Question seeds.**
Grouped under a `### <Category>` heading per category in the map.
Each seed pairs a starting question with a named probe pattern: `forced-choice`, `ladder`, `contrast`, `artifact`, `critical-incident`, or `triad`.
These match the technique index in [rule 16](../method.md#16-elicitation-technique-index).
Seeds are starting points, not a script.
Interview follows a thread when something interesting emerges.

**Artifact plan.**
Paths to every real artifact the interview will ground questions in, selection instructions when a category has more artifacts than the interview needs, and a note on how each artifact gets used: a contrast pair, a single grounding example, or a sorting set.
In augment mode, the target skill's own files come first.

**Forced-choice bank.**
Numbered `FC-01`, `FC-02`, and so on.
Each entry is a pair of concrete options plus the standard probe: which, why, and what would flip your answer.
The bank exists because [rule 4](../method.md#4-forced-choice-beats-open-description) ranks forced choice over open description.

**Closing questions.**
Every interview ends with the same three fixed closers, asked verbatim, plus any domain-specific addition design chooses to append:

1. "What did this interview miss?"
2. "If you could give one instruction that overrides everything else, what is it?"
3. "What did you learn about yourself answering this?"

## Extraction README Status Table

Every extraction directory carries a `README.md` whose body is a single status table, not narrative prose.
There is no `/metacognition:status` command, because this table already answers "where is this extraction."

The columns, in order:

- `design`: whether the interview spec exists and its creation date.
- `interview n/floor`: questions asked so far over the sum of category floors.
- `compile tokens`: the compiled profile's estimated token count, the figure the structure check recomputes and checks against the 10,000-token ceiling.
- `calibrate rounds, last count`: how many calibration rounds have run, and the correction count of the most recent one.
- `skillify -> plugin:skill (mode)`: once skillify has run, the target skill it produced or augmented, and whether it ran in augment or replace mode.

Every stage that touches an extraction updates this table as its last action.
Interview updates its cell as the interview happens, not at the end.
A stale table is a bug in whichever stage last touched the extraction.

Excerpt from the synthetic woodworking fixture:

```markdown
| design | interview n/floor | compile tokens | calibrate rounds, last count | skillify -> plugin:skill (mode) |
|---|---|---|---|---|
| 2026-09-21 | 7/9 | 1860 | 1 round, last 2 | |
```
