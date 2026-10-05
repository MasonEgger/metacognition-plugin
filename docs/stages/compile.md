# Compile

```text
/metacognition:compile [domain-slug]
```

Compile compresses a finished archive into `profile.md`.
It is the compressor, not the interviewer.
It reads the whole archive and decides what survives, and it never asks a new taste question.

## Arguments

- `[domain-slug]`: the extraction to compile. Optional, and defaults to the only extraction under the root.
- `--extractions-root <dir>`: overrides the extraction root for this run.

## What It Asks of You

Very little.
Compile runs in the conversation, so you can answer a clarifying question about material already in the archive, such as an ambiguous line or a cut that needs your confirmation.
It never asks a question that would extend the interview.

Compile refuses an archive whose `status` is `in-progress`.
It tells you to run `/metacognition:interview <slug> --resume` first.

## What It Produces

- `<root>/<slug>/profile.md`: seventeen sections in a fixed order. See [profile.md](../formats/profile.md).
- `<root>/<slug>/compile-log.md`: one entry for every line it cut, with the source question and the reason, then an `## Exports` list copied from the archive.
- The `compile tokens` cell of the extraction README.

The profile body targets 2,000 to 4,000 tokens for a single register, more for several, with a hard ceiling of 10,000.
The ceiling guards against padding; a line that passes the keep/cut test is never cut to make a number.
A line is kept only if removing it would change how a downstream system writes, judges, edits, refuses, or decides something.
Biography and flattering self-description are cut.
Conflicts between what you said and what the archive shows become tension entries, and compile never resolves one for you.
The new profile starts with `calibrated: false`.

Some archive content is handled on its own terms:

- A ratified practice, which is a researched practice you agreed to, compiles to the written practice with its citation.
  Compile never writes a bare instruction to follow community practice.
- Exports, which are topics you assigned to another skill, stay out of the profile body.
  They go to the compile log.
- An open research line still marked unresolved is listed in the profile as not yet settled.

Compile keeps the profile's `token_estimate` current with `scripts/update_token_estimate.py`.
The script counts the body in characters divided by four and rewrites the line when it is stale.
When the script cannot run, compile computes the same figure by hand.

## How Long It Takes

No source gives a duration.
The input is the whole archive, which the skill describes as running 20,000 to 30,000 tokens.
The work varies with the archive.

## What Done Looks Like

`profile.md` and `compile-log.md` exist, and the structure check reports no findings.
Compile reports its token estimate and section count.
Read the compile log once.
Anything cut that you want back can be rescued from it.
Compile names both files and `/metacognition:calibrate <slug>`, and then stops.
It never edits `archive.md`.
