# archive.md

`archive.md` is the running record of the interview: every question asked, every answer given, and every contradiction the interviewer catches.
[Interview](../stages/interview.md) writes it incrementally, one entry at a time (a battery is one entry), and it is the source of truth for the interview.
The conversation transcript is not.
Interview appends each entry with `scripts/archive_append.py`, which updates the counts and the README cell in the same call.
Where the script cannot run, interview makes the same edits by hand.
[Compile](../stages/compile.md) reads it to produce `profile.md`.
[Skillify](../stages/skillify.md) reads its `### Qnn [<category>]` headings to derive a section map for the produced skill.

## Template

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

Open research and Exports are optional.
An archive gets each one only once it has a line to put there, and an archive with neither is complete and valid.
When present, they sit in the order shown, after the ledger and before the questions.

## Frontmatter Fields

- `domain`: the same slug as `interview-spec.md`, so the two files are paired.
- `registers`: copied from the interview spec at interview start.
  A register that surfaces mid-interview may be added once you accept it.
  The interviewer raises it with you first and never adds one silently.
- `questions_asked`: the running total of `### Qnn` entries logged, updated after every entry.
  A battery is one entry, so it raises this count by one.
- `categories`: a map from category name to its own running tally of `asked`, `floor`, and `saturated`.
  `asked` counts probes, not entries.
  A battery counts its items, and every other entry (an open probe, a forced choice, an evidence entry) counts one.
  `asked` and `saturated` update after every entry in that category.
  `floor` is copied from the interview spec's category map and does not change.
- `status`: `in-progress` while the interview is running, `complete` once every category is saturated (or the interview was deliberately closed early) and no further questions are expected.

The `categories` counts are the interviewer's own running tally, not a value recomputed from the body on every write.
That is what makes `--resume` cheap: interview reads the frontmatter and continues from the last question.
The structure check is the independent test that the tally still matches the body.
It recounts the actual probes per category and flags a frontmatter that has drifted.

## Contradiction Ledger

The ledger holds every conflict the interviewer catches between a stated rule and an observed exception, per [rule 8](../method.md#8-contradiction-detection).
Each entry is a single line: an ID (`L01`, `L02`, ...), the pair of question numbers in tension, the two claims in your own words, and a resolution.
The resolution is one of three shapes:

- which claim wins outright;
- a note that the tension depends on context, so both claims are true in different contexts (see [rule 9](../method.md#9-register-separation));
- `unresolved`, when the interview closed before you settled it.

An `unresolved` entry is not a defect.
Compile may record it downstream as a productive contradiction instead of forcing a resolution the interview never earned.

Entry from the synthetic woodworking fixture:

```markdown
- L01 (Q03 vs Q05): "I never use pocket screws on anything that will be seen" vs "This jig has three pocket screws and I have never once cared." Resolution: register-dependent (never on furniture, always on shop jigs).
```

## Open Research

The optional Open research section holds one line per deferral to outside practice that could not be researched in the same turn.
Each line has an ID (`R01`, `R02`, ...), the question where the deferral happened, what you deferred to, and a status: `unresolved`, or `resolved in Qnn` once an evidence entry settled it.
The interviewer writes the lines during the interview.
Compile reads them and lists each unresolved one as not yet settled.
It never turns one into an instruction.

## Exports

The optional Exports section holds one line per topic you voiced taste about but assigned to a different skill's territory.
Each line has an ID (`E01`, `E02`, ...), the question, the topic, and a destination: the skill you named, or `unassigned`.
The interviewer writes the lines during the interview.
Compile leaves export content out of the profile and copies the list into `compile-log.md`.
Skillify names the exports as follow-up work in its finish message and never writes them into the produced skill.

## Questions

Questions are logged in the order they were asked, under a heading with a fixed shape: `### Qnn [<category>] [<register>] [probe: <type>]`.

- `Qnn` is the global question number, zero-padded.
- `<category>` matches a category name from the interview spec's category map.
- `<register>` names which register the question belongs to.
  The tag is always written, even in a single-register archive.
- `<type>` is the probe pattern used: `forced-choice`, `ladder`, `contrast`, `artifact`, `critical-incident`, `triad`, `battery`, or `evidence`.

`[closing]` is a pseudo-category, written in the `<category>` position for every closing question.
It is never counted in the `categories` tally and never appears in the `categories` map.
Skillify excludes it when it derives a section map.

A battery heading carries one more tag after the probe tag: `[probe: battery] [items: n]`, with n from 3 to 6.
An `[items: n]` tag on any other probe type is an error.
An evidence entry records researched practice shown to you: the question line carries the findings with their source links and the ratification question, and the answer line carries your reaction as you gave it.

Question numbers are global and continuous across the whole interview, and never restart per category.
Because saturation decides when a category is done, categories interleave in the archive exactly as they were asked.

A battery is three to six closed items, all in one category, logged as one entry: the stem on the question line, n numbered items, a bare answer line, then n numbered answers in the same order.
Every other entry's body is exactly two lines: a bolded `**Q:**` line carrying the question as asked, with any grounding artifact excerpt inlined into the question text, and a bolded `**A:**` line carrying the answer exactly as given.
Nothing else goes in an entry.
Interview never paraphrases at capture, per [rule 11](../method.md#11-verbatim-capture).
A hedge, a false start, or a mid-answer correction stays in the `**A:**` line as spoken.
The one normalization is that dash and curly-quote characters are straightened to a hyphen and straight quotes.

The heading shape is load-bearing.
A category name that does not exactly match the interview spec's category map, or a heading missing the bracketed category, breaks the skillify section map.
The structure check confirms the `Qnn` numbering is contiguous, with no gaps and no repeats.

Entry from the synthetic woodworking fixture:

```markdown
### Q01 [joinery] [shop] [probe: forced-choice]
**Q:** Here are two identical toolboxes, one mitered and glued, one butt-jointed and pinned. Which one ships to a client, and why?
**A:** The butt-jointed one ships. A miter looks sharp until it sees a shop floor, and a pin holds under racking in a way glue alone will not. I would rather hand over something that survives being dropped off a tailgate than something that photographs well in the shop.
```

Battery from the same fixture's persona:

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

## Provenance and Capture Conventions

A picked answer, one chosen through the host's choice picker, is logged as the selected label verbatim, followed by any words you added.
Option description text belongs to the interviewer, so it goes into the question line as part of the option and never into the answer line.

A few conventions keep the record honest:

- When you interrupt and dictate an answer again, the corrected dictation replaces the earlier answer.
- A question you did not understand is not logged.
  The reframed question that got an answer is the entry of record.
- Labels used in conversation may drift.
  The archive's contiguous numbering is authoritative.
