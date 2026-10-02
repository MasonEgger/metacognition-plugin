# Calibration Protocol

`/metacognition:calibrate` runs `profile.md` against a task, hands the result to the person for redlines, and folds every correction back into the file.
This reference documents the material the skill needs to run a round: the task bank it picks from, how to build a task when the bank does not fit, the fold-back decision tree that turns a correction into a profile edit, and the round file format each round writes to disk.

Calibration reads `profile.md` only, never the archive; the point of a round is to test the compressed file the way a consumer skill will actually load it.

## Task Bank

A calibration task exists to produce an artifact the person can redline, not to test recall.
When `target_skill` is set in `interview-spec.md`, the existing skill's `evals/` directory is a candidate source of tasks before falling back to this bank.
Each entry below names the artifact the task must produce; the skill fills in the concrete prompt (a real diff, a real draft, a real backlog) at run time rather than inventing a toy example.

### Writing

1. Draft a short piece (300 to 500 words) on a supplied topic in the domain's target register.
2. Rewrite a rough paragraph pulled from an existing draft into finished prose.
3. Write inline redline comments on a supplied piece of someone else's writing.
4. Expand a bullet outline into full prose.
5. Write the closing section for a supplied piece that stops short of an ending.

### Code

1. Implement a function from a supplied signature and behavior description.
2. Refactor a supplied function for clarity without changing its behavior.
3. Write review comments on a supplied diff.
4. Write tests for a supplied function.
5. Diagnose and fix a supplied failing test, explaining the fix.

### Architecture

1. Draft a one-page design note for a supplied feature request.
2. Describe the component boundaries for a supplied system.
3. Write a decision record for a supplied technical tradeoff.
4. Sketch a data model for a supplied domain.
5. Write a migration plan for a supplied breaking change.

### Review

1. Leave inline comments on a supplied pull request diff.
2. Leave margin notes on a supplied document draft.
3. Triage and rank a supplied backlog.
4. Flag risks in a supplied contract or proposal.
5. Check a supplied plan step against its spec's stated constraints and report violations.

### Selection

1. Recommend one of three supplied options (vendors, tools, approaches) and justify the call.
2. Rank a supplied set of candidates and justify the order.
3. Pick one item from a supplied list of ideas and justify keeping or killing it.
4. Choose between two supplied competing designs and justify the choice.
5. Prioritize a supplied reading or work list and justify the order.

### Product

1. Write a one-paragraph problem statement for a supplied user complaint.
2. Draft the Non-goals section of a spec for a supplied feature.
3. Write a prioritized slice of a roadmap from a supplied backlog.
4. Draft release notes for a supplied changeset.
5. Write a go or no-go recommendation for a supplied launch candidate.

## Constructing A Domain-Specific Task

When none of the bank entries fit the domain, build one that meets the same three requirements the bank entries meet:

- The task produces an artifact the person can redline: a document, a diff, a ranked list, a memo. A task whose output is a bare yes/no or a single sentence gives nothing to correct against.
- The task exercises judgment, not recall. It should force a choice the profile's `judgment_fingerprint` and `decision_rules` actually bear on, not a lookup of a fact the archive happens to record.
- The task draws on real material where real material exists (an open PR, an actual backlog, a genuine draft) rather than an invented example, because invented examples tend to under-specify the exact ambiguity a real artifact carries.

## The Fold-Back Decision Tree

Every correction the person makes during a round resolves to exactly one of three decisions.
The skill records the decision in the round file's Fold-back decisions table and edits `profile.md` accordingly, marking every changed line with `<!-- calibrated: round N, YYYY-MM-DD -->`.

**(a) The profile has the rule, but the generated artifact misapplied it.**
Strengthen the existing rule's wording, or add a golden example that makes the correct application concrete. The rule itself is not wrong; the profile did not state it forcefully enough to survive generation.

**(b) The profile lacks the rule entirely.**
Add a new law or refusal, citing the round that surfaced it. This is the ordinary growth path: a gap the interview did not reach, now closed by a concrete miss.

**(c) The correction contradicts a rule already in the profile.**
Surface the conflict rather than picking a winner silently. Ask the person which rule wins in this case. Encode the answer either as a `<tension>` entry (both readings are valid, context-dependent) or as a replacement of the losing rule, per their answer.

## The Round File Format

Each round writes `<root>/<slug>/calibration/round-NN.md`.

```markdown
---
domain: <slug>
round: NN
date: YYYY-MM-DD
task: <id or path>
corrections: N
---
## Task
## Generated artifact (probe; never ships)
## Corrections (verbatim)
## Fold-back decisions
| # | Correction | Decision (a/b/c) | Profile edit |
```

The frontmatter fields: `domain` matches the extraction's slug; `round` is the zero-padded round number, contiguous from `01`; `date` is the day the round ran; `task` is the task bank id or the path to the supplied task material; `corrections` is the count of corrections the person made this round, the figure the calibrated-state test tracks.

The body's four sections, in order:

- **Task.** What was asked: the task bank entry or the constructed prompt, verbatim.
- **Generated artifact (probe; never ships).** What the profile produced, unedited. The heading itself carries the probe label; no separate disclaimer line is needed.
- **Corrections (verbatim).** The person's redlines exactly as given, in chat or via `--corrections`, with a why per correction where one was given.
- **Fold-back decisions.** One table row per correction: its number, the correction itself, the decision (`a`, `b`, or `c`), and the specific edit made to `profile.md`.

## The Probe Rule

Every round's Generated artifact heading states that what follows is a probe and never ships, regardless of domain.
This holds even in a domain whose eventual skill is forbidden from authoring on its own: calibration still needs a generated artifact to redline, so the skill produces one, labeled as a probe, and the never-author boundary applies to the produced skill's own operation, not to this diagnostic step.

## Calibrated State

Each round's report states the trend across rounds run so far.
The test that flips a profile's `calibrated` field to `true` is defined once, in `profile-format.md`'s `calibrated` frontmatter field entry; this reference does not restate it.
