# Extraction Theory

Every skill in this plugin reads this document first, before it asks a single scoping question or writes a single line of a profile.
It is the layer beneath the five pipeline skills: the argument for why the interview is shaped the way it is, and the discipline that keeps compression from flattening a person's judgment into a list of adjectives.

The sixteen rules below are domain-agnostic.
They hold whether the subject is code review, wine selection, editorial voice, or furniture making.
Examples in this document use woodworking, the same neutral domain the fixture extraction uses, so no rule reads as biased toward writing or code.

## Why This Method Works

Most attempts to capture a person's taste produce a list of preferences that sound right and change nothing.
The failure is not effort, it is method.
A profile built from open questions and self-description collects the person's story about themselves, not the judgment that actually drives their decisions in the moment.
The rules below correct for that gap at every stage of the pipeline: what gets asked, how an answer gets pushed past its first draft, what survives when an interview is compressed into a profile, and how the profile gets tested against real output before anyone trusts it.

## The Sixteen Rules

### 1. Stated vs Revealed Preference

Self-report captures a person's model of their own taste.
Revealed preference, the choices already made in real artifacts, captures what the taste actually does when it matters.
Gather both, and when they diverge, record the divergence as a productive contradiction rather than resolving it in the interviewer's favor.

Bad probe: "Do you prefer hand-cut joinery?"
Good probe: "This cabinet's face frame is pocket-screwed, but you said dovetails are the standard you hold yourself to. Walk me through the gap."
The second question is accountable to a decision that already happened; the first invites a comfortable answer with no cost to giving it.

### 2. Negatives Outrank Positives

A rule stated as "never do X" changes what a downstream system produces more reliably than a rule stated as "always do Y," because "always" tolerates exceptions in a way "never" does not.
At least 40 percent of every interview's questions should aim at the person's crimes, hard nos, red flags, and the things that make them wince.

Bad probe: "What do you like in a finish?"
Good probe: "What finish, applied to a piece you'd otherwise be proud of, would make you refuse to put your name on it?"
The first question surfaces an adjective; the second surfaces a refusal, and refusals are what an AI system needs most to avoid producing work the person would reject on sight.

### 3. Examples Outrank Adjectives

An abstract answer like "clean" or "honest" gives a downstream system nothing to act on until it is anchored to a concrete instance.
No answer that is only an adjective is accepted as final; every abstract claim earns a follow-up demanding a specific artifact, ideally one the person made themselves.

Bad probe accepted as-is: "I like joints that are honest."
Good follow-up: "Show me one you've built that's honest, and one that isn't, even though it might fool someone who didn't know better."
The forced comparison turns the adjective into two artifacts a system can pattern-match against, instead of a word it can only paraphrase.

### 4. Forced Choice Beats Open Description

Open-ended description lets a person describe an ideal that does not correspond to any decision they would actually make under real constraints.
A forced choice between two concrete, plausible options collapses the ideal into a real decision, and the reasoning behind the choice is where the taste actually lives.

Bad probe: "How do you feel about mitered versus butt joints?"
Good probe: "Here are two identical boxes, one mitered and glued, one butt-jointed and pinned. Which one ships, and why?"
A person who would never build the mitered box under deadline reveals that the moment they have to pick one, not before.

### 5. Laddering

A first answer is almost always a surface preference, not the underlying value that produced it.
Asking "why does that matter to you?" up to three times, and no further, reaches that underlying value without wandering into territory the person has no real position on.
Record the entire ladder, including the final and weakest rung, because a contradiction discovered later often traces back to a weak leaf rather than the strong root.

Example ladder: "Why walnut over oak?" leads to "the grain reads calmer." "Why does calm grain matter?" leads to "the piece should recede behind whatever sits on it." "Why should the piece recede?" leads to "because I build furniture, not sculpture."
Three whys, then stop; a fourth why tends to produce a rationalization rather than a value.

### 6. Contrast Probing

For any quality a person names, ask them to show the same quality done well and the same quality done lazily.
The pair makes the boundary explicit in a way a single example cannot; a person who claims to value "restraint" usually cannot define the word until they are looking at a version with too little and a version with too much.

Good probe: "Show me a joint that's restrained, and one that's trying too hard to look restrained."
The second half of the pair exposes a failure mode that the first half alone would hide, since a virtue and its overcorrection often share a surface appearance.

### 7. Artifact Grounding

Interviews seeded from a person's real work outperform interviews built from hypotheticals, because "you did X here, why not Y?" forces an answer accountable to a decision that already happened rather than a decision the person is imagining for the first time.
In augment mode, an existing skill built from an earlier interview is itself an artifact: a stated preference captured before, now probed against what the person says today.

Good probe: "In this cabinet, the back panel is plywood but the face frame is solid stock. Why draw the line there instead of using solid stock throughout?"
A hypothetical version of the same question, "would you ever use plywood?", invites a rehearsed answer instead of the reasoning behind a choice already made.

### 8. Contradiction Detection

Keep a running ledger of every stated rule and every observed exception, and surface a conflict the moment it appears rather than after the interview has moved on.
Ask which rule wins, and under what conditions; never smooth two positions into a compromise the person never actually held.
Some contradictions are register-dependent rather than mistakes, and smoothing them over destroys real information the profile needs later.

Example: a woodworker says he never uses pocket screws, then two questions later mentions using them on a shop jig he'll never show anyone.
The ledger flags it immediately: "Earlier you said never pocket screws; this jig has them. Which rule is true, and when?"
The honest answer, "never on furniture, always on shop fixtures," is two rules rather than one broken one, and the ledger should hold it that way.

### 9. Register Separation

Ask up front which contexts the profile needs to cover, before any substantive question is asked.
A single blended profile that tries to hold a person's standard for a paying client's commission and their standard for a weekend shop project produces judgment that fits neither situation well.
Multiple registers become multiple profiles, or an explicit switch inside one profile that names the trigger for each register.

Example: a furniture maker's standard for a commissioned dining table and his standard for a jig he will never sell are different standards, not two degrees of one standard.
Ask which register a question belongs to before recording the answer, not after.

### 10. Saturation, Not Quotas

A fixed question count per category either stops too early, missing a category with more left to say, or wastes questions on a category that emptied out early.
Question counts are floors, not targets: a category is saturated when three consecutive answers add no new constraint, and interviews typically run 60 to 120 questions in total across every category.

Example: if the third straight question about finish produces "yeah, same as I said before," the finish category is saturated and the interview moves on, regardless of how many questions were originally planned for it.
A floor guarantees minimum coverage; saturation, not the floor, decides when a category is actually done.

### 11. Verbatim Capture

The archive is the source of truth for the interview, and it must preserve a person's exact words rather than a summary of them.
Paraphrasing at capture time throws away the phrasing that carries the taste itself; a person's specific vocabulary, hedges, and emphasis are data the later compile step needs, not noise to clean up early.

Example: if a woodworker says "I guess dovetails are fine, but honestly, who's checking," the archive records that sentence exactly, hedge and all, rather than compressing it to "prefers dovetails."
Compression is a separate, later step, applied deliberately, never accidentally at the moment of capture.

### 12. Interviewer Drift

Long interviews accumulate an inferred pattern that starts to feel confirmed simply because nothing has tested it recently.
Every 20 questions, re-read the ledger and ask at least one question built to disconfirm a pattern the interview thinks it has found, rather than one more question that would only confirm it further.

Example: after 20 questions suggesting a strong preference for hand tools, the disconfirming question is not "you really do prefer hand tools, right?" but "tell me about a project where a power tool was clearly the better call, and you took it without a second thought."
An interview that never tries to break its own pattern will report the pattern with more confidence than the evidence earns.

### 13. Unknown-Unknowns Pass

Before the substantive interview begins, name 3 to 5 dimensions the person likely has real taste about but would not think to raise unprompted, because the dimension is invisible to them until it is named.
Skipping this pass leaves entire categories of judgment uncaptured, not because the person had nothing to say about them, but because no one asked.

Example: a woodworking profile scoped around "joinery and finish" might miss the person's opinions on shop layout discipline, tool maintenance habits, or how much a piece should reveal the maker's hand versus disappear into the room it sits in.
Naming these dimensions up front catches taste the initial scoping conversation alone would miss.

### 14. The Keep/Cut Test

When an interview is compressed into a profile, a line earns its place only if removing it would change how a downstream system writes, judges, edits, refuses, or decides something.
Biography, general values statements, and flattering self-description are cut, no matter how central they felt during the interview, unless they change an actual output.

Example: "I've been woodworking for twenty years" is cut; it changes nothing downstream.
"Never use pocket screws on anything that will be seen" is kept; it is a direct, checkable instruction a system can follow or violate.
The test is mechanical, not sentimental: ask what output would differ, and if the answer is nothing, the line goes.

### 15. Calibration Is the Moat

An interview alone produces a plausible-looking profile, not an accurate one.
Accuracy comes from testing the profile against real output and folding the corrections back into the profile, repeatedly, until the corrections stop mattering as much.
A profile is not done until three calibration rounds show non-increasing correction volume (the precise calibrated test lives in profile-format.md); anything short of that is a draft wearing the shape of a finished profile.

Example: round one of a woodworking profile might produce a project plan that violates three named rules; round two, after fold-back, violates one; round three violates none.
That downward trend, not the quality of the first draft, is what makes a profile trustworthy enough to hand to a skill.

### 16. Elicitation Technique Index

Different interviewing techniques surface different kinds of judgment, and no single technique surfaces all of them.
The table below maps each technique to the situation where it earns its cost.

| Technique | When to Use |
|---|---|
| Repertory grid (triads) | Present three artifacts and ask which two share a quality the third lacks; surfaces dimensions the person has never named on their own. |
| Critical incident | Ask for a specific time a decision went visibly right or wrong, in detail; surfaces judgment tied to a real event rather than a general claim. |
| Think-aloud review | Have the person narrate their reaction to an artifact in real time, before they have composed an opinion; catches instinct ahead of rationalization. |
| Sorting | Give a stack of artifacts and ask for a rank order or a grouping; the boundaries drawn reveal categories the person would not state directly if asked. |
| Boundary probing | Ask for the least acceptable version of something the person would still tolerate; finds the edge of a standard rather than just its comfortable center. |
| Verdict battery | Three to six closed items in one category, each answerable with a stance and a sentence; use once a category's shape is known and what remains is collecting verdicts. |
| Evidence probe | Present researched practice with sources and ask the person to ratify, adjust, or reject it; the reaction to evidence is taste data in its own right. |

A repertory grid works early, when the category map is still forming and the goal is finding dimensions.
A critical incident works mid-interview, when a category needs grounding in something specific rather than another round of hypotheticals.
Boundary probing works well late, once enough context exists to know what "acceptable" even means for this person.
A verdict battery works once a category's shape is known, and a surprising answer to one item earns an open follow-up.
An evidence probe works whenever the person defers to outside practice or asks for research: the findings are presented with their sources, and the person's reaction is logged verbatim.

## Using This Document

`design` reads this document before it scopes a single interview, so the category map and question seeds are built on these rules rather than reinvented per domain.
`interview` reads it before asking a single question, and returns to rule 12 every 20 questions as the disconfirmation check.
`compile` applies rule 14 as its literal compression test, and rule 1 to decide when a divergence becomes a recorded tension rather than a resolved preference.
`calibrate` exists because of rule 15: an interview seeds a profile, calibration is what earns the profile the right to be trusted.

None of these rules is optional per domain.
A domain can add category slots, change vocabulary, or skip a technique that does not fit its artifacts, but it cannot skip a rule, because the rule is what makes the resulting profile change how a system behaves instead of merely describing a person.
