# Skill Scaffold Template

`/metacognition:skillify` is the pipeline's final stage: it turns a calibrated `profile.md` into a taste skill the person actually invokes.
This reference documents the three templates skillify fills: the SKILL.md template for a greenfield scaffold, the mode-file template for each selected mode, and the augment-diff template for the default path, where a skill for the domain already exists.
Every template here is complete on its own: skillify fills it from the profile and the archive with no other file needed.
When the `exemplar` setting names a skill, skillify reads that skill live at run time to match its shape, never a frozen copy of it; without one, this reference is the only template.
Where a template needs an example value, this reference uses a woodworking-fixtures domain: a shop-jig-and-joinery taste skill, chosen because it is concrete without being any of the person's actual domains.

Two sibling references hold facts this file does not restate: the archive's `### Qnn [<category>]` heading shape lives in [archive-format.md](references/archive-format.md), and the profile's frontmatter and seventeen-section order live in [profile-format.md](references/profile-format.md).
Skillify reads both directly; this reference only shows where those facts plug into the produced skill.

## Greenfield Or Augment

Skillify decides which template set to fill from `interview-spec.md`'s `target_skill` field: `target_skill` set means augment (write the SKILL.md diff template below) unless `--replace` is passed; no `target_skill` means greenfield (write the SKILL.md template and mode-file templates below).
`--replace` on an existing domain forces the greenfield scaffold beside the old skill and reports what to retire; that is still the greenfield path, aimed at a different directory.

## The SKILL.md Template

```markdown
---
name: <domain-slug>
description: "<one paragraph naming when this skill should be used: the roles it may take, the trigger phrases the person actually says, and any surface it explicitly does not cover>"
version: <version, in the scheme the target's neighboring skills use; omit this line when they carry none>
compatibility: "<one or two sentences naming the surfaces and capabilities the skill needs>"
---

# <Domain Title>

<One-line mission: what this skill assists with, and the boundary it never crosses.>

## Hard boundary (overrides everything below)

- Roles: **<role>, <role>, ... Never <role>.**
- <Refusal drawn from profile.md's hard_refusals: what the skill must never produce, and what it offers instead.>
- <consumer> holds final veto on every suggestion; the artifact belongs to <consumer>, not the skill.
- When unsure about anything, do not guess: list the uncertainty under "Open questions" at the end of the task.

## Registers

Select the register before applying the profile:

- **<register 1>**: <what changes under this register>
- **<register 2>**: <what changes under this register>

Ownership vs register: <state which surfaces this skill owns regardless of register, and which surfaces route to a different skill even in a register this skill would otherwise cover>.

## Workflow

1. Confirm the task fits this skill's domain. If it belongs to a different skill's territory, stop and redirect there.
2. Read [references/profile.md](references/profile.md) in full. It is the compressed profile: identity context, domain laws, hard refusals, phrase bank, golden examples, decision rules.
3. Pick the mode and read its reference file:

| Mode | When | File |
|---|---|---|
| <mode 1> | <trigger condition> | [references/mode-<mode-1>.md](references/mode-<mode-1>.md) |
| <mode 2> | <trigger condition> | [references/mode-<mode-2>.md](references/mode-<mode-2>.md) |

Mode selection when more than one fits: <the tie-break rule the person gave at skillify's mode question>.

4. Apply the mode.
5. List every uncertainty at the end of the task under "Open questions" so <consumer> knows to look for them.

## The deep reference

[references/archive.md](references/archive.md) is the full interview the profile was compressed from.
Do not load it wholesale.
Consult it when the compressed profile does not answer a question, using the section map below.
Question numbers are interleaved across categories (the interview followed threads, not a fixed order); grep the question index rather than assuming ranges.

- **<category 1>**: <one line naming what this category covers>
- **<category 2>**: <one line naming what this category covers>

Lookup pattern: `grep -n "^### Q" references/archive.md` for the question index, then read the relevant range.

## Profile canon is read-only

`profile.md` and `archive.md` are canon in <consumer>'s own words.
Never edit them; content changes come only from <consumer> or a new interview session.
A lint conflict between this skill's other rules and the profile gets an exemption, never an edit to the profile.

## Resources

### references/

- [profile.md](references/profile.md): the compressed profile. Read first, always.
- [archive.md](references/archive.md): the full interview. Grep, don't load.
- [mode-<mode-1>.md](references/mode-<mode-1>.md), [mode-<mode-2>.md](references/mode-<mode-2>.md): one per workflow mode.
```

### Example Values, Woodworking Fixtures

The bracketed placeholders above resolve, for the woodworking-fixtures domain, roughly like this: `name: woodworking-fixtures`; roles `jig designer, shop-safety reviewer, never build-log author`; registers `Shop notes` (terse, tool names and dimensions only) and `Teaching a beginner` (same judgment, slower pace, no jargon without a gloss); categories `Joinery philosophy`, `Jig and fixture design`, `Tool selection`, `Shop safety`.
These are illustrations only; skillify fills every placeholder from the actual interview answers and the actual profile, never from this reference.

## Frontmatter Field Reference

A produced SKILL.md carries exactly these frontmatter keys and no others: `name`, `description`, `compatibility`, and `version` only where a version is stamped.
Every path in a produced SKILL.md is relative to the skill's own directory, such as `references/profile.md`; never an absolute path, never a path that climbs into a parent directory, and never a plugin-root variable.

- `name`: the domain slug, matching the extraction's `domain` field and the skill's own directory name.
- `description`: a single quoted paragraph, not a list. It states when the skill should trigger, in the person's own trigger phrases where the interview captured them, and names any adjacent surface the skill explicitly does not cover. This is the field the harness matches against a request, so vague language here costs the skill its own triggering. It runs at most 1,024 characters and contains no angle-bracket token, so a placeholder such as `<domain-slug>` is always filled in, never left in the description.
- `compatibility`: one or two sentences, at most 500 characters, naming the surfaces and capabilities the skill needs. A produced taste skill needs only file reading and `grep` (or the surface's equivalent).
- `version`: optional. Skillify stamps it only when the target's neighboring skills carry a `version:` field, in the scheme those neighbors use, and names no version scheme of its own. Skillify never bumps an existing skill's version; it reports what the person may want to bump.

## The Hard Boundary Block

Every produced skill's hard boundary states its roles explicitly, drawn from the roles the person names when skillify asks "which roles the skill may take": reviewer, critic, advisor, author, or never-author, and any domain-specific role the interview surfaced.
A boundary such as "editor, critic, interviewer, never author" is the default when the interview did not push toward a different boundary: most taste domains are safer as a veto-and-critique layer over the person's own output than as an unattended author.
Each refusal listed under the boundary traces to a `<never>` entry in `profile.md`'s `hard_refusals` section (see [profile-format.md](references/profile-format.md)); skillify does not invent refusals the profile does not already state.

## The Register Block

A register is a context that changes how the profile applies without changing which rules apply: tone, formality, or terseness shift, but the underlying judgment does not.
Registers come from `interview-spec.md`'s `registers` field, carried through `archive.md` and `profile.md` unchanged.
Ownership is a separate question from register: a surface belongs to this skill or it does not, regardless of which register it uses.
State both explicitly: a skill that only states its registers, without also stating what it does and does not own, leaves a produced skill guessing at its own edges.

## The Workflow Section

Every produced skill's workflow reads `references/profile.md` in full on every invocation, never a summary or an excerpt, because the profile is already the compressed form and a further summary loses exactly the specificity that makes a taste skill useful.
The mode table is the second load-bearing piece: it names every mode the skill supports and the file that documents it, so the workflow step "pick the mode" resolves to a single table lookup rather than a judgment call the skill has to remake on every invocation.
The workflow's final step always lists every uncertainty at the end of the task under "Open questions", matching the profile's own `usage` fallback: when a case falls outside what the profile covers, the skill flags rather than guesses.

## The Deep-Reference Lookup Pattern

A produced skill never loads `archive.md` wholesale; the interview can run to tens of thousands of tokens, and loading all of it on every invocation defeats the reason `profile.md` exists.
The section map skillify writes into the SKILL.md's deep-reference block is derived mechanically from the archive's `### Qnn [<category>]` headings (the heading shape [archive-format.md](references/archive-format.md) documents): skillify groups question numbers by category and lists each category as one bullet naming what it covers, so a reader scanning the map picks a category, then greps the question index for that category's numbers.
Because question numbers interleave across categories in the order they were actually asked, the section map is a grouping, not a claim that the numbers fall in a contiguous range; the lookup pattern (`grep -n "^### Q" references/archive.md`) is what actually finds a given question, not the range implied by adjacent bullets.

## The Mode-File Template

One `references/mode-<name>.md` file per mode the person selects at skillify's mode question.
The default mode set, offered as a starting menu and narrowed or extended per the person's answer, is `review`, `critique`, `advise`, `generate-with-veto`:

| Mode | Shape |
|---|---|
| `review` | Reads a finished artifact and reports findings against the profile's laws and refusals; does not edit. |
| `critique` | Same input as review, but structured as a bad-to-good delta per finding, citing the profile's `golden_examples` pattern where one applies. |
| `advise` | Answers a direct question ("how would you handle this", "what would you add here") without requiring a full artifact to review. |
| `generate-with-veto` | Produces a draft artifact only when the hard boundary permits authoring, always labeled as a draft the person must approve before it ships under their name. |

A domain whose hard boundary is never-author (the default boundary above) omits `generate-with-veto` entirely; a domain where the interview established that a full author role is safe keeps it.
Each mode file follows the same shape regardless of which mode it documents:

```markdown
# Mode: <name>

<One line: what this mode does and when the workflow table routes to it.>

## Steps

1. <first step, grounded in what the profile's judgment_fingerprint and decision_rules require for this mode>
2. <subsequent steps>

## What This Mode Never Does

- <boundary specific to this mode, if narrower than the skill's hard boundary>

## Output Shape

<What the mode returns: a findings list, a redlined excerpt, a draft plus veto flag, an answer. Named concretely, not "helpful output.">
```

A mode file is where mode-specific judgment lives; the hard boundary in SKILL.md is where skill-wide judgment lives, and a mode file never contradicts it.

## The Augment Diff Template

Augment is the default whenever `target_skill` names an existing skill; skillify proposes a diff to its existing SKILL.md and only writes `references/profile.md` and `references/archive.md` into that skill's directory after the person approves.
The diff has two parts: a profile-load step to insert into the existing workflow, and a conflict table naming every existing rule the profile contradicts.

### The Profile-Load Step

Inserted into the existing SKILL.md's workflow, as early as the existing steps allow without breaking a step that already depends on order:

```markdown
N. Read [references/profile.md](references/profile.md) in full. It is the compressed taste profile from the `/metacognition:*` pipeline; apply it alongside this skill's existing rules, per the conflict resolutions below where the two disagree.
```

### The Conflict Table

One row per existing-skill rule the profile contradicts, sourced by comparing the profile's `domain_laws`, `hard_refusals`, and `decision_rules` against the target SKILL.md's current text:

| Existing rule | Profile's evidence | Proposed resolution |
|---|---|---|
| <the existing SKILL.md's rule, quoted or closely paraphrased, with its source line> | <the profile section and content that contradicts it, e.g. `hard_refusals`: "Never X. Bad: ... Use: ..."> | <keep existing, adopt profile, encode both as a register-dependent tension, or flag for the person's call> |

A rule the profile does not touch is not a row; the table lists contradictions only, not every existing rule.
The proposed resolution defaults to the profile's answer when the profile carries stronger evidence (a `hard_refusals` entry against an unsourced existing preference), and defaults to flagging the person's call when both sides carry comparable evidence; skillify never resolves a genuine tie on its own.

### Presenting The Diff

The full diff, profile-load step plus conflict table plus resolutions, is presented to the person for review before any file changes; `--dry-run` stops here regardless.
On approval, skillify applies exactly the reviewed diff, writes `references/profile.md` and `references/archive.md`, and records the skillify in the extraction README's status table.
Re-running skillify after a later calibration round replaces `references/profile.md` and produces a fresh diff against the SKILL.md as it stands then; the extraction's own `profile.md` stays canonical, and the copy inside the produced skill is always the thing that gets overwritten, never the other way around.
