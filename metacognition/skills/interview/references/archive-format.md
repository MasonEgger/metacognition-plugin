# Archive Format

`archive.md` is the pipeline's running record of the interview: every question asked, every answer given, and every contradiction the interviewer catches along the way.
`/metacognition:interview` writes it incrementally, one entry at a time (a battery is one entry), per extraction theory rule 11's verbatim-capture discipline; it is the source of truth for the interview, never the session transcript.
`/metacognition:compile` reads it to produce `profile.md`; `/metacognition:skillify` reads its `### Qnn [<category>]` headings to derive a section map for the produced skill.

## The Fenced Template

```markdown
---
domain: <slug>
registers: [...]
questions_asked: N
categories: {<category>: {asked: n, floor: m, saturated: true|false}}
status: in-progress|complete
---

# Archive: <title>

## Contradiction ledger
- L01 (Q07 vs Q23): "<claim A>" vs "<claim B>". Resolution: <which wins / register-dependent / unresolved>

## Open research
- R01 (Q73): <what the person deferred to>. Status: unresolved | resolved in Q74

## Exports
- E01 (Q92): <topic> -> <destination skill or unassigned>

## Questions
### Q01 [<category>] [<register>] [probe: <type>]
**Q:** <question, with any artifact excerpt inline>
**A:** <verbatim answer>

### Q02 [<category>] [<register>] [probe: battery] [items: 3]
**Q:** <stem>
1. <item>
2. <item>
3. <item>
**A:**
1. <verbatim answer>
2. <verbatim answer>
3. <verbatim answer>

### Q03 [<category>] [<register>] [probe: evidence]
**Q:** <bottom lines with source links, and the ratification question>
**A:** <verbatim reaction>
```

`## Open research` and `## Exports` are optional.
An archive carries each one only once it has a line to put there, and an archive with neither section is complete and valid.
When present, they sit in the order shown: after the ledger, before `## Questions`.

## Frontmatter Fields

- `domain`: the same slug as `interview-spec.md`'s frontmatter, so the two files are unambiguously paired.
- `registers`: copied from the interview spec at interview start.
  A register that surfaces mid-interview may be added once the person accepts it; the interviewer raises it with the person first and never adds one silently.
- `questions_asked`: the running total of `### Qnn` entries logged, updated after every entry, not just at the end of the session.
  A battery is one entry, so it raises this count by one.
- `categories`: a map from category name to its own running tally, `asked`, `floor`, and `saturated`.
  `asked` counts probes, not entries: a battery counts its items, and every other entry (an open probe, a forced choice, an evidence entry) counts one.
  `asked` and `saturated` update after every entry in that category; `floor` is copied from the interview spec's Category map and does not change during the interview.
- `status`: `in-progress` while the interview is still running, `complete` once every category is saturated (or the interview was deliberately closed early) and no further questions are expected.

The frontmatter `categories` counts are the interviewer's own running tally, not a value recomputed from the body on every write.
This is what makes `--resume` cheap: on resume, interview reads the frontmatter, reconstructs the ledger and the per-category counts from it directly, and continues from the last question, rather than re-parsing the entire question history to rebuild state that was already being tracked.
`python3 scripts/validate_artifacts.py` is the independent check that this running tally still matches the body: it recounts the actual probes per category (each heading counts one, except a battery, which counts its `[items: n]` tag) and flags a frontmatter that has drifted from what the archive body actually contains.

## Contradiction Ledger

Per extraction theory rule 8, the ledger holds every conflict the interviewer catches between a stated rule and an observed exception, surfaced the moment it appears rather than smoothed into a compromise the person never held.
Each entry is a single line: an ID (`L01`, `L02`, ...), the pair of question numbers in tension, the two claims in the person's own words, and a resolution.
The resolution is one of three shapes: which claim wins outright, a note that the tension is register-dependent (both claims are true, in different contexts, per rule 9), or `unresolved`, when the interview closed before the person settled it.
An `unresolved` entry is not a defect in the archive; compile reads it and, per extraction theory rule 1, may record it downstream as a productive contradiction rather than forcing a resolution the interview never earned.

## Open Research

The optional `## Open research` section holds one line per deferral to outside practice that could not be researched in the same turn: `- R01 (Q73): <what the person deferred to>. Status: unresolved | resolved in Q74`.
IDs run `R01`, `R02`, ... with no gaps.
The status is `unresolved` while nothing was found or no research was possible, and `resolved in Qnn` once an evidence entry settled it.
The interviewer writes the lines during the interview, like the ledger.
Compile reads them and lists each `unresolved` line as not yet settled; it never turns one into an instruction.

## Exports

The optional `## Exports` section holds one line per topic the person voiced taste about but assigned to a different skill's territory: `- E01 (Q92): <topic> -> <destination skill or unassigned>`.
The destination is a skill name the person gave, or `unassigned` when they named none.
IDs run `E01`, `E02`, ... with no gaps.
The interviewer writes the lines during the interview, like the ledger.
Compile leaves export content out of the profile body and copies the list into `compile-log.md`; skillify names the exports as follow-up work in its finish message and never writes them into the produced skill.

## Questions

Questions are logged in the order they were asked, under a heading with a fixed shape: `### Qnn [<category>] [<register>] [probe: <type>]`, where `Qnn` is the global question number, zero-padded, `<category>` matches a category name from the interview spec's Category map, `<register>` names which register the question belongs to, and `<type>` is the probe pattern used (`forced-choice`, `ladder`, `contrast`, `artifact`, `critical-incident`, `triad`, `battery`, or `evidence`).
The `[<register>]` tag is always written, even in a single-register archive; a heading never drops the bracket just because there is only one register to name.

`[closing]` is a pseudo-category, written in the same `<category>` bracket position for every closing question logged per the Closing Questions convention.
It is never counted in the frontmatter `categories` tally (the three fixed closers, and any domain-specific closer, are not part of category saturation) and it never appears in the frontmatter `categories` map at all.
`/metacognition:skillify` excludes `[closing]` when it derives its section map from the archive's `### Qnn [<category>]` headings, since a closing question belongs to no category the interview spec scoped.

A battery heading carries one more tag after the probe tag: `[probe: battery] [items: n]`, with n from 3 to 6.
An `[items: n]` tag on any other probe type is an error.
An evidence entry records researched practice presented to the person: the `**Q:**` line carries the bottom lines with their source links and the ratification question, and the `**A:**` line carries the person's reaction verbatim.

Question numbers are global and continuous across the whole interview, never restarted per category.
Because saturation, not a fixed order, decides when a category is done, categories interleave in the archive exactly as they were asked.
A reader scanning `### Qnn` headings in order sees the interview as it actually happened, threads and all, not a category-sorted reorganization of it.

Every entry other than a battery has a two-line body, and a battery body has the shape below.
A battery is three to six closed items, all in one category, and the entry is logged once: the stem on the `**Q:**` line, then n numbered items, then a bare `**A:**` line, then n numbered answers in the same order.

```markdown
### Q12 [joinery] [shop] [probe: battery] [items: 3]
**Q:** For each of these shop-built joints, would you ship it to a client as it is?
1. A half-blind dovetail with a visible gap under 1/32 inch.
2. A pocket-screwed face frame on a painted cabinet.
3. A butt joint reinforced with a dowel on a drawer back.
**A:**
1. Yes. Under a thirty-second I will not touch it.
2. Yes, painted is the only place I allow it.
3. No. A drawer back gets a rabbet or I redo it.
```

Each other question's body is exactly two lines: a bolded `**Q:**` line carrying the question as asked, with any grounding artifact excerpt inlined directly into the question text per extraction theory rule 7, and a bolded `**A:**` line carrying the answer exactly as given.
Nothing else goes in an entry.
Interview never paraphrases at capture, per extraction theory rule 11; a hedge, a false start, or a mid-answer correction stays in the `**A:**` line exactly as spoken, because compile is where compression happens, deliberately and later, never by accident at the moment of capture.

`/metacognition:skillify` derives its section map for the produced or augmented skill by reading every `### Qnn [<category>]` heading in the archive and grouping by category, which is why the heading shape is load-bearing: a category name that does not exactly match the interview spec's Category map, or a heading missing the bracketed category, breaks that derivation.
`python3 scripts/validate_artifacts.py` checks the `Qnn` numbering is contiguous with no gaps and no repeats, independent of whether compile or skillify has run yet.

## Provenance and Capture Conventions

A picked answer, one chosen through the host's choice picker, is logged as the selected label verbatim, followed by any words the person added, verbatim.
Option description text belongs to the interviewer, so it is written into the `**Q:**` line as part of the option and never into the `**A:**` line.

A few conventions keep the record honest:

- When the person interrupts and dictates an answer again, the corrected dictation replaces the earlier answer in the entry.
- A question the person did not understand is not logged.
  The reframed question that got an answer is the entry of record.
- Labels used in conversation may drift.
  The archive's contiguous numbering is authoritative.
