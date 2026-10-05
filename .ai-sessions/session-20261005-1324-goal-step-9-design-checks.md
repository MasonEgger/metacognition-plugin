# Session: Step 9, Design Checks Artifacts and Plans Register Coverage

## Summary

In the first full run, design pointed at a repository that turned out to be an empty skeleton, and one planned register got no dedicated questions.
Step 9 changes the design skill so it checks artifact paths before planning around them and refuses to finish with a register no category targets.
The skill body went from about 1,985 to about 2,340 words.
The scope Q&A and Research steps are untouched.

## What Changed

- `metacognition/skills/design/SKILL.md`: the category map gains a Registers column, and a gate requires every planned register to be targeted by at least one category.
- The artifact plan now checks each path before the plan relies on it, with a plain definition of an empty skeleton.
- Where the surface has no file access, the skill states that in one line instead of checking.
- An unavailable path counts as none toward `artifacts_available`.
- Seeds are concrete scenarios, with one bad and one good example.
- The closure pass confirms both the register check and the artifact check.
- `todo.md`: Step 9 checked off.

## Verification

- `uv run pytest -q`: 504 passed.
- `just check` exits 0.
- The validator verdict was clean at iteration 1 with no findings.

## Deviations from Plan

None recorded.
