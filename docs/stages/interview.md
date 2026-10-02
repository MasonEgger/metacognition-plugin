# Interview

```text
/metacognition:interview [domain-slug]
```

Interview asks the taste questions that [design](design.md) scoped, and writes `archive.md` as the answers come in.
It never redesigns the categories, floors, or seeds mid-interview.

## Arguments

- `[domain-slug]`: the extraction to interview against. Optional, and defaults to the only extraction under the root.
- `--resume`: continues an existing archive.
- `--extractions-root <dir>`: overrides the extraction root for this run.

## What It Asks of You

You answer, one question at a time.
Speaking your answers works well.
The archive keeps each answer exactly as given, hedges, false starts, and mid-answer corrections included.
The only edit is that dash and curly-quote characters are straightened to a hyphen and straight quotes.

Expect pushback.
A vague answer gets a request to show the quality done well and done lazily.
An answer that is only an adjective gets a request for a concrete example.
If you say "I don't know," interview reframes the question, approaches it through a real artifact, or offers a forced choice between two concrete options.
When an answer contradicts an earlier one, interview names both claims at once and asks which wins, or whether the difference depends on context.

Before the first question, interview reads your registers back to you and confirms them.
Every 20 questions it asks at least one question built to break a pattern it thinks it has found, followed by a one-line progress note.
At the end it asks the three closing questions.

## What It Produces

- `<root>/<slug>/archive.md`, written one question at a time. See [archive.md](../formats/archive.md).
- The `interview n/floor` cell of the extraction README, updated with every answer.

## How Long It Takes

No source gives a duration in minutes.
The size of the work is defined in questions.
An interview typically runs 60 to 120 questions across all categories.
Each category has a floor, a minimum question count, and stops when it saturates: three consecutive answers add no new constraint.
The floor guarantees coverage, and saturation decides when a category is done.
Plan on hours of your own time rather than minutes, and expect the total to vary with the domain and with how much you have to say.

You can stop and come back.
Each question is saved as it is answered, so a killed session loses at most the one question in flight.
`--resume` reads the archive's frontmatter and continues from the last question.

## What Done Looks Like

Every category is saturated, or you closed the interview early.
The closing questions are logged, and the archive's `status` is `complete`.
Interview then runs the structure check on the extraction and fixes every finding.
It names `archive.md` and `/metacognition:compile <slug>`, and then stops.

Interview needs `interview-spec.md` to exist.
If it does not, interview stops and names `/metacognition:design <domain>`.
