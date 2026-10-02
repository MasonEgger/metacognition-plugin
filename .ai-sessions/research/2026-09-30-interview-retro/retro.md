# Interview Retro: First Full Pipeline Run

This is the public version of a retro written on 2026-09-30, right after the first real (non-fixture) run of the design and interview stages closed.
The original lives in the private source and quotes the person's interview answers at length.
Those quotes are not reproduced here, because an archive holds verbatim answers and stays private.
What follows keeps the findings, the evidence in summary form, and the recommendations, with every file reference rewritten for this repo.

It exists so the next phase can turn it into a spec slice and a plan.
Nothing in it has been implemented.

## The Run

The run covered two pipeline stages over about six days and at least three sittings, with dictation as the main input mode.

Design stage:

- The domain statement widened during scope questions.
- Augment mode against an existing skill, which the person confirmed was accurate but had gaps.
- Four registers, with a fifth candidate register explicitly rejected.
- Domain research returned twelve dimensions, and the person added four more to probe again.
- Nine categories: the seven generic slots plus two domain additions, with a floor sum of 95.
- 53 question seeds, 21 of them grounded in the existing skill, and 12 forced-choice bank entries.

Interview stage:

- 100 questions logged: 96 category questions, the three fixed closers, and one domain closer.
- All nine categories reached floor and closed.
- Nine contradiction ledger entries, all resolved, four of them against the target skill itself.
- Eight live research rounds during the interview, plus the design-stage research.
- The closing self-check passed the structure check and the prose check.

Two shifts happened mid-interview, both at the person's explicit request, and they are the core of this retro.
At question 47 the style changed from single laddered questions to five-item concrete batteries.
At question 73 research changed from banking deferrals for a later stage to dispatching in the same turn and ratifying the result.

## What Worked

**Artifact grounding produced the highest-value catches.**
Reconciling the person's published and shipped work against their stated rules surfaced decisions the existing skill never absorbed, and forced real resolutions where a stated rule and a shipped artifact disagreed.

**Treating the existing skill as an artifact showed how much of it was not load-bearing memory.**
The person did not recognize several rules in their own skill.
Each unrecognized rule was then either ratified again with fresh reasoning or retired.
Without augment-mode probing those would have stayed as rules nobody stands behind.

**The contradiction ledger did its job in real time.**
It caught a dictation slip within one question, tracked a three-step change of mind to a settled answer, and caught the person contradicting their own written rule.
The most productive entries were skill-versus-statement, not statement-versus-statement.

**Verbatim capture preserved material compile needs.**
Hedges, garbles, and analogies all survived intact.
The codepoint normalization rule worked without friction.

**Live research became taste extraction.**
One research round flipped a stated preference into a rule adopted on evidence, and the person named that flip in a closing question as the thing they learned.
Research rounds also produced meta-rules nobody planned to ask about.

**Incremental persistence removed resume anxiety.**
The archive and the README were current after every answer, so nothing was at risk beyond the question in flight.
Resume was never needed, but the state that would have made it cheap was always on disk.

**The closing questions earned their fixed slots.**
They produced the request for this retro, the feedback that the early interview was too reserved, an override rule for the profile, and a structure hint for compile.

## What Failed Or Dragged

**(a) The early interview was too reserved.**
Questions 1 through 46 were mostly single ladder, contrast, or critical-incident probes, one per turn.
Batteries from question 47 onward produced most of the profile's checkable rules per unit of the person's time.
Several early open probes produced adjectives that needed a second question to anchor.
The interview skill's rule against batching two questions in a turn reads as forbidding the thing that worked best.
The distinction the rule needs is open-ended versus closed-form: batching two open probes loses data, and a battery of closed verdict items in one category does not.

**(b) Deferred research was banked silently.**
The person used deferral phrases repeatedly, telling the interviewer to look up standard practice.
The interviewer researched two of them live and banked the rest for skillify without saying so.
The person noticed and objected, and the backfill cost a three-agent dispatch and two ratification rounds to repay eleven items.
Once research ran in the same turn, with bottom lines presented, ratified, and recorded with citations, it worked and the person engaged with every round.
The cause was the skill text, which says the interview dispatches nothing, and the interviewer followed that until overridden.

**(c) Battery accounting distorts the floor arithmetic.**
A five-item battery logs as one question entry and adds one to its category count.
The nominal 100 questions carried well over 150 distinct probes.
The floors were calibrated for single-question units, so the interview chased counters that no longer measured coverage.
Saturation is also harder to judge when one entry holds five constraints.

**(d) Archive persistence cost four to five file edits per question.**
Each answer needed separate edits to the question count, the category counter, the body, and the README cell, plus a ledger edit when a contradiction landed.
Over 100 questions that is roughly 420 edits of bookkeeping.
It never corrupted state, but it is slow, and each batch is a window where an interruption leaves frontmatter and body out of step.

**(e) Picker provenance smudged verbatim capture.**
Several picker answers were logged as the selected label followed by the option's description text, which the interviewer wrote.
The person endorsed that text by selecting it, but the archive does not tell dictated words from clicked options.
Compile needs a convention to tell them apart.

**(f) Smaller friction.**

- Numbering drift: when research or an interruption landed while a question was pending, chat labels and archive numbers drifted apart. The archive stayed contiguous, but the convention that archive numbering is authoritative was invented mid-run.
- A dead artifact: design pointed at a repository that turned out to be an empty skeleton, and the real one only surfaced when the person pasted a link mid-interview. Design never checked that artifact paths held content.
- Registers were underused: nearly every question carried the primary register, one planned register got no dedicated questions, and a new register surfaced mid-interview with nowhere to go.
- Mid-answer corrections were handled by replacing the answer with the corrected dictation, which is right, but the convention is not written anywhere.
- Scope redirects, where the person said a topic belongs to a different skill, were captured only inside verbatim answers, with no structured place for skillify to find them.
- One question had to be asked again because an abstract phrasing did not land, and a concrete scenario worked at once. Concrete scenarios beat abstract framings, and the seeds should reflect that from the start.

## Recommendations

Ordered by expected impact.
Paths are this repo's.
A change to a file under `src/references/` also changes the docs page that restates it, in the same pull request.

### 1. Make Batteries A First-Class Technique

Files: `metacognition/skills/interview/SKILL.md`, `src/references/extraction-theory.md` (the rule 16 technique table), `src/references/archive-format.md`.

Change the interview loop from one question at a time to a turn discipline.
A turn is either a single open probe or a battery: three to six closed-form verdict items, all in one category, each answerable with a stance and a sentence.
Never two open probes in one turn, and never mixed categories in a battery.

Open probes lead early, while the map of the person's judgment is still forming, and whenever an answer needs laddering.
Batteries take over once a category's shape is known and what remains is collecting verdicts.
A request for more concrete questions is a standing instruction, not a one-turn preference.
A battery item that gets a surprising answer earns an open follow-up.

A battery logs as one question entry with numbered items and numbered answers, tagged as a battery probe, with an optional item count on the heading so tooling can count probes.

### 2. Write A Live-Research Protocol Into The Interview Skill

File: `metacognition/skills/interview/SKILL.md`.

The current text says the interview dispatches nothing, which forbids what the person asked for.
A research dispatch should fire in the same turn whenever the person defers to outside practice or asks for one, and a deferral is never banked for a later stage.

When research returns, present the bottom lines with citations, ratify with the person, and record the outcome as its own question entry whose question line carries the findings and links.
A deferral that committed in advance still gets presented and ratified, because the person's reaction to evidence is taste data.

Corollary for compile: a compiled profile never contains a bare instruction to follow community practice.
Every deferral resolves into the written practice with its citation.

### 3. Picker Use And Provenance

Files: `metacognition/skills/interview/SKILL.md`, `src/references/archive-format.md`.

Forced-choice probes and research ratifications go through the host's picker when one exists, and open probes never do.
A picker selection logs the selected label verbatim and nothing else, unless the person added their own words, which follow verbatim.
Option description text is the interviewer's, so it belongs in the question line as part of the option, never in the answer line.

### 4. Floors Count Probes, Not Turns

Files: `metacognition/skills/design/SKILL.md`, `src/references/interview-spec-format.md`.

A battery of five items is five probes.
State this in the spec's category map so the interview's counters and the README cell measure what design calibrated.
The alternative, counting turns and lowering the default floors, makes floors depend on interviewing style.

### 5. Design Verifies Artifacts And Plans Register Coverage

File: `metacognition/skills/design/SKILL.md`.

Before writing the artifact plan, check that every local path exists and holds real content.
An empty skeleton is recorded as unavailable and the person is told at design time.

The category map gains a note per category naming which registers its questions target, and the interview's progress notes report register coverage beside category coverage.
A register with no planned questions is a design-time error.

### 6. An Exports Section For Scope Redirects

Files: `src/references/archive-format.md`, `metacognition/skills/interview/SKILL.md`, with a consumption note for compile and skillify.

Add an exports section to the archive, kept up as the interview goes, like the ledger.
One line per redirect, naming the question and the destination.
An export records taste the person voiced but assigned to a different skill's territory.
Compile leaves export content out of the profile body and carries the list forward, and skillify surfaces it as follow-up work.

### 7. One Call To Append An Archive Entry

Files: `metacognition/skills/interview/SKILL.md`, a new shipped script under `src/scripts/`.

A script that, in one call, appends the entry, raises the question count and the category counter, flips saturation when told, rewrites the README cell, and optionally appends a ledger line.
The skill text then replaces the four-edit ritual with one call, and the interruption window shrinks to one write.
The fallback, if tooling waits, is to require a single edit that carries the body and the counters together.

### 8. Write Down Correction And Re-Ask Conventions

Files: `metacognition/skills/interview/SKILL.md`, `src/references/archive-format.md`.

When the person interrupts and dictates an answer again, the corrected dictation is the answer: replace, do not append.
A question the person did not understand is not logged; the reframed version that got an answer is the question of record.
Chat labels may drift from archive numbers, and the archive's contiguous numbering is authoritative.

### 9. Route Emergent Meta-Rules To The Right Layer

Files: compile and profile guidance, plus one candidate for `src/references/extraction-theory.md`.

Rules about how the person wants judgment exercised (when to reconsider a dependency, whose decisions take precedence over an adopted outside reference, deletion before addition, how to raise a discouraged pattern, what posture to take in uncodified areas) emerged mid-run.
They are profile content, not interview-skill content, and compile guidance should say where they go.

The one generic candidate for extraction theory is the evidence probe: the person's response to researched evidence is first-class taste data.

### Smaller Text Fixes

- Interview skill: a question with no register-specific content takes the domain's primary register, and the progress note flags registers with no coverage.
- Interview spec format: the README's interview cell may exceed the floor and is marked complete when the status flips.

## What This Repo Adds To The Problem

The private retro was written against a single-surface plugin with shared references.
This repo has constraints it did not have to consider.

- **A spec invariant changes.** The Invariants list "one question per turn" as a pipeline rule that holds on every surface. Recommendation 1 replaces it with a turn discipline, so the spec changes first.
- **Three surfaces.** The interview runs on Claude Code, Cowork, and claude.ai chat. A picker may not exist on every surface, and plugin agents are ignored on claude.ai chat, so recommendations 2 and 3 need the same three-way wording the design stage already uses for research: dispatch where agents load, run in-session otherwise, and say so and continue with no web access.
- **Sync slices.** Each skill ships only its slice of `src/`. If the interview skill starts doing research it needs the research contract in its slice, and a new script joins the interview slice. Both change the manifest in `tools/sync_skills.py` and the table in spec goal G2.
- **Shipped scripts.** A new script is standard library only, runs on Python 3.11 or newer, is written test-first, works as `python3 scripts/<name>.py`, and has a by-hand fallback stated in the skill for when it cannot run.
- **The validator.** An item count on battery headings and an exports section both need `src/scripts/validate_artifacts.py` to accept them, with tests and fixtures.
- **Docs that restate references.** The Method page restates extraction theory and says there are sixteen rules; an evidence-probe rule would make seventeen. The File Formats pages restate the archive and interview spec formats.
- **Evals and fixtures.** The interview and design evals check behavior that changes, and the woodworking fixture is the only example the project ships.
- **Version.** Whether this is a new beta version is the maintainer's ruling.

## Open Questions For The Maintainer

The private retro closes with six questions.
Three are about the plugin and gate parts of the scope:

1. Floor semantics: count probes and keep the default floors, or keep counting turns and shrink the floors? The retro recommends counting probes.
2. The append script: build it before the next extraction, or run one more extraction on the manual ritual first?
3. Live research volume: always on with no cap, or should the interviewer state a running count at checkpoints?

The other three concern the private extraction itself (a follow-up session for under-covered registers, whether reconstructed exports are authoritative, and whether older picker entries get annotated).
They stay with that extraction and are not part of this repo's scope.

Two more arise from this repo:

4. Does the interview stage get research on claude.ai chat, where there is no agent to dispatch and web access may be absent, or is live research limited to surfaces that can do it?
5. Is the evidence probe a seventeenth extraction rule, or a note under an existing rule?

## Handoff

Inputs in this repo:

- This file.
- The skills and references it proposes changing: `metacognition/skills/design/SKILL.md`, `metacognition/skills/interview/SKILL.md`, `metacognition/skills/compile/SKILL.md`, `src/references/extraction-theory.md`, `src/references/archive-format.md`, `src/references/interview-spec-format.md`, and `src/scripts/validate_artifacts.py`.
- The issue that tracks the work, linked from the Roadmap in `spec.md`.

Expected output: a spec slice and a plan through the normal flow, opening with the open questions above.
Each of the nine recommendations is either implemented or declined with a reason recorded in the spec or the plan.
