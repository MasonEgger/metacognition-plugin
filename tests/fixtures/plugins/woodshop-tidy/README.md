<!-- Synthetic fixture plugin for the metacognition pipeline tests. Not a real plugin. -->

# Woodshop Tidy (fixture)

A fixture plugin whose one skill is well structured on purpose.
Do not degrade it.

- The description is third person and names the phrases a user would say.
- `SKILL.md` is a few hundred words in imperative form.
- The detail lives in one file under `references/`, and `SKILL.md` points at it by relative path.
- An Additional Resources section names that file.

`/metacognition:skillify` in augment mode should assess this structure, say in one line that it holds, and continue on the diff path.
It should propose no restructure.
The sibling fixture `woodshop-sprawl` is the target whose structure is challenged, and `woodshop` is the minimal stub.
