---
domain: woodworking
round: 1
date: 2026-09-21
task: Recommend a fence-to-base attachment for a new router table jig, and justify the call.
corrections: 2
---

*Synthetic fixture calibration round for the metacognition pipeline tests. Not a real calibration round.*

## Task

Recommend a fence-to-base attachment for a new router table jig, and justify the call. Bank entry: Selection 1 (recommend one of three supplied options and justify the call), adapted to a domain-specific jig question since none of the bank entries name a shop-fixture case directly.

## Generated artifact (probe; never ships)

Recommendation: attach the fence to the base with two pocket screws and a bead of glue. Pocket screws keep the joint tight and glue backs it up, and since the fence will get swapped out eventually anyway, a permanent joint is not worth the extra setup time. A mitered corner on the fence itself would look tidier but adds no real holding power over a butt joint, so skip it.

## Corrections (verbatim)

1. "Pocket screws are right for a jig, no correction there, that reads correctly." Why: matches the register-dependent rule; jigs and furniture are separate cases.
2. "You wrote 'no real holding power over a butt joint' about the fence corner, but you never said which one you would actually build. Say the butt joint ships, the way the toolbox example already settled it, instead of just comparing options and stopping." Why: an evaluation without a stated recommendation is not a decision; the profile's domain law on pinned butt joints should have produced a direct call.

## Fold-back decisions

| # | Correction | Decision (a/b/c) | Profile edit |
|---|---|---|---|
| 1 | Pocket screws on the jig read correctly, no edit needed. | a | None; confirms the existing register-dependent tension entry needs no change. |
| 2 | Recommendation stopped at a comparison instead of naming what ships. | a | Strengthened the first `domain_laws` entry's example clause to state explicitly that the butt-jointed, pinned option ships, not merely that it survives better, so a generated recommendation states a call rather than only a comparison. |
