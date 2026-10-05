<!-- Synthetic fixture plugin for the metacognition pipeline tests. Not a real plugin. -->

# Woodshop Sprawl (fixture)

A fixture plugin whose one skill is badly structured on purpose.
The defects are deliberate, so do not fix them.

- The description is one vague line with no trigger phrases and no statement of when to use the skill.
- `SKILL.md` is a single file of about 1,600 words that inlines joinery rules, a finishing schedule, a safety checklist, jig notes, and lumber sourcing.
- There is no `references/` directory, so nothing is loaded on demand.

`/metacognition:skillify` in augment mode should assess this structure, report these findings, and present an alternative layout beside keep-as-is.
It should draft no diff until the person chooses.
The sibling fixture `../woodshop/` is the minimal target; this one is the target whose structure is challenged.
