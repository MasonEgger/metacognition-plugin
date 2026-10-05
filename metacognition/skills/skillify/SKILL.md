---
name: skillify
version: 0.1.1
description: 'This skill should be used when the user asks to "skillify a domain", "turn the profile into a skill", "turn this profile into a skill", "augment a skill with the profile", "scaffold a new skill from the profile", "greenfield a skill for a domain", "replace a skill with the profile", or runs `/metacognition:skillify`. Turns a calibrated `profile.md` into a taste skill the person actually invokes: greenfield when no `target_skill` is set, augment (the default whenever one is) otherwise. The augment path always stops at a reviewed `SKILL.md` diff; nothing lands in an existing skill without the person''s approval.'
compatibility: 'Runs on Claude Code, Cowork, and claude.ai. The scripts need code execution and Python 3.12 or newer; without them the skill applies the same rules by hand. It reads the extraction files and writes a skill directory, plus a zip package where a zip command can run, so it needs file access or the files uploaded to the conversation. The optional plugin-dev plugin, where installed, supplies a skill-structure baseline.'
---

# Skillify

Turn a calibrated `profile.md` into a taste skill the person actually invokes.
Skillify is the pipeline's final stage: everything upstream of it, design, interview, compile, calibrate, exists to earn this step a profile worth turning into a skill.
This is also where the augment-or-replace call is made, after the interview and calibration are both done, never earlier.

## Arguments

- `<domain-slug>`: required. The extraction to skillify; see Preflight for why there is no default.
- `--into <dir>`: optionally names where a greenfield scaffold is written; see Mode Selection for how it resolves and what happens without it.
- `--replace`: forces the greenfield path beside an existing target skill.
- `--dry-run`: stops at the proposed files and diff without writing anything.
- `--extractions-root <dir>`: optionally overrides the extraction root.

## Read First

Read `references/skill-scaffold.md` in full before writing a single file.
It is the single source for the three templates this skill fills: the greenfield SKILL.md template, the mode-file template, and the augment-diff template.
This skill does not restate any of them, only applies them.

Then read `references/profile-format.md` and `references/archive-format.md`.
Both are pointers this skill reads directly rather than restates: the profile frontmatter's `target_skill` field is what step 7 of Preflight below resolves, and the archive's `### Qnn [<category>]` heading shape is what step 3 derives the produced skill's section map from.

Before writing a scaffold or proposing a structure, load the provider baseline: invoke `plugin-dev:skill-development` through the Skill tool.
When that plugin is not installed, or the surface cannot load another plugin's skill (claude.ai chat), say so in one line, continue on `references/skill-scaffold.md`, and recommend installing `plugin-dev` in the finish message.
The baseline is recommended, never required; nothing here fails without it.

Then, once Preflight step 2 has resolved the settings, check the `exemplar` setting.
The exemplar is an advanced option most people never set.
With no `exemplar` setting, or a setting whose path does not exist (`exists` is `false` in the resolved settings), skip the read and say nothing about it.
When one exists, read it live, never from memory or a cached copy, and let it shape the produced files.
The baseline review still runs, and its findings are answered, not skipped.

Precedence, in this order: the person's decision, then the provider baseline review, then the exemplar, then the bundled templates in `references/skill-scaffold.md`.
Those templates are complete on their own when nothing above them applies.

## Preflight

1. Read the arguments: `<domain-slug>` is required, not optional, unlike the earlier pipeline stages; skillify is the highest-stakes stage, the one that writes into another skill, so it never guesses which extraction to act on.
If it is missing, ask for it and stop rather than falling back to "the only extraction under the root."
`--into <dir>` names the target for a greenfield scaffold; `--replace` forces the greenfield path beside an existing target skill; `--dry-run` stops at the proposed files and diff without writing; `--extractions-root <dir>` optionally overrides the default extraction root.
2. Resolve settings and the extraction root.
Run `python3 scripts/resolve_config.py`, passing `--extractions-root <dir>` when that flag was given and `--set key=value` for any setting the person stated in the conversation or in Project instructions.
Read the JSON it prints, which carries the `exemplar` setting too, its value and its `exists` boolean; relay any `Loaded config from: <path>` line it printed, and state the root in one line: "Extraction root: `<path>`".
When the script cannot run (no code execution, or an interpreter older than Python 3.12), apply the same tiers by hand from `references/settings.md`, and say so in one line.
3. Load `<extractions-root>/<domain-slug>/profile.md`.
Missing means there is nothing to skillify yet; stop and name `/metacognition:compile <domain-slug>` as the prerequisite.
4. Check `profile.md`'s frontmatter `calibrated` field.
If `false`, warn the person per extraction theory rule 15 (calibration is the moat: an uncalibrated profile is a guess dressed as a rule) and ask whether to proceed anyway rather than refusing outright; the choice belongs to the person, not to this skill.
5. Load `<extractions-root>/<domain-slug>/interview-spec.md` for `target_skill`.
Confirm it agrees with `profile.md`'s own `target_skill` field; if the two disagree, say so and ask the person which one is current before continuing.
6. Determine the mode from `target_skill` and the flags, per Mode Selection below.
7. Resolve every path the chosen mode needs, per Mode Selection below.
Every resolved path is a data path against the working directory.
8. In augment or replace mode, load the target skill's existing `SKILL.md` and every file under its `<target-skill>/references/` now, before step 1 of the procedure asks the person anything.
This is what lets step 1 skip a question the existing skill already answers.

Throughout this skill, `<target-skill>` is the directory of the skill being produced or augmented, and every path written with that prefix is a file inside it, never one of this skill's own.

## Mode Selection: Greenfield or Augment

This is the augment-or-replace call, made here and nowhere earlier in the pipeline.

- `target_skill` set in `interview-spec.md`, `--replace` not passed: **augment**, the default whenever an existing skill claims the domain.
- `target_skill` not set (`null`): **greenfield**.
With `--into <dir>`, the skill is written under that directory.
Without `--into`, it is written to `<extractions-root>/<domain-slug>/skill/<domain-slug>/` and packaged, per step 3.
- `target_skill` set, `--replace` passed: **greenfield beside the existing skill**.
Still the greenfield path, aimed at a directory next to the old one; report at the end what the person should retire.

`target_skill` resolves in one of two forms: `<plugin>:<skill>`, which resolves to `<working directory>/<plugin>/skills/<skill>/`; or a directory path, relative paths resolving against the working directory and absolute paths used directly with no further resolution, the form an eval harness uses to point augment mode at a scratch copy of a fixture skill.
`--into` resolves the same two ways: a bare plugin name resolves to `<working directory>/<plugin>/`, and a directory path is used directly, absolute paths included, the same scratch-copy case for greenfield evals.

`--dry-run` applies to every mode: it stops at the proposed files and the diff, and writes nothing, packages nothing, regardless of what the person would otherwise approve.
In augment mode it also shows the structural assessment and the layout options from step 3, and applies nothing.
A dry run never asks for approval either, since there is nothing pending approval to write.

## The Six-Step Procedure

### 1. Ask the Person About Roles, Modes, Triggers, Refusals

One question at a time: which roles the produced or augmented skill may take (reviewer, critic, advisor, author, never-author, and any domain-specific role the interview surfaced), which modes it needs from the default set (`review`, `critique`, `advise`, `generate-with-veto`), the trigger phrases the person actually says for this domain, and what the skill must refuse.

In augment mode, ask only what the existing skill's `SKILL.md` (loaded in Preflight step 8) does not already answer: an existing hard boundary already states roles and refusals, and an existing mode table already states modes, so re-ask only where the profile's material suggests a gap or a change.
In greenfield mode there is no existing answer to skip; ask all four in full.

### 2. Read the Templates and Target Conventions

Read `references/skill-scaffold.md` and the exemplar, if one exists, per Read First, if not already open from that step.
Then read the target's other existing skills (every `SKILL.md` beside `<target-skill>`, in the same `skills/` directory) to match local conventions: heading style, how arguments are documented, whether skills there carry `version:` frontmatter at all.
A produced skill that ignores its new home's own conventions is a worse fit than one that follows `skill-scaffold.md` alone.

### 3. Write the Files

Every produced or diffed `<target-skill>/SKILL.md`, in either mode, must read `<target-skill>/references/profile.md` in full on every invocation, never load `<target-skill>/references/archive.md` wholesale, instruct the grep-by-section-map lookup for the archive that `references/skill-scaffold.md`'s Deep-Reference Lookup Pattern gives, state the hard boundary explicitly, declare register handling, and list every uncertainty at the end of the task under "Open questions".
A produced `<target-skill>/SKILL.md` meets the same upload constraints as this plugin's own skills: frontmatter keys limited to `name`, `description`, `compatibility`, and `version` only where a version is stamped; a `description` of at most 1,024 characters with no angle-bracket token, so no placeholder is left in it; a `compatibility` of at most 500 characters; and every path relative to the skill's own directory, per `references/skill-scaffold.md`'s Frontmatter Field Reference.
The section map is derived mechanically from the archive's `### Qnn [<category>]` headings, grouping question numbers by category, exactly as `skill-scaffold.md`'s Deep-Reference Lookup Pattern section describes; skillify does not invent categories the archive does not already name.
Tags after the category, such as `[items: n]`, are ignored and do not disturb the map.
`[closing]` is excluded from this derivation: the closing questions belong to no category the interview spec scoped, per `references/archive-format.md`'s pseudo-category rule, so they earn no entry in the produced skill's section map.

**Greenfield.** Scaffold `<target-skill>` from `skill-scaffold.md`'s SKILL.md template and mode-file template: `<target-skill>/SKILL.md`, `<target-skill>/references/profile.md` (copied from the extraction's canonical profile), `<target-skill>/references/archive.md` (copied from the extraction's canonical archive), and one `<target-skill>/references/mode-<name>.md` per mode selected in step 1.
With `--into <dir>`, `<target-skill>` is `<into>/skills/<domain-slug>/`; without `--into`, it is `<extractions-root>/<domain-slug>/skill/<domain-slug>/`.
Fill every placeholder from step 1's actual answers and the actual profile; never from `skill-scaffold.md`'s own woodworking-fixtures illustration.
Present the full proposed file set to the person before writing when this is the first skillify run for the domain; write on `--dry-run` only as a preview, nothing to disk.
Outside `--dry-run`, write the files directly: greenfield creates new files in a new directory, so nothing existing is at risk the way an augment diff is.
Without `--into`, package the directory once it is written.
The package contains the verbatim interview archive.
Say so to the person before creating it, because a package meant for upload carries everything they said in the interview.
Then create `<extractions-root>/<domain-slug>/skill/<domain-slug>.zip` with `<domain-slug>/` as its single top-level entry, ready to upload: from `<extractions-root>/<domain-slug>/skill/`, run `python3 -m zipfile -c <domain-slug>.zip <domain-slug>/` (the Python standard library; `zip -r <domain-slug>.zip <domain-slug>/` does the same where that command exists), then list the archive with `python3 -m zipfile -l <domain-slug>.zip` and confirm every entry starts with `<domain-slug>/`.
Where code execution is unavailable and the zip cannot be created, say so, leave the directory in place, and name it for the person to package.

**Augment.** First assess the existing target skill's structure against the baseline: description triggering, progressive disclosure, size, and reference layout.
Use the `plugin-dev:skill-reviewer` agent where it can be dispatched, and the loaded baseline otherwise; with neither available, assess against `references/skill-scaffold.md` and say the baseline was unavailable.
When the structure holds, say so in one line and continue on the diff below.
When it does not, present the best alternative layout beside keep-as-is, with the findings as the reasoning, and wait for the person's choice before drafting any diff.
A restructure is applied only on that explicit choice, and it still goes through a reviewed diff.
The assessment is a presented verdict, never an applied one.

Then prepare, but do not yet write, the copies of `<target-skill>/references/profile.md` and `<target-skill>/references/archive.md` that will land in the existing skill's directory, and the proposed diff to its `<target-skill>/SKILL.md`: a profile-load step inserted into the existing workflow (as early as the existing steps allow without breaking one that depends on order) plus a conflict table, per `skill-scaffold.md`'s Augment Diff Template, listing every existing rule the profile contradicts against the profile's own evidence and a proposed resolution.
Source conflicts by comparing the profile's `domain_laws`, `hard_refusals`, and `decision_rules` against the target `SKILL.md`'s current text; a rule the profile does not touch is not a row.
Default the proposed resolution to the profile's answer when its evidence is the stronger of the two (a `hard_refusals` entry against an unsourced existing preference), and default to flagging the person's call when both sides carry comparable evidence; never resolve a genuine tie unilaterally.
Present the full diff (profile-load step plus conflict table plus resolutions) to the person for review before any file changes.
`--dry-run` stops here regardless of what the review would have concluded.
On approval, apply exactly the reviewed diff, write `<target-skill>/references/profile.md` and `<target-skill>/references/archive.md` into the existing skill's directory, and continue to step 6.

**Replace.** Follow the greenfield path above, writing beside the existing skill rather than into a new location, and additionally report which files under the old skill's directory the person should retire once the new one is confirmed working.

### 4. Never Bump a Version or Edit a Manifest

Never edit a plugin or marketplace manifest in the target, in any mode.
Report what the person may want to bump, in whatever scheme the target's own skills and manifests already use, as part of the end-of-run report; do not make the edit on their behalf, and name no version scheme of your own.
A greenfield scaffold's own `<target-skill>/SKILL.md` may carry a `version:` frontmatter field, but only when step 2's read of the target's neighboring skills shows they carry one; stamp it in the scheme those neighbors use.
With no neighbors to read, as in the default package, stamp none.
This is an initial stamp on a brand-new file, not a bump, and it is the one version-shaped write this skill ever performs.

### 5. The Loader Step

This step runs on Claude Code only; on any other surface, skip it.

**Augment.** Confirm the existing skill's deterministic loader still covers the profile; state this confirmation in the end-of-run report.
If the loader does not cover the profile, for instance a path-rule pointer scoped too narrowly for the domain the profile now covers, name the gap and propose a fix, but do not edit anything outside the target without the person's approval, per the same rule that applies in greenfield mode below.

**Greenfield.** Offer a `~/.claude/rules/<domain-slug>.md` pointer, so the skill loads for the files that match the domain.
This lives outside the target, so write it only on the person's explicit approval; presenting the offer is not the same as writing it, and `--dry-run` never writes it regardless of approval.

### 6. Record the Skillify in the Extraction README

Update `<extractions-root>/<domain-slug>/README.md`'s `skillify -> plugin:skill (mode)` cell with the target skill and whether this run applied in augment, greenfield, or replace mode, per `references/interview-spec-format.md`'s standing rule that every pipeline stage updates the table as its last action.
Skip this write on `--dry-run`: nothing was applied, so nothing is recorded yet.
Re-running skillify after a later calibration round replaces the skill's `<target-skill>/references/profile.md` copy and produces a fresh diff against the target `SKILL.md` as it stands then; the extraction's own `profile.md` stays canonical, and the copy inside the produced or augmented skill is always the thing that gets overwritten, never the other way around.

## Finish

End by naming what was written: the skill directory `<target-skill>` and its files, and, in the default case, the package `<extractions-root>/<domain-slug>/skill/<domain-slug>.zip` (or, under `--dry-run`, the plan that was printed).
List the archive's Exports as follow-up work for other skills, and state that exports are never written into the produced skill.
When the baseline could not be loaded, recommend installing `plugin-dev`.
Skillify is the last stage; there is no next stage's command.
Then stop.

## Inputs and Outputs

- Reads: `references/skill-scaffold.md` (always, first); `references/profile-format.md` and `references/archive-format.md` (pointers for the section map and frontmatter fields); `references/settings.md` (to resolve settings by hand when the script cannot run); the skill the `exemplar` setting names, when one is set and exists, read fresh every run, never cached.
Optional and external, never files in this skill's slice: the `plugin-dev:skill-development` skill, loaded through the Skill tool, and the `plugin-dev:skill-reviewer` agent, dispatched where the surface allows.
`<extractions-root>/<domain-slug>/profile.md` and `interview-spec.md` (read only; this skill never edits the extraction's own canonical copies); `<extractions-root>/<domain-slug>/archive.md` (copied into the produced skill, never edited).
In augment or replace mode, also the target skill's existing `<target-skill>/SKILL.md` and every file under its `<target-skill>/references/`, resolved from `target_skill` against the working directory.
All extraction and target paths resolve against the working directory, `extractions` under it by default or the configured or passed root for the former.
- Scripts: `python3 scripts/resolve_config.py` resolves the settings. It imports the sibling parser `scripts/yaml_subset.py`, which a skill never runs on its own.
- Writes (skipped entirely under `--dry-run`): greenfield or replace, `<target-skill>/SKILL.md`, `<target-skill>/references/profile.md`, `<target-skill>/references/archive.md`, and one `<target-skill>/references/mode-*.md` per selected mode, plus `<extractions-root>/<domain-slug>/skill/<domain-slug>.zip` when no `--into` was given; augment, on approval only, the target skill's `<target-skill>/references/profile.md`, `<target-skill>/references/archive.md`, and the reviewed diff applied to its `<target-skill>/SKILL.md`; either mode, `<extractions-root>/<domain-slug>/README.md`'s skillify cell.
A `~/.claude/rules/<domain-slug>.md` pointer, written only on the person's separate approval per step 5.
- Dispatches: optionally the `plugin-dev:skill-reviewer` agent for the augment structural assessment; otherwise nothing.
Skillify runs in-session.

## What This Skill Never Does

- Never bumps a version or edits a manifest.
It reports what the person may want to bump and leaves the edit to them; the one exception is stamping `version:` on a brand-new greenfield `SKILL.md`, which is an initial stamp, not a bump.
- Never lands an augment diff without the person's approval.
The profile-load step and the conflict table are always presented in full before any file changes; `--dry-run` stops at the same point regardless.
- Never writes the loader pointer without the person's approval.
It lives outside the target, so an offer is not a write; step 5 writes it only when the person says yes.
- Never auto-chains into another pipeline stage.
This session's completion is the files it wrote (or, under `--dry-run`, the plan it printed) and the README update, nothing more.
- Never edits the extraction's canonical `profile.md` or `archive.md`.
It reads them and copies them; any correction to either belongs to `/metacognition:calibrate` or a resumed `/metacognition:interview` session, not to this skill.
- Never resolves a genuine conflict-table tie on its own.
A row where both the existing rule and the profile carry comparable evidence is flagged for the person's call, never decided unilaterally.
- Never invents template content.
Every placeholder in the greenfield SKILL.md, mode files, and augment diff is filled from step 1's actual answers and the actual profile, never from `skill-scaffold.md`'s own woodworking-fixtures illustration.

## Resources

- [references/skill-scaffold.md](references/skill-scaffold.md): the SKILL.md template, the mode-file template, and the augment-diff template this skill fills; single source, not restated here.
- [references/settings.md](references/settings.md): the five tiers and two keys, for resolving settings by hand.
- [references/profile-format.md](references/profile-format.md): the frontmatter fields, including `target_skill`, this skill reads from `profile.md`.
- [references/archive-format.md](references/archive-format.md): the `### Qnn [<category>]` heading shape this skill derives the produced skill's section map from.
- [references/interview-spec-format.md](references/interview-spec-format.md): the `target_skill` field's two forms, and the extraction README status table this skill updates.
- [references/extraction-theory.md](references/extraction-theory.md): rule 15, why an uncalibrated profile is warned about rather than refused outright.
- [scripts/resolve_config.py](scripts/resolve_config.py): the settings resolver; it imports [scripts/yaml_subset.py](scripts/yaml_subset.py).
