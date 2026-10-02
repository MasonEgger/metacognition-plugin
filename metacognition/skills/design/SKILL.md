---
name: design
version: 0.1.0
description: 'This skill should be used when the user asks to "design an interview for a domain", "scope a new taste extraction", "design the extraction for a domain", "build the interview spec for a domain", "design an augment interview against an existing skill", or runs `/metacognition:design`. Produces two artifacts: `interview-spec.md` and the extraction README. It never asks the person a taste question itself; that is the job of /metacognition:interview.'
compatibility: 'Runs on Claude Code, Cowork, and claude.ai. The scripts need code execution and Python 3.11 or newer; without them the skill applies the same rules by hand. Research uses the plugin research agent where the surface loads plugin agents, and otherwise runs in-session; it needs web access, or it continues on the scoping answers alone.'
---

# Design

Scope a new taste extraction and produce the two artifacts `/metacognition:interview` runs against: `interview-spec.md` and the extraction `README.md`.
Design is the crafter, not the interviewer.
It never asks the person a single taste question, so the same design session can be reviewed and trusted before hours of interview time get spent against it.

## Arguments

- `<domain>`: the domain statement. Required.
- `--target <plugin>:<skill>`: optionally names an existing skill the extraction will augment.
- `--extractions-root <dir>`: optionally overrides the extraction root.

## Read First

Read `references/extraction-theory.md` in full before asking a single scoping question or writing a single line of `interview-spec.md`.
Every rule this skill leans on below, stated vs. revealed preference (rule 1), register separation (rule 9), unknown-unknowns (rule 13), forced choice (rule 4), artifact grounding (rule 7), saturation (rule 10), the technique index (rule 16), is defined there in full; this skill does not re-derive them.

## Preflight

1. Read the arguments: the domain statement is required (`<domain>`); `--target <plugin>:<skill>` optionally names an existing skill; `--extractions-root <dir>` optionally overrides the default root.
2. Resolve settings and the extraction root.
Run `python3 scripts/resolve_config.py`, passing `--extractions-root <dir>` when that flag was given and `--set key=value` for any setting the person stated in the conversation or in Project instructions.
Read the JSON it prints, relay any `Loaded config from: <path>` line it printed, and state the root in one line: "Extraction root: `<path>`".
When the script cannot run (no code execution, or an interpreter older than Python 3.11), apply the same tiers by hand from `references/settings.md`, and say so in one line.
3. Derive the domain slug from the domain statement: lowercase it, restrict to ASCII, collapse every run of spaces and punctuation to a single hyphen, strip leading and trailing hyphens.
Print the derived slug back to the person ("Domain slug: `<slug>`") before continuing, so a bad derivation is caught immediately instead of after nine steps of work.
4. If `<extractions-root>/<slug>/interview-spec.md` already exists, say so and ask whether to overwrite it or restate the domain, as the opening move of scope Q&A rather than a separate gate.

## The Nine-Step Procedure

Design never asks the person a taste question.
Every question below is about the shape of the interview to come, never about their actual judgment in the domain; that boundary is what keeps this session reusable and reviewable before any interview time is spent.

### 1. Scope Q&A (One Question at a Time)

Ask ONE question at a time, each building on the prior answer, never batching several into one turn.
Cover, in order:

- The domain in one sentence.
- Which registers the profile must cover (extraction theory rule 9); a domain with a single register still gets an explicit answer, never an assumed default.
- What artifacts exist and where (repo paths, documents, past decisions), to ground the interview later (rule 7).
- Who consumes the profile: which future skill, and what it must let the model do, for example "review PRs like me" or "pick a joinery approach like me".
- Whether a skill already exists for this domain.
When `--target` named one, confirm it rather than opening the question fresh (`--target` is a shortcut, not a skip); otherwise ask directly.
Once a target skill is identified, by flag or by answer, record it as `target_skill` and load that skill's `SKILL.md` and every file under its `references/` as artifacts for both the research step (step 2) and the artifact plan (step 6).
Whether skillify later augments or replaces that skill is not decided here; recording `target_skill` is as far as design goes.

Record every answer verbatim under `## Starting context`.
Extraction theory rule 11, verbatim capture, applies to design's own scoping conversation, not only to the interview transcript that follows later.

### 2. Research

Once scope Q&A closes, run the research.
Pass the one-sentence domain statement, the consumer capability from step 1, and, in augment mode, the target skill's file paths as artifact paths.
`references/research-contract.md` defines the input and output contract; pass nothing beyond what it asks for.

- Where the surface loads plugin agents (Claude Code and Cowork), dispatch the `metacognition:domain-research` agent via the Agent tool with that input.
- Where it does not (claude.ai chat), run the same contract yourself in this session, following `references/research-contract.md` and returning the same fixed shape.
- With no web access, say so in one line and continue to step 3 on the scoping answers alone.

Present the returned dimensions, schools, vocabulary, and artifact types back to the person as a single list and let them drop or add entries before anything is written down.
If the research returns `no relevant results`, say so plainly and move to step 3 on the scope Q&A alone; never pad a thin result to look complete.

### 3. Unknown-Unknowns Pass

Per extraction theory rule 13, name 3 to 5 dimensions the person likely has real taste about but did not raise in step 1 or step 2.
Frame each as "you may have taste about X" rather than "you must answer X"; the person engages with any, all, or none.
Record each as `engaged` or `declined` under `## Unknown-unknowns surfaced`.
A declined dimension is recorded, not silently dropped, so a later design run on the same domain does not re-surface it without new cause.

### 4. Category Map

Instantiate the seven generic slots below, each with its default floor.
A domain may add slots (for example, a "trade-off resolution" slot for a code domain) and may rename any of the seven for domain-appropriate labels, but every one of the seven must map to something in the final table; none may be dropped.

| Generic slot | Purpose | Default floor |
|---|---|---|
| Beliefs and contrarian takes | What practitioners in this domain get wrong | 10 |
| Mechanics | How the person actually does the work, not how they think they do | 15 |
| Aesthetic crimes | What makes them cringe, close the tab, reject the PR | 12 |
| Voice and posture | How they critique, praise, disagree, express uncertainty here | 10 |
| Structural preferences | How they organize, decompose, sequence | 10 |
| Hard nos | Lines they will not cross | 8 |
| Red flags | What makes them distrust an artifact or a person in this domain | 8 |

Write the final `## Category map` table with columns `Category | Maps to generic slot | Floor | Saturation rule`.
The saturation rule column carries the standing rule from extraction theory rule 10 (three consecutive answers with no new constraint) unless a category earns a documented exception.

### 5. Question Seeds

Write 5 to 8 seeds per category under `## Question seeds`, each pairing a starting question with a named probe pattern: `forced-choice`, `ladder`, `contrast`, `artifact`, `critical-incident`, or `triad`, matching extraction theory rule 16's technique index.
Seeds are starting points for the interview, never a script.

When `target_skill` is set, ground at least one seed per category in the existing skill, for example "your skill says X; is that still true, and when not?", and hold at least one third of all seeds across the whole spec to this grounded pattern.
Count seeds across every category before closing this step to confirm the floor is met; a spec that falls short goes back and adds seeds rather than shipping under the floor.

### 6. Artifact Plan

Write `## Artifact plan`: every real artifact the interview will ground questions in, its path or fetch instructions, and how it gets used, a contrast pair, a single grounding example, or a sorting set.
In augment mode, the target skill's own files come first: extraction theory rule 7 treats an existing skill as itself an artifact, a stated preference from an earlier interview, now probed against what the person says today.

Set `artifacts_available: false` in frontmatter when no real artifacts exist.
This does not skip the section; it records that the interview leans harder on hypotheticals and contrast probing, and the resulting profile carries lower confidence.

### 7. Forced-Choice Bank

Write 8 to 12 numbered entries (`FC-01`, `FC-02`, and so on) under `## Forced-choice bank`, each a pair of concrete options, plausible on both sides, plus the standard probe: which, why, and what would flip the answer.
Draw pairs from the artifact plan where possible; write fresh pairs only where no artifact grounds the choice.

### 8. Closure Pass

Before writing anything to disk, re-read the whole session and list every question, fork, or ambiguity raised.
Resolve each one now: ask it if it is still open, or, for anything the person waved off with "whatever" or "you decide", record the concrete choice made with a one-line rationale rather than leaving it phrased as a question.
`interview-spec.md` never carries an "Open questions" or "TBD" section; every decision the interview needs is closed before step 9 writes the file.

### 9. Write the Artifacts

Write `<extractions-root>/<slug>/interview-spec.md` exactly per the fenced template and field reference in `references/interview-spec-format.md`: frontmatter (`domain`, `title`, `registers`, `consumer`, `target_skill`, `artifacts_available`, `calibration_threshold`, default `3` unless the person names a different number during scope Q&A or the closure pass, `created`), then the eight body sections in the order that reference documents: Starting context, Research findings, Unknown-unknowns surfaced, Category map, Question seeds, Artifact plan, Forced-choice bank, Closing questions.

Append the three fixed closing questions verbatim to `## Closing questions`, per `references/interview-spec-format.md`: "What did this interview miss?", "If you could give one instruction that overrides everything else, what is it?", and "What did you learn about yourself answering this?"
Add any domain-specific closer after the three fixed ones, never in place of them.

Then write `<extractions-root>/<slug>/README.md` with the status table from `references/interview-spec-format.md`'s "Extraction README Status Table" section: `design | interview n/floor | compile tokens | calibrate rounds, last count | skillify -> plugin:skill (mode)`.
Fill only the `design` cell, spec exists plus today's date; every other cell starts blank, to be filled by the pipeline stage that produces it.

## Finish

End by naming the files written, `<extractions-root>/<slug>/interview-spec.md` and `<extractions-root>/<slug>/README.md`, and the next stage's command, `/metacognition:interview <slug>`.
Then stop.

## Inputs and Outputs

- Reads: `references/settings.md` (to resolve settings by hand when the script cannot run); `references/extraction-theory.md` (always, first); `references/interview-spec-format.md` (the template and field reference for step 9); `references/research-contract.md` (the research contract for step 2).
In augment mode, also reads the target skill's `SKILL.md` and `references/*.md`, a data path resolved from the working directory.
- Scripts: `python3 scripts/resolve_config.py` resolves the settings. It imports the sibling parser `scripts/yaml_subset.py`, which a skill never runs on its own.
- Writes: `<extractions-root>/<slug>/interview-spec.md` and `<extractions-root>/<slug>/README.md`.
Both resolve against the extraction root, `extractions` under the working directory by default or the configured or passed root.
- Dispatches: the `metacognition:domain-research` agent (step 2) where the surface loads plugin agents, and nothing else.

## What This Skill Never Does

- Never asks the person a taste question.
Every question above is about the shape of the interview, never about their judgment in the domain; the taste questions belong to `/metacognition:interview` alone.
- Never auto-chains into the interview or any other pipeline stage.
The person runs `/metacognition:interview` on their own schedule; this session's completion is `interview-spec.md` and the README existing on disk, nothing more.
- Never decides augment vs. replace.
It records `target_skill` when one exists and leaves the augment-or-replace call to skillify.
- Never invents research findings.
An empty or `no relevant results` return from the research is presented as empty, not padded to look thorough.

## Resources

- [references/settings.md](references/settings.md): the five tiers and two keys, for resolving settings by hand.
- [references/extraction-theory.md](references/extraction-theory.md): the sixteen rules this skill applies at every step; read first, every run.
- [references/interview-spec-format.md](references/interview-spec-format.md): the frontmatter, section order, and the extraction README status table this skill writes to.
- [references/research-contract.md](references/research-contract.md): the input and output contract for the step 2 research.
- [scripts/resolve_config.py](scripts/resolve_config.py): resolves the settings; its parser dependency is [scripts/yaml_subset.py](scripts/yaml_subset.py).
