# Design

```text
/metacognition:design <domain>
```

Design plans the interview.
It is the crafter, not the interviewer, and it never asks you a taste question.
Every question it asks is about the shape of the interview to come, never about your judgment in the domain.
That boundary lets you review the plan before you spend any interview time against it.

## Arguments

- `<domain>`: the domain statement. Required.
- `--target <plugin>:<skill>`: names an existing skill the extraction will augment.
- `--extractions-root <dir>`: overrides the extraction root for this run.

## What It Asks of You

Design resolves your settings, states the extraction root, derives the domain slug, and prints it back so a bad derivation is caught at once.
If `interview-spec.md` already exists for that slug, design asks whether to overwrite it or restate the domain.

Then it asks scoping questions, one at a time:

- The domain in one sentence.
- Which registers the profile must cover. A domain with one register still gets an explicit answer.
- What artifacts exist and where, such as repositories, documents, and past decisions.
- Who consumes the profile: which future skill, and what it must let Claude do.
- Whether a skill already exists for this domain.

Design records your answers verbatim.

After scoping it runs research on the domain and shows you the dimensions, schools of thought, vocabulary, and artifact types it found, as one list.
You can drop or add entries.
It then names three to five dimensions you may have taste about but did not raise, and you mark each as engaged or declined.

Before it writes the artifact plan, design checks that each local artifact path exists and holds real content.
A missing path, or a directory or document that holds only scaffolding, is recorded as unavailable with the reason, and design tells you at once so you can supply another.
Where the surface has no file access, design says the paths could not be checked.
An unavailable path counts as no artifact when design sets `artifacts_available`.

Every register you named must be targeted by at least one category in the category map.
When one is not, design raises it with you and either adds questions that target it or drops the register, before it writes anything.

Before writing anything, it closes every open question, so the finished spec has no open questions in it.

## What It Produces

- `<root>/<slug>/interview-spec.md`: the category map, question seeds, artifact plan, forced-choice bank, and closing questions. See [interview-spec.md](../formats/interview-spec.md).
- `<root>/<slug>/README.md`: the extraction status table, with only the `design` cell filled.

## How Long It Takes

No source gives a duration for this stage, and it varies with the domain and with how much you have to say about it.
The size of the work is one scoping question at a time, a research step, and a review of the plan.
The research step needs web access.
Without it, design says so and continues from your scoping answers alone.

## What Done Looks Like

`interview-spec.md` and the extraction `README.md` exist under `<root>/<slug>/`.
Design names both files and `/metacognition:interview <slug>`, and then stops.
Design never starts the interview.
It never decides augment versus replace either; it records the `target_skill` and leaves that call to [skillify](skillify.md).
