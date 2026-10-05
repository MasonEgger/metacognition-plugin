# Session: Step 11, Ground Skillify in the Provider Baseline

## Summary

Skillify's knowledge of skill-making was entirely internal: its scaffold and an optional exemplar.
A new skill's description was therefore written without the provider's guidance on triggering, and augment kept an existing skill's structure even when it was poor.
Step 11 makes skillify consult the plugin-dev baseline when it is installed and puts keep-or-restructure to the person before any diff.
The skillify body went from about 2,800 to about 3,090 words by the executor's count (the validator counted about 3,265 with a different method).

## What Changed

- `metacognition/skills/skillify/SKILL.md`: skillify loads the plugin-dev baseline first.
- Every use of plugin-dev carries a fallback, and claude.ai chat is named as a surface where the fallback is the normal path.
- A missing exemplar is now skipped with no message.
- The precedence order is stated once.
- Augment gives its structural assessment before any diff.
- A restructure applies only on the person's explicit choice, through a reviewed diff.
- Dry-run shows the assessment and applies nothing.
- The finish message lists exports as a follow-up and recommends the plugin-dev install when the baseline was absent.
- `src/references/settings.md` and the five synced copies under `metacognition/skills/*/references/`: only the description of the exemplar changed, and it is now an advanced option.
- `CLAUDE.md` and `todo.md` updated.

## Verification

- `uv run pytest -q`: 504 passed.
- `just check` exits 0.
- The validator verdict was clean at iteration 1.

## Deviations from Plan

None recorded.

## Observations

- For Step 13: `docs/configuration.md` lines 16 and 94 contradict the settings reference until that step updates them.
- The page still says skillify tells the person the exemplar was not found and describes the exemplar as a shape to match.
- For Step 13: the README needs the plugin-dev companion-install recommendation.
