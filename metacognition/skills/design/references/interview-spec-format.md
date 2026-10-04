# Interview Spec Format

`interview-spec.md` is the pipeline's input artifact.
`/metacognition:design` writes it after a scoping conversation with the person; `/metacognition:interview` reads it and runs the interview against it.
Nothing downstream reopens `design`'s scoping conversation: every decision the interview needs, categories, floors, artifact locations, the forced-choice bank, lives in this one file.

This reference documents two things: the frontmatter and section shape of `interview-spec.md` itself, and, in its final section, the format of the extraction README status table, which lives alongside `interview-spec.md` in every extraction directory but is not part of the interview spec's own frontmatter or body.

## The Fenced Template

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

- `domain`: a slug, lowercase and hyphenated, matching the extraction directory name under the extraction root, `<root>/<domain-slug>/`.
- `title`: the human-readable title, used in headings and in the README status table.
- `registers`: the list of contexts the profile must cover, decided during the `Starting context` conversation per extraction theory rule 9.
  A domain with one register still carries the field as a single-item list.
- `consumer`: a plain-language statement of what the future skill must be able to do with the profile, for example "review pull requests the way the person would" or "pick a joinery approach the way the person would."
  This drives the `judgment_fingerprint` section of the eventual profile.
- `target_skill`: the augment-or-greenfield signal, in one of three forms.
  `<plugin>:<skill>` names an existing skill inside an installed plugin, the normal augment case.
  A repo-relative skill directory (for example `woodshop/skills/woodworking`) names a skill still inside this checkout that has not shipped as a standalone plugin skill reference yet.
  An absolute directory path names a skill directory outside the checkout, used directly with no further resolution; this is how an eval harness points augment mode at a scratch copy of a fixture skill, and it exists alongside the other two forms rather than replacing either.
  `null` means greenfield: no existing skill claims this domain, and skillify creates a new skill instead of proposing a diff against one.
  Design sets this field from the person's answer to "who consumes the profile"; every later stage reads it but only skillify acts on it.
- `artifacts_available`: whether the person has real artifacts (repos, past reviews, decision logs) to ground the interview against, per extraction theory rule 7.
  `false` does not skip the Artifact plan section; it records that the interview leans harder on hypotheticals and contrast probing instead.
- `calibration_threshold`: the correction count calibrate treats as acceptable for a round to count toward the calibrated state, the state `profile-format.md`'s `calibrated` frontmatter field entry defines.
  Default `3`; a domain can raise or lower it in the spec if the standard 3 does not fit, but the field must be present and explicit rather than left to calibrate's own default.
- `created`: the date design wrote the spec, `YYYY-MM-DD`.

## Section Reference

**Starting context.** The person's scoping answers, recorded verbatim per extraction theory rule 11, never summarized by design.
This is the raw material every later section derives from; if a category map decision cannot be traced back to something said here or in Research findings, it does not belong in the spec.

**Research findings.** The domain-research agent's output, folded in: confirmed dimensions, schools of thought, and the quality and failure vocabulary practitioners use, each with a source.
Design does not invent findings; it cites what the agent returned, and drops what turned out to be irrelevant to this particular person's scope.

**Unknown-unknowns surfaced.** Per extraction theory rule 13, 3 to 5 dimensions the person likely has real taste about but would not raise unprompted.
Each is marked `engaged` or `declined`: engaged means the person confirmed it belongs in the interview and it earns a category or a question seed; declined means they ruled it out of scope for this extraction, and the decision is recorded here so a later design run does not re-surface the same question without cause.

**Category map.** A table naming every category the interview will cover, the generic interview slot it feeds, one of the seven generic interview slots (Beliefs and contrarian takes, Mechanics, Aesthetic crimes, Voice and posture, Structural preferences, Hard nos, Red flags), or a sanctioned domain-specific addition (the design skill defines these), a floor (the minimum question count per extraction theory rule 10), and the saturation rule that lets interview stop asking early when three consecutive answers add no new constraint.
A category maps to one of the seven generic interview slots, never to a `profile.md` section; compile is what turns an answered category into the corresponding profile section later, and that mapping is compile's job, not design's.
The floor guarantees coverage; saturation, not the floor, decides when a category is actually done.

**Question seeds.** Grouped under a `### <Category>` heading per category in the map, each seed pairs a starting question with a named probe pattern: `forced-choice`, `ladder`, `contrast`, `artifact`, `critical-incident`, or `triad`, matching extraction theory's technique index (rule 16).
Seeds are starting points, not a script; interview follows a thread when something interesting emerges.

**Artifact plan.** Paths to every real artifact the interview will ground questions in, selection instructions when a category has more artifacts than the interview needs, and a note on how each artifact gets used (contrast pair, single grounding example, sorting set).
In augment mode, the target skill's own files come first: an existing skill built from an earlier interview is itself an artifact, per extraction theory rule 7, a stated preference captured before, now probed against what the person says today.

**Forced-choice bank.** Numbered `FC-01`, `FC-02`, and so on, each entry a pair of concrete options plus the standard probe, which, why, and what would flip your answer.
This bank exists because extraction theory rule 4 ranks forced choice over open description; design pre-builds a starting set so interview is not inventing forced-choice pairs from scratch mid-session for every category.

**Closing questions.** Every interview ends with the same three fixed closers, regardless of domain, plus any domain-specific addition design chooses to append.
The three fixed closers, asked verbatim in every interview: "What did this interview miss?", "If you could give one instruction that overrides everything else, what is it?", and "What did you learn about yourself answering this?"
The first closer is the interview's own unknown-unknowns check (rule 13) turned back on itself; the second asks the person to name the single highest-priority instruction directly, close in spirit to the keep/cut test (rule 14) but framed as one forced priority rather than a line-by-line cut; the third is a reflection question with no direct rule mapping, aimed at what answering the interview revealed to the person being interviewed.

## Extraction README Status Table

Every extraction directory carries a `README.md` whose body is a single status table, not narrative prose.
The table is the dashboard: there is no `/metacognition:status` command, because this table already answers "where is this extraction" without a separate command.

Columns, in order:

- `design`: whether the interview spec exists and its creation date.
- `interview n/floor`: questions asked so far over the sum of category floors, so a glance shows how far the interview has to go.
- `compile tokens`: the compiled profile's estimated token count, the same figure `python3 scripts/validate_artifacts.py` recomputes and checks against the 10,000-token ceiling.
- `calibrate rounds, last count`: how many calibration rounds have run, and the correction count of the most recent one, the number that has to trend down for the profile to reach the calibrated state.
- `skillify -> plugin:skill (mode)`: once skillify has run, the target skill it produced or augmented, and whether it ran in augment or replace mode.

Every pipeline skill that touches an extraction updates this table as its last action, not a separate housekeeping pass: design writes the `design` cell when it writes `interview-spec.md`, interview updates `interview n/floor` as it runs (per extraction theory rule 11's incremental-persistence discipline, the archive and the README both update as the interview happens, not at the end), and so on through skillify.
A stale table is a bug in whichever skill last touched the extraction, not an expected state.
