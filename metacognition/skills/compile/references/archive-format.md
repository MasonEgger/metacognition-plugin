# Archive Format

`archive.md` is the pipeline's running record of the interview: every question asked, every answer given, and every contradiction the interviewer catches along the way.
`/metacognition:interview` writes it incrementally, one question at a time, per extraction theory rule 11's verbatim-capture discipline; it is the source of truth for the interview, never the session transcript.
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

## Questions
### Q01 [<category>] [<register>] [probe: <type>]
**Q:** <question, with any artifact excerpt inline>
**A:** <verbatim answer>
```

## Frontmatter Fields

- `domain`: the same slug as `interview-spec.md`'s frontmatter, so the two files are unambiguously paired.
- `registers`: copied from the interview spec at interview start; unchanged for the life of the archive.
- `questions_asked`: the running total of questions logged, updated after every question, not just at the end of the session.
- `categories`: a map from category name to its own running tally, `asked`, `floor`, and `saturated`.
  `asked` and `saturated` update after every question in that category; `floor` is copied from the interview spec's Category map and does not change during the interview.
- `status`: `in-progress` while the interview is still running, `complete` once every category is saturated (or the interview was deliberately closed early) and no further questions are expected.

The frontmatter `categories` counts are the interviewer's own running tally, not a value recomputed from the body on every write.
This is what makes `--resume` cheap: on resume, interview reads the frontmatter, reconstructs the ledger and the per-category counts from it directly, and continues from the last question, rather than re-parsing the entire question history to rebuild state that was already being tracked.
`python3 scripts/validate_artifacts.py` is the independent check that this running tally still matches the body: it recounts the actual `### Qnn` headings per category and flags a frontmatter that has drifted from what the archive body actually contains.

## Contradiction Ledger

Per extraction theory rule 8, the ledger holds every conflict the interviewer catches between a stated rule and an observed exception, surfaced the moment it appears rather than smoothed into a compromise the person never held.
Each entry is a single line: an ID (`L01`, `L02`, ...), the pair of question numbers in tension, the two claims in the person's own words, and a resolution.
The resolution is one of three shapes: which claim wins outright, a note that the tension is register-dependent (both claims are true, in different contexts, per rule 9), or `unresolved`, when the interview closed before the person settled it.
An `unresolved` entry is not a defect in the archive; compile reads it and, per extraction theory rule 1, may record it downstream as a productive contradiction rather than forcing a resolution the interview never earned.

## Questions

Questions are logged in the order they were asked, under a heading with a fixed shape: `### Qnn [<category>] [<register>] [probe: <type>]`, where `Qnn` is the global question number, zero-padded, `<category>` matches a category name from the interview spec's Category map, `<register>` names which register the question belongs to, and `<type>` is the probe pattern used (`forced-choice`, `ladder`, `contrast`, `artifact`, `critical-incident`, or `triad`).
The `[<register>]` tag is always written, even in a single-register archive; a heading never drops the bracket just because there is only one register to name.

`[closing]` is a pseudo-category, written in the same `<category>` bracket position for every closing question logged per the Closing Questions convention.
It is never counted in the frontmatter `categories` tally (the three fixed closers, and any domain-specific closer, are not part of category saturation) and it never appears in the frontmatter `categories` map at all.
`/metacognition:skillify` excludes `[closing]` when it derives its section map from the archive's `### Qnn [<category>]` headings, since a closing question belongs to no category the interview spec scoped.

Question numbers are global and continuous across the whole interview, never restarted per category.
Because saturation, not a fixed order, decides when a category is done, categories interleave in the archive exactly as they were asked.
A reader scanning `### Qnn` headings in order sees the interview as it actually happened, threads and all, not a category-sorted reorganization of it.

Each question's body is exactly two lines: a bolded `**Q:**` line carrying the question as asked, with any grounding artifact excerpt inlined directly into the question text per extraction theory rule 7, and a bolded `**A:**` line carrying the answer exactly as given.
Nothing else goes in a question entry.
Interview never paraphrases at capture, per extraction theory rule 11; a hedge, a false start, or a mid-answer correction stays in the `**A:**` line exactly as spoken, because compile is where compression happens, deliberately and later, never by accident at the moment of capture.

`/metacognition:skillify` derives its section map for the produced or augmented skill by reading every `### Qnn [<category>]` heading in the archive and grouping by category, which is why the heading shape is load-bearing: a category name that does not exactly match the interview spec's Category map, or a heading missing the bracketed category, breaks that derivation.
`python3 scripts/validate_artifacts.py` checks the `Qnn` numbering is contiguous with no gaps and no repeats, independent of whether compile or skillify has run yet.
