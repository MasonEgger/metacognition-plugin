# Skillify

```text
/metacognition:skillify <domain-slug>
```

Skillify turns the calibrated profile into a skill you can invoke.
It is the last stage, and it is also where the choice between augmenting an existing skill and writing a new one is made.

## Arguments

- `<domain-slug>`: the extraction to skillify. Required. Skillify never guesses which extraction to act on.
- `--into <dir>`: where a new skill is written.
- `--replace`: writes a new skill beside an existing target skill, instead of augmenting it.
- `--dry-run`: stops at the proposed files and diff and writes nothing.
- `--extractions-root <dir>`: overrides the extraction root for this run.

## What It Asks of You

If the profile's `calibrated` field is `false`, skillify warns you and asks whether to proceed.
The choice is yours.

Then it asks four things, one at a time: which roles the skill may take (reviewer, critic, advisor, author, never-author, or a role the interview surfaced), which modes it needs from `review`, `critique`, `advise`, and `generate-with-veto`, the trigger phrases you actually say for this domain, and what the skill must refuse.
When augmenting, it asks only what the existing skill does not already answer.

The mode depends on `target_skill` in the interview spec.
With a target skill set, augment is the default.
With none, skillify writes a new skill.
With `--replace`, it writes a new skill beside the old one and tells you which old files to retire.

In augment mode, skillify shows you a diff to the existing `SKILL.md` first, with a profile-load step and a table of every existing rule the profile contradicts.
Nothing in the existing skill changes until you approve that diff.
Where both sides carry comparable evidence, the call is flagged for you and never decided by skillify.

Before it writes a scaffold or proposes a structure, skillify loads the provider's skill-craft guidance through the `plugin-dev` plugin's `skill-development` skill.
When `plugin-dev` is not installed, or the surface cannot load another plugin's skill, skillify says so in one line and continues on its own templates.
It then recommends installing `plugin-dev` in its closing message.
The plugin is recommended and never required.

When augmenting, skillify first assesses the existing skill's structure: description triggering, progressive disclosure, size, and reference layout.
When the structure holds, it says so in one line and moves on to the diff.
When it does not, skillify shows the best alternative layout beside keeping the skill as it is, with its findings as the reasoning, and waits for your choice.
A restructure happens only on your explicit choice, and it still goes through a reviewed diff.
With `--dry-run`, skillify shows the assessment and the options and applies nothing.

There is an advanced `exemplar` setting for a skill whose shape yours may follow.
Most people never set it, and skillify says nothing when it is unset or the path does not exist.
See [Configuration](../configuration.md).

## What It Produces

A new skill holds `SKILL.md`, `references/profile.md`, `references/archive.md`, and one `references/mode-<name>.md` for each mode you chose.
The profile and archive are copied from the extraction, which stays the canonical copy.

- With `--into <dir>`, the skill is written under `<dir>/skills/<slug>/`.
- Without `--into` and without a target skill, it is written to `<root>/<slug>/skill/<slug>/` and packaged as `<root>/<slug>/skill/<slug>.zip`, with `<slug>/` as the single top-level entry, ready to upload.
- In augment mode, on your approval, the reviewed diff is applied and the profile and archive copies land in the existing skill's `references/` directory.

The package includes the verbatim interview archive.
Skillify tells you so before it creates the package.
See [Privacy](../privacy.md).

Skillify lists the archive's exports as follow-up work for other skills.
It never writes them into the produced skill.

Skillify never bumps a version and never edits a plugin or marketplace manifest.
It reports what you may want to bump, in the scheme the target already uses.
On Claude Code only, it may offer a `~/.claude/rules/<slug>.md` pointer so the skill loads for matching files, and it writes that file only on your approval.
It records the result in the `skillify` cell of the extraction README.

## How Long It Takes

No source gives a duration.
Your part is four questions and a review of the proposed files or diff.
The rest varies with the size of the profile and archive.
Packaging the zip needs code execution.
Where that is unavailable, skillify leaves the directory in place and names it for you to package.

## What Done Looks Like

The skill directory and its files are written.
In the default case the zip exists and every entry in it starts with `<slug>/`.
Under `--dry-run`, the printed plan is the result.
Skillify names what it wrote, and there is no next stage.
