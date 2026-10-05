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

You answer one turn at a time.
A turn is either one open question or one short battery: three to six closed verdict items, all in one category, each answerable with a stance and a sentence.
Two open questions never share a turn, and a battery never mixes categories.
Open questions lead early, while the map of your judgment is forming, and whenever an answer needs a follow-up.
Batteries take over once a category's shape is known.
A surprising battery answer earns an open follow-up.
If you ask for more concrete questions, that holds for the rest of the interview.

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
The note reports category coverage, register coverage, and the running count of research rounds.
At the end it asks the three closing questions.

### Choices

Closed choices go through your host's choice picker when the surface has one.
That covers forced choices, battery items you answer by choosing, and research ratifications.
Where the surface has no picker, the same options appear as a lettered list.
Open questions never use it.
A picked answer is logged as the label you selected, plus any words you add.

### Research in the Same Turn

When you defer to outside practice, such as "look up what is standard", or ask for research, interview researches it in the same turn.
It never saves a deferral for a later stage.
It shows you the bottom lines with their sources and asks you to ratify, adjust, or reject each.
Your reaction is logged as its own entry in the archive.
There is no cap on research rounds.

Interview uses the plugin's research agent where the surface loads plugin agents.
Elsewhere it runs the same research in the conversation.
With no web access, interview says so, records the deferral as unresolved open research, and continues.
When the research returns nothing relevant, it says so and records the deferral as unresolved.

### Exports

When you assign a topic to another skill's territory, interview records it as an export and moves on.
[Compile](compile.md) keeps exports out of the profile, and [skillify](skillify.md) lists them as follow-up work.

## What It Produces

- `<root>/<slug>/archive.md`, written one entry at a time. See [archive.md](../formats/archive.md).
  It can also hold research findings with their source links, and a list of topics you assigned to other skills.
- The `interview n/floor` cell of the extraction README, updated with every answer.

## How Long It Takes

No source gives a duration in minutes.
The size of the work is defined in questions.
An interview typically runs 60 to 120 questions across all categories.
Each category has a floor, a minimum count of probes, and stops when it saturates: three consecutive answers add no new constraint.
An open question, a forced choice, or a research entry counts one probe, and a battery counts its items.
The floor guarantees coverage, and saturation decides when a category is done.
Plan on hours of your own time rather than minutes, and expect the total to vary with the domain and with how much you have to say.

You can stop and come back.
Each entry is saved as it is answered, so a killed session loses at most the one in flight.
`--resume` reads the archive's frontmatter and continues from the last question.

## What Done Looks Like

Every category is saturated, or you closed the interview early.
The closing questions are logged, and the archive's `status` is `complete`.
Interview then runs the structure check on the extraction and fixes every finding.
It names `archive.md` and `/metacognition:compile <slug>`, and then stops.

Interview needs `interview-spec.md` to exist.
If it does not, interview stops and names `/metacognition:design <domain>`.
