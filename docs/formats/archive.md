# archive.md

`archive.md` is the running record of the interview: every question asked, every answer given, and every contradiction the interviewer catches.
[Interview](../stages/interview.md) writes it incrementally, one question at a time, and it is the source of truth for the interview.
The conversation transcript is not.
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

## Questions
### Q01 [<category>] [<register>] [probe: <type>]
**Q:** <question, with any artifact excerpt inline>
**A:** <verbatim answer>
```

## Frontmatter Fields

- `domain`: the same slug as `interview-spec.md`, so the two files are paired.
- `registers`: copied from the interview spec at interview start, and unchanged for the life of the archive.
- `questions_asked`: the running total of questions logged, updated after every question.
- `categories`: a map from category name to its own running tally of `asked`, `floor`, and `saturated`.
  `asked` and `saturated` update after every question in that category.
  `floor` is copied from the interview spec's category map and does not change.
- `status`: `in-progress` while the interview is running, `complete` once every category is saturated (or the interview was deliberately closed early) and no further questions are expected.

The `categories` counts are the interviewer's own running tally, not a value recomputed from the body on every write.
That is what makes `--resume` cheap: interview reads the frontmatter and continues from the last question.
The structure check is the independent test that the tally still matches the body.
It recounts the actual `### Qnn` headings per category and flags a frontmatter that has drifted.

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

## Questions

Questions are logged in the order they were asked, under a heading with a fixed shape: `### Qnn [<category>] [<register>] [probe: <type>]`.

- `Qnn` is the global question number, zero-padded.
- `<category>` matches a category name from the interview spec's category map.
- `<register>` names which register the question belongs to.
  The tag is always written, even in a single-register archive.
- `<type>` is the probe pattern used: `forced-choice`, `ladder`, `contrast`, `artifact`, `critical-incident`, or `triad`.

`[closing]` is a pseudo-category, written in the `<category>` position for every closing question.
It is never counted in the `categories` tally and never appears in the `categories` map.
Skillify excludes it when it derives a section map.

Question numbers are global and continuous across the whole interview, and never restart per category.
Because saturation decides when a category is done, categories interleave in the archive exactly as they were asked.

Each entry's body is exactly two lines: a bolded `**Q:**` line carrying the question as asked, with any grounding artifact excerpt inlined into the question text, and a bolded `**A:**` line carrying the answer exactly as given.
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
