---
name: interview
version: 0.1.1
description: 'This skill should be used when the user asks to "run the taste interview for a domain", "interview me about a domain", "start the extraction interview", "resume the interview for a domain", "continue the taste interview", or runs `/metacognition:interview`. Runs the interview a prior `/metacognition:design` session scoped, asking one probe or one short battery per turn, researching a deferral to outside practice in the same turn, and writing `archive.md` incrementally. It never compiles the archive into a profile; that is the job of `/metacognition:compile`.'
compatibility: 'Runs on Claude Code, Cowork, and claude.ai. The scripts need code execution and Python 3.12 or newer; without them the skill applies the same rules by hand. It reads the extraction files design wrote and writes archive.md in the same directory, so it needs file access or the files uploaded to the conversation. Practice lookups use the plugin research agent where the surface loads plugin agents, and otherwise run in-session with web access.'
---

# Interview

Run the taste interview `/metacognition:design` scoped, and write the answers to `archive.md` as they happen.
Interview is the extractor, not the crafter.
It asks the person's actual taste questions; `interview-spec.md` already decided their shape, so this session never redesigns categories, floors, or seeds mid-interview.

## Arguments

- `[domain-slug]`: optional. The extraction to interview against; see Preflight for how it defaults.
- `--resume`: optionally continues an existing archive.
- `--extractions-root <dir>`: optionally overrides the extraction root.

## A Note Before Starting

Speaking your answers works well for this interview.
The archive keeps an answer exactly as given, hedges, false starts, and mid-answer corrections included, per extraction theory rule 11.
The one exception is capture-time codepoint normalization (see the Capture-Time Codepoint Normalization section below): dash and curly-quote characters get straightened to plain punctuation before an answer is appended.
Nothing else about an answer changes at capture.

## Read First

Read `references/extraction-theory.md` in full before asking the first question.
Every mechanic below, push-back on vague answers (rule 3), contradiction detection (rule 8), saturation (rule 10), interviewer drift (rule 12), traces back to a rule defined there; this skill does not re-derive them.
Then read the extraction's `interview-spec.md`, the category map, question seeds, artifact plan, and forced-choice bank it wrote are the material this session works from; interview never invents a category or a seed `design` did not already scope.

## Preflight

1. Read the arguments: `[domain-slug]` is optional; `--resume` optionally continues an existing archive; `--extractions-root <dir>` optionally overrides the default root.
2. Resolve settings and the extraction root.
Run `python3 scripts/resolve_config.py`, passing `--extractions-root <dir>` when that flag was given and `--set key=value` for any setting the person stated in the conversation or in Project instructions.
Read the JSON it prints, relay any `Loaded config from: <path>` line it printed, and state the root in one line: "Extraction root: `<path>`".
When the script cannot run (no code execution, or an interpreter older than Python 3.12), apply the same tiers by hand from `references/settings.md`, and say so in one line.
3. Resolve the slug: if `[domain-slug]` was passed, use it directly; if it was omitted, use the only extraction under the root and error if there are zero or several, naming each candidate slug in the error so the person can retry with one named.
4. Load `<extractions-root>/<slug>/interview-spec.md`.
Missing means there is nothing to interview against yet; stop and name `/metacognition:design <domain>` as the prerequisite.
5. Check `<extractions-root>/<slug>/archive.md`.
No `--resume` and no existing archive starts fresh at question 1.
No `--resume` and an existing archive with `status: in-progress` asks whether to resume or start over, as the opening move of the session rather than a silent overwrite.
`--resume` with no existing archive is a contradiction; say so and stop.
`--resume` with an existing archive runs the Resume Procedure below before the first new question.

## Register Check

Before the first question, read `registers` from `interview-spec.md`'s frontmatter and state them back to the person.
A single-register domain still gets this confirmation, never an assumed default, per extraction theory rule 9.
Every question and answer logged from here on carries a `[<register>]` tag in its heading, a single-register domain included, per `references/archive-format.md`'s fenced template; a question whose register is ambiguous, in a multi-register domain, gets asked before it gets logged, never guessed.

## The Interview Loop

1. **One probe or one battery per turn.**
A turn is either one open probe or one battery: three to six closed verdict items, all in a single category, each answerable with a stance and a sentence.
Two open probes never share a turn, because a batched open question gets answered as one and the second one's data is lost.
A battery never mixes categories.
Open probes lead early, while the map of the person's judgment is forming, and whenever an answer needs laddering.
Batteries take over once a category's shape is known and what remains is collecting verdicts.
A surprising battery answer earns an open follow-up.
A request for more concrete questions is a standing instruction for the rest of the interview.
Favor a concrete scenario over an abstract framing.
A canonical battery, in the `joinery` category:

> For each of these shop-built joints, would you ship it to a client as it is?
> 1. A half-blind dovetail with a visible gap under 1/32 inch.
> 2. A pocket-screwed face frame on a painted cabinet.
> 3. A butt joint reinforced with a dowel on a drawer back.

2. **Push back, never accept the first draft as final.**
A vague or hedged answer earns a contrast probe: show the quality done well and done lazily, per extraction theory rule 6.
An answer that is only an adjective earns an example demand: no answer stands as final until it is anchored to a concrete instance, per rule 3.
An "I don't know" earns one of three moves, whichever fits the moment: reframe the question from a different angle, approach it through a real artifact instead of a hypothetical (rule 7), or offer a forced choice between two concrete options (rule 4).

3. **Call out ledger contradictions immediately.**
Keep the running contradiction ledger extraction theory rule 8 describes.
The instant an answer conflicts with something already logged, name both claims and ask which wins, or whether the conflict is register-dependent (rule 9).
Never smooth two positions into a compromise the person never actually held; log the resolution, including `unresolved` when the interview closes before they settle it.

4. **Follow threads; category order is not fixed.**
When an answer opens an interesting thread outside the current category, follow it before returning to the seed list.
The archive's `### Qnn [<category>]` headings record categories exactly as they interleaved in the live conversation, never reorganized after the fact.

5. **Every 20 questions: one disconfirmation question, plus a one-line progress note.**
Re-read the ledger and the category tallies, then ask at least one question built to break an inferred pattern rather than confirm it further, per extraction theory rule 12.
Follow it with a spoken progress note reporting category coverage, register coverage, and the running count of research rounds, for example "42 questions; Mechanics and Crimes saturated; Hard nos and Red flags remaining; shop covered, client not yet; 2 research rounds," so the person always knows where the interview stands.

6. **Saturation per category.**
A category closes when three consecutive answers in it add no new constraint, provided its floor from `interview-spec.md`'s Category map is already met.
The floor guarantees minimum coverage; saturation, never the floor alone, decides when a category is actually done, per extraction theory rule 10.
Pass `--saturated` on the call that logs the closing answer.

7. **Artifact-grounded questions quote the excerpt inline.**
When a question draws on a real artifact from the interview spec's Artifact plan, quote the relevant excerpt directly inside the `**Q:**` line, so the archive is self-contained and a later reader never has to chase an external file to understand the question that was asked.

8. **Count probes, not turns.**
A category's `asked` tally counts probes: an open probe, a forced choice, or an evidence entry counts one, and a battery counts its items.
`questions_asked` still counts entries, and the README's `interview n/floor` cell shows probes over the floor sum and may exceed it.
`references/archive-format.md` holds the full rule, and the script applies it.

9. **Use the host's choice picker for closed choices.**
Forced choices, battery items the person answers by choosing, and research ratifications go through the host's choice picker, when the surface has one; otherwise write the same options as a lettered list.
Open probes never use it.
A picked answer logs the selected label verbatim plus any words the person added.
Option description text is the interviewer's, so it goes in the `**Q:**` line as part of the option, never in the `**A:**` line.

10. **Assign each question a register.**
A question with no register-specific content takes the primary register, the first in `registers`.
A register that surfaces mid-interview is raised with the person and added to the archive's `registers` only once they accept.

11. **Exports.**
When the person assigns a topic to another skill's territory, add an `--export` line on the call that logs that answer and move on.

## Live Research

When the person defers to outside practice ("look up what is standard", "I just do what the community does") or asks for research, research it in the same turn; a deferral is never banked for a later stage.
The request is the practice lookup shape in `references/research-contract.md`: one question about practice plus the person's stated lean in their words, and no domain statement.

- Where the surface loads plugin agents (Claude Code and Cowork), dispatch the `metacognition:domain-research` agent via the Agent tool with that request.
- Where it does not (claude.ai chat), run the same contract yourself in this session, following `references/research-contract.md`.
- With no web access, say so in one line, record the deferral under Open research as unresolved (`--research "(Q73): <what was deferred to>. Status: unresolved"`), and continue.

Present the bottom lines with their sources and ask the person to ratify, adjust, or reject each, through the choice picker per rule 9.
A deferral that committed in advance ("whatever the standard is, do that") is still presented and ratified.
On `no relevant results`, say so plainly and record the deferral as unresolved.
Log the outcome as its own `--probe evidence` entry: the `**Q:**` line carries the bottom lines with source links and the ratification question, and the `**A:**` line the person's reaction verbatim.
An evidence entry counts one probe in its category.
Research rounds have no cap.
When a later evidence entry settles an Open research line, edit that one line by hand to read `resolved in Qnn`; the script only appends.

## Capture Conventions

- When the person interrupts and dictates an answer again, the corrected dictation replaces the earlier answer; do not append a second one.
- A question the person did not understand is not logged; the reframed question that got an answer is the entry of record.
- Labels used in conversation may drift from archive numbers; the archive's contiguous numbering is authoritative.

## Fresh Start

On a fresh run, no `--resume` and no existing archive, write the archive skeleton to `<extractions-root>/<slug>/archive.md` before asking Q01: frontmatter per `references/archive-format.md`'s fenced template, with `categories` pre-populated from `interview-spec.md`'s Category map (every category name and its floor, `asked: 0`, `saturated: false`), `status: in-progress`, and an empty `## Contradiction ledger` and `## Questions` section.
The `## Open research` and `## Exports` sections are optional; the script adds each one the first time a line goes in.
This gives `--resume` a consistent file to reconstruct state from even if the session is killed before the first question is answered.

## Incremental Persistence

This is the load-bearing rule of the whole session: append each question and answer to `archive.md` as it happens, not at the end of a batch and never only in the session transcript.
The archive is the source of truth for the interview, per extraction theory rule 11 and `references/archive-format.md`; a killed session loses at most the one Q/A in flight when it died, nothing earlier.

Make one call per turn with `python3 scripts/archive_append.py <extractions-root>/<slug>`.
It appends the entry, assigns the next `Qnn`, updates `questions_asked` and the category's `asked`, and rewrites the README's `interview n/floor` cell, so the README updates as the interview happens, per `references/interview-spec-format.md`.
An open probe:

```bash
python3 scripts/archive_append.py extractions/woodworking --category joinery --register shop --probe ladder \
  --question "You said a joint should look intentional. What does that look like on a drawer front?" \
  --answer "Even reveals all the way around, and the grain running across the front like one board."
```

A battery (the question file is a stem line then items numbered `1.` to `n.`, the answer file is lines numbered the same way, and `1)` is refused):

```bash
python3 scripts/archive_append.py extractions/woodworking --category joinery --register shop \
  --probe battery --items 3 --question-file q.txt --answer-file a.txt
```

The script prints the assigned `Qnn`.
Optional flags on the same call: `--saturated` flips the category's flag, and `--ledger`, `--research`, and `--export` each append one line to that section, given as everything after the ID starting with "(": `--ledger '(Q07 vs Q23): "A" vs "B". Resolution: unresolved'`, `--export "(Q92): <topic> -> <destination>"`.
A section line cannot be added without logging an entry in the same call.
For a long or quote-heavy answer, the safe path is UTF-8 files passed with `--question-file` and `--answer-file`.
Any error exits 2 with one line and writes nothing; fix the cause and call again.

The archive format gives every non-battery entry a two-line body, so the script refuses a line break inside a question or answer.
When an answer arrives in several lines or paragraphs, log it as one line, replacing each line break with a single space and changing no word.

When the script cannot run (no code execution, or an interpreter older than Python 3.12), say so in one line and make one edit to `archive.md` that carries the entry body and the frontmatter counters together, then one edit to the README cell.
Write the entry in the shape `references/archive-format.md` fences: a `### Qnn [<category>] [<register>] [probe: <type>]` heading, then a bolded `**Q:**` line and a bolded `**A:**` line (the battery shape for a battery).
Never paraphrase the answer at capture; a hedge, a false start, or a mid-answer correction stays in the `**A:**` line exactly as spoken.

### Capture-Time Codepoint Normalization

The one edit interview makes to an answer before it lands in the archive (the script applies it, and by hand it is yours to apply): normalize dash codepoints (en dash, em dash) and curly-quote codepoints (curly single and double quotes) to their plain ASCII equivalents, hyphen and straight quotes.
This is transcription cleanup only, so the archive carries plain punctuation; it is not a content edit.
Words, word order, hedges, and garbled phrasing all stay exactly as given.
Nothing else about the answer changes: never fix grammar, never drop a false start, never tidy a run-on sentence.

## Resume Procedure

When `--resume` is passed against an existing `archive.md`, reconstruct state from the archive alone; never re-parse the full question history to rebuild what the frontmatter already tracks.

1. Read the frontmatter directly: `questions_asked` gives the next question number, and the `categories` map gives each category's running `asked`, `floor`, and `saturated` state.
2. Reconstruct the contradiction ledger from the `## Contradiction ledger` section as written; it is already the complete record, nothing to recompute.
3. Reconstruct the register tag state from the frontmatter's `registers` list, unchanged since interview start.
4. Confirm the last logged `### Qnn` heading matches `questions_asked` (a battery is one heading, so this check is about entries, not probes); a mismatch means the last write was interrupted mid-append, so the session continues from `questions_asked`, losing at most that one Q/A.
5. State the resumed position back to the person in one line, for example "Resuming at Q43; Mechanics and Crimes saturated; Hard nos and Red flags remaining," then continue the Interview Loop.

## Closing Questions

Once every category is saturated, or the person chooses to close the interview early, read `interview-spec.md`'s `## Closing questions` section and ask everything it lists: the three fixed closers verbatim first, never paraphrased and never reworded, then any domain-specific closer design appended after them, in the order the spec lists them.

1. "What did this interview miss?"
2. "If you could give one instruction that overrides everything else, what is it?"
3. "What did you learn about yourself answering this?"
4. Any domain-specific closer(s), verbatim as written in `interview-spec.md`.

Log each as its own `### Qnn [closing] [<register>] [probe: <type>]` entry per the same archive format, `<type>` being whichever probe pattern best fits how the question was actually asked, with `--closing` in place of `--category` on the call.
`[closing]` is the pseudo-category `references/archive-format.md` defines: it never increments any category's frontmatter tally and never appears in the frontmatter `categories` map.
Only after the LAST closer listed in the spec is logged, whether that is the third fixed closer or a later domain-specific one, set `status: complete` in the archive's frontmatter and edit the extraction README's `interview n/floor` cell one final time to mark it complete.

### Closing Self-Check

After setting `status: complete`, run `python3 scripts/validate_artifacts.py <extractions-root>/<slug>` against the just-completed extraction and resolve every finding it reports before telling the person the archive is done.
A finding here means the archive as written does not satisfy the structural contract `/metacognition:compile` will assume; fix it now, while the interview's own state is still loaded, rather than leaving it for compile to trip over.
When the script cannot run (no code execution, or an interpreter older than Python 3.12), say so in one line and check the same things by hand against `references/archive-format.md`: the frontmatter parses, the `### Qnn` numbering is contiguous from Q01 with no gap and no repeat, and each category's `asked` count matches the headings that carry it.

Tell the person the archive is complete and name `/metacognition:compile <domain-slug>` as the next stage, together with the file written, `<extractions-root>/<slug>/archive.md`; never run it automatically.
Then stop.

## Inputs and Outputs

- Reads: `references/settings.md` (to resolve settings by hand when the script cannot run); `references/extraction-theory.md` (always, first); `references/archive-format.md` (the fenced template this skill writes to); `references/interview-spec-format.md` (the format of the input `interview-spec.md` and the README status table); `references/research-contract.md` (the practice lookup shape for live research); `<extractions-root>/<slug>/interview-spec.md` (categories, floors, seeds, artifact plan, forced-choice bank, closing questions), a data path resolved against the extraction root.
- Scripts: `python3 scripts/resolve_config.py` resolves the settings, `python3 scripts/archive_append.py` writes each entry, and `python3 scripts/validate_artifacts.py` runs the closing self-check. All three import the sibling parser `scripts/yaml_subset.py`, which a skill never runs on its own.
- Writes: `<extractions-root>/<slug>/archive.md`, incrementally, one turn at a time; `<extractions-root>/<slug>/README.md`'s `interview n/floor` cell, updated alongside every archive append.
Both resolve against the extraction root, `extractions` under the working directory by default or the configured or passed root.
- Dispatches: the `metacognition:domain-research` agent for practice lookups, where the surface loads plugin agents, and nothing else.
Elsewhere the lookup runs in-session.

## What This Skill Never Does

- Never writes the compressed profile.
The interview ends when the archive is complete and `status: complete` is set; `/metacognition:compile` alone produces `profile.md`.
- Never paraphrases an answer at capture.
The only edit made to an answer is the codepoint normalization above, plus joining the lines of a multi-line answer into one with single spaces; compression is a separate, later, deliberate step that belongs to compile, never an accident of capture.
- Never redesigns the category map, floors, or seeds mid-interview.
Those decisions belong to `/metacognition:design`; if a category genuinely needs to change, the fix is a new or revised `interview-spec.md`, not a live edit during interview.
- Never banks a deferral to outside practice for a later stage.
It is researched in the same turn or recorded as unresolved open research.
- Never auto-chains into compile or any other pipeline stage.
The person runs `/metacognition:compile` on their own schedule; this session's completion is a `status: complete` archive on disk, nothing more.
- Never smooths a contradiction into a single resolved rule when the ledger cannot support one.
An `unresolved` entry is a legitimate outcome, not a defect to paper over.

## Resources

- [references/settings.md](references/settings.md): the five tiers and two keys, for resolving settings by hand.
- [references/extraction-theory.md](references/extraction-theory.md): the sixteen rules this skill applies at every question; read first, every run.
- [references/archive-format.md](references/archive-format.md): the frontmatter, contradiction ledger, and per-question fenced template this skill writes to.
- [references/interview-spec-format.md](references/interview-spec-format.md): the format of the input `interview-spec.md` this skill reads, and the extraction README status table this skill updates.
- [references/research-contract.md](references/research-contract.md): the practice lookup request and output shapes for live research.
- [scripts/resolve_config.py](scripts/resolve_config.py), [scripts/archive_append.py](scripts/archive_append.py), and [scripts/validate_artifacts.py](scripts/validate_artifacts.py): the settings resolver, the entry writer, and the structural validator; each imports [scripts/yaml_subset.py](scripts/yaml_subset.py).
