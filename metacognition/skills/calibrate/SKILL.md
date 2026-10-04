---
name: calibrate
version: 0.1.1
description: 'This skill should be used when the user asks to "run a calibration round for a domain", "calibrate the profile for a domain", "run calibration against profile.md", "test the compiled profile", "redline this probe artifact", or runs `/metacognition:calibrate`. Runs a probe task against a compiled `profile.md`, takes the person''s redlines, and folds each correction back into the profile per the fold-back decision tree. It never touches the archive and never authors anything that ships.'
compatibility: 'Runs on Claude Code, Cowork, and claude.ai. The scripts need code execution and Python 3.11 or newer; without them the skill applies the same rules by hand. It reads profile.md and interview-spec.md and writes round files and profile edits in the same extraction directory, so it needs file access or the files uploaded to the conversation.'
---

# Calibrate

Run a round against a compiled `profile.md`, hand the result to the person for redlines, and fold every correction back into the file.
Calibrate is the correction loop.
It is mandatory, not optional: per extraction theory rule 15, an interview only seeds a profile; calibration is what earns the profile the right to be trusted.
Calibration is the moat: a profile nobody has redlined against a real task is a guess dressed as a rule.

## Arguments

- `[domain-slug]`: optional. The extraction to calibrate; see Preflight for how it defaults.
- `--task <path>`: optionally supplies the task material directly instead of picking from the bank.
- `--corrections <path>`: optionally supplies the redlines as a file instead of taking them in chat.
- `--extractions-root <dir>`: optionally overrides the extraction root.

## Read First

Read `references/extraction-theory.md` rule 15 before running a round: it states why this stage exists at all.

Then read `references/calibration-protocol.md` in full.
It is the single source for the task bank, the guidance for constructing a domain-specific task when the bank does not fit, the fold-back decision tree, and the round file format.
This skill does not restate any of it, only applies it.

Then read `references/profile-format.md`'s `calibrated` frontmatter field entry.
It is the single source for the calibrated-state test; this skill does not restate the test's wording, only applies it and reports against it.

## Preflight

1. Read the arguments: `[domain-slug]` is optional; `--task <path>` optionally supplies the task material directly instead of picking from the bank; `--corrections <path>` optionally supplies the person's redlines as a file instead of taking them in chat; `--extractions-root <dir>` optionally overrides the default root.
2. Resolve settings and the extraction root.
Run `python3 scripts/resolve_config.py`, passing `--extractions-root <dir>` when that flag was given and `--set key=value` for any setting the person stated in the conversation or in Project instructions.
Read the JSON it prints, relay any `Loaded config from: <path>` line it printed, and state the root in one line: "Extraction root: `<path>`".
When the script cannot run (no code execution, or an interpreter older than Python 3.11), apply the same tiers by hand from `references/settings.md`, and say so in one line.
3. Resolve the slug: if `[domain-slug]` was passed, use it directly; if it was omitted, use the only extraction under the root and error if there are zero or several, naming each candidate slug in the error so the person can retry with one named.
4. Load `<extractions-root>/<slug>/profile.md`.
Missing means there is nothing to calibrate yet; stop and name `/metacognition:compile <domain-slug>` as the prerequisite.
Never fall back to the archive when the profile is missing; the archive is not a substitute input for this skill under any condition.
5. Load `<extractions-root>/<slug>/interview-spec.md` for `calibration_threshold` (per `references/profile-format.md`'s `calibrated` frontmatter field entry, the single source for what this field means) and for `target_skill`.
6. Determine the next round number: the highest existing `calibration/round-NN.md` plus one, or `01` when no round has run yet.
Round numbers must stay contiguous; `scripts/validate_artifacts.py` checks this.

## The Per-Round Procedure

### 1. Read the Profile, Never the Archive

Load `profile.md` and apply it exactly the way the eventual consumer skill would: as the only source of the person's judgment for this round.
The point of a round is to test the compressed file the way a real consumer will load it, not to re-derive an answer from the fuller archive.
Calibrate never opens `archive.md`.

### 2. Pick or Accept a Task

When `--task <path>` was passed, use the supplied material as the task and skip the bank.
Otherwise, when `target_skill` is set in `interview-spec.md`, treat that skill's `evals/` directory as a candidate source of tasks before falling back to the bank.
Otherwise, pick a task from `references/calibration-protocol.md`'s bank for the domain family, filling in real material (a real diff, a real draft, a real backlog) rather than inventing a toy example.
When no bank entry fits, construct a domain-specific task per the three requirements `references/calibration-protocol.md` names: it produces an artifact the person can redline, it exercises judgment rather than recall, and it draws on real material where real material exists.
State the chosen task back to the person before generating anything, so a bad task pick is caught before the round is spent.

### 3. Generate the Probe Artifact

Apply `profile.md` silently and generate the artifact the task calls for, with no meta-commentary about what the profile says or why a choice was made.
Head the generated section with a round header stating plainly that what follows is a probe and never ships, regardless of domain, per `references/calibration-protocol.md`'s Probe Rule.
This holds even in a domain whose eventual skill is forbidden from authoring on its own: the never-author boundary applies to the produced skill's own operation, not to this diagnostic step, so a probe still gets generated here, labeled as one.

### 4. Take the Person's Redlines

When `--corrections <path>` was passed, read the file: either the generated artifact the person edited directly, or a list of corrections, and treat its content as the round's redlines without asking in chat.
Otherwise, take redlines freeform or inline in chat.
Encourage a why per correction, since the why is what step 5 needs to fold back correctly, and accept a bare "no" on any line, following up with one clarifying question rather than guessing the reason.

### 5. Fold Back Per the Decision Tree

For every correction, apply `references/calibration-protocol.md`'s fold-back decision tree:

- **(a)** the profile has the rule but the artifact misapplied it: strengthen the wording or add a golden example.
- **(b)** the profile lacks the rule entirely: add a new law or refusal, citing this round.
- **(c)** the correction contradicts a rule already in the profile: surface the conflict, ask the person which rule wins, and encode the answer as a `<tension>` entry or a replacement of the losing rule, per their answer.

Calibrate never resolves a (c) conflict on its own; the question always goes to the person.
Edit `profile.md` directly for every fold-back, marking each changed line with `<!-- calibrated: round N, YYYY-MM-DD -->`, and restamp the frontmatter `version` since a fold-back materially changes the file.

### 6. Write the Round File

Write `<extractions-root>/<slug>/calibration/round-NN.md` per `references/calibration-protocol.md`'s round file format: frontmatter (`domain`, `round`, `date`, `task`, `corrections`), then the four fixed sections, Task, Generated artifact (probe; never ships), Corrections (verbatim), Fold-back decisions, with one table row per correction.

### 7. Report the Trend and Update the Profile's Calibration State

Update `profile.md`'s `<calibration_state>` section: increment `<rounds>`, set `<last_date>` to today, and set `<last_correction_count>` to this round's correction count.
The calibrated-state test itself, when the field flips from `false` to `true`, is the one defined in `references/profile-format.md`'s `calibrated` frontmatter field entry; apply that test exactly and set the frontmatter `calibrated` field accordingly, without restating the test's wording here.
Report the correction-count trend across every round run so far, and whether this round moved the profile closer to or further from the calibrated state.
Update the extraction README's `calibrate rounds, last count` cell with the same figures, per `references/interview-spec-format.md`'s standing rule that every pipeline stage updates the table as its last action.

### Closing Self-Check

After `round-NN.md` is written and `profile.md`'s fold-back edits and `<calibration_state>` are both in place, run `python3 scripts/validate_artifacts.py <extractions-root>/<slug>` against the extraction and resolve every finding it reports before telling the person the round is done.
A finding here means this round's edits broke the structural contract downstream stages assume, a round-numbering gap, a stale `token_estimate`, a golden example a fold-back left incomplete; fix it now, while this session's context is still loaded.
When the script cannot run (no code execution, or an interpreter older than Python 3.11), say so in one line and check the same things by hand against `references/calibration-protocol.md` and `references/profile-format.md`: the `calibration/round-NN.md` numbers run contiguously from `01` with no gap and no repeat, each round file's frontmatter parses, and `profile.md` still parses, stays at or under the 10,000-token ceiling counted as characters divided by four, carries a `token_estimate` equal to that same count, keeps all seventeen sections present in the fixed order, and has every golden example complete with `<bad>`, `<good>`, and `<why>`.

## Redlining Without Chat

Redlining happens in chat, or by the person editing the generated artifact file directly and re-running this skill with `--corrections <edited-path>`.
There is no HTML server for this stage; one is held off until chat redlining actually hurts.
`--corrections` is also how a behavior eval scripts a round end to end without a live chat turn.

## Finish

End by naming the files written, `<extractions-root>/<slug>/calibration/round-NN.md` and `<extractions-root>/<slug>/profile.md`, and the next stage's command, `/metacognition:skillify <slug>`.
Then stop.

## Inputs and Outputs

- Reads: `references/settings.md` (to resolve settings by hand when the script cannot run); `references/extraction-theory.md` rule 15; `references/calibration-protocol.md` (always, first, for the task bank and the fold-back tree); `references/profile-format.md`'s `calibrated` frontmatter field entry (the calibrated-state test); `<extractions-root>/<slug>/profile.md` (the only extraction file this skill ever reads for judgment; never `archive.md`); `<extractions-root>/<slug>/interview-spec.md` (`calibration_threshold`, `target_skill`); the target skill's `evals/` directory when `target_skill` is set.
All extraction paths resolve against the extraction root, `extractions` under the working directory by default or the configured or passed root.
- Scripts: `python3 scripts/resolve_config.py` resolves the settings and `python3 scripts/validate_artifacts.py` runs the closing self-check. Both import the sibling parser `scripts/yaml_subset.py`, which a skill never runs on its own.
- Writes: `<extractions-root>/<slug>/profile.md` (fold-back edits, the `<calibration_state>` section, the `calibrated` and `version` frontmatter fields); `<extractions-root>/<slug>/calibration/round-NN.md`; the extraction README's `calibrate rounds, last count` cell.
- Dispatches: nothing.
Calibrate runs entirely in-session; it never hands work to a subagent.

## What This Skill Never Does

- Never reads `archive.md`.
The point of a round is to test the compressed `profile.md` the way a real consumer will load it, and reaching for the archive would defeat that test.
- Never ships a probe.
Every generated artifact carries the never-ships probe header from step 3, in every domain, including one whose eventual skill is forbidden from authoring unattended.
- Never resolves a (c) tension on its own.
A correction that contradicts an existing rule always goes back to the person for which rule wins; calibrate encodes the answer, it does not guess it.
- Never auto-runs another round.
Each invocation runs exactly one round and stops; the person decides when to run the next.
- Never auto-chains into `/metacognition:skillify` or any other pipeline stage.
This session's completion is the round file and the updated `profile.md` on disk, nothing more.
- Never serves an HTML page for redlining.
Chat and `--corrections <path>` are the only two ways a round takes corrections.

## Resources

- [references/settings.md](references/settings.md): the five tiers and two keys, for resolving settings by hand.
- [references/extraction-theory.md](references/extraction-theory.md): rule 15, why calibration exists.
- [references/calibration-protocol.md](references/calibration-protocol.md): the task bank, the domain-specific task construction guidance, the fold-back decision tree, and the round file format this skill writes to.
- [references/profile-format.md](references/profile-format.md): the `calibrated` frontmatter field entry, the single source for the calibrated-state test this skill applies and reports against.
- [references/interview-spec-format.md](references/interview-spec-format.md): the `calibration_threshold` field this skill reads, and the extraction README status table this skill updates.
- [scripts/resolve_config.py](scripts/resolve_config.py) and [scripts/validate_artifacts.py](scripts/validate_artifacts.py): the settings resolver and the structural validator; both import [scripts/yaml_subset.py](scripts/yaml_subset.py).
