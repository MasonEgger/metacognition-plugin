# The Method

Every stage of the plugin follows one set of rules.
There are sixteen.
They are domain-agnostic, and they hold whether the subject is code review, wine selection, editorial voice, or furniture making.
The examples here use woodworking, the same neutral domain the plugin's synthetic fixture uses.

## Why It Works

Most attempts to capture a person's taste produce a list of preferences that sound right and change nothing.
The failure is not effort.
It is method.
A profile built from open questions and self-description collects your story about yourself, not the judgment that drives your decisions in the moment.
The rules correct for that gap at every stage: what gets asked, how an answer gets pushed past its first draft, what survives when an interview is compressed, and how the profile is tested against real output before anyone trusts it.

## The Sixteen Rules

### 1. Stated vs Revealed Preference

Self-report captures your model of your own taste.
Revealed preference, the choices you already made in real artifacts, captures what the taste does when it matters.
The interview gathers both.
When they diverge, the divergence is recorded as a productive contradiction and is not resolved in the interviewer's favor.

A weak probe is "Do you prefer hand-cut joinery?"
A better one is "This cabinet's face frame is pocket-screwed, but you said dovetails are the standard you hold yourself to. Walk me through the gap."
The second question is accountable to a decision that already happened.
The first invites a comfortable answer with no cost to giving it.

### 2. Negatives Outrank Positives

A rule stated as "never do X" changes what a downstream system produces more reliably than "always do Y," because "always" tolerates exceptions in a way "never" does not.
At least 40 percent of every interview's questions aim at your crimes, hard nos, red flags, and the things that make you wince.

"What do you like in a finish?" surfaces an adjective.
"What finish, applied to a piece you'd otherwise be proud of, would make you refuse to put your name on it?" surfaces a refusal.
Refusals are what an AI system most needs in order to avoid producing work you would reject on sight.

### 3. Examples Outrank Adjectives

An abstract answer like "clean" or "honest" gives a downstream system nothing to act on until it is anchored to a concrete instance.
No answer that is only an adjective is accepted as final.
Every abstract claim earns a follow-up that demands a specific artifact, ideally one you made yourself.

If you say "I like joints that are honest," the follow-up is "Show me one you've built that's honest, and one that isn't, even though it might fool someone who didn't know better."
The forced comparison turns the adjective into two artifacts a system can pattern-match against.

### 4. Forced Choice Beats Open Description

Open-ended description lets you describe an ideal that matches no decision you would make under real constraints.
A forced choice between two concrete, plausible options collapses the ideal into a real decision, and the reasoning behind the choice is where the taste lives.

"How do you feel about mitered versus butt joints?" is open.
"Here are two identical boxes, one mitered and glued, one butt-jointed and pinned. Which one ships, and why?" is forced.
Someone who would never build the mitered box under deadline shows it the moment they have to pick one.

### 5. Laddering

A first answer is almost always a surface preference, not the underlying value that produced it.
Asking "why does that matter to you?" up to three times, and no further, reaches the underlying value without wandering into territory you have no real position on.
The whole ladder is recorded, including the final and weakest rung, because a contradiction found later often traces back to a weak leaf rather than the strong root.

Example: "Why walnut over oak?" leads to "the grain reads calmer." "Why does calm grain matter?" leads to "the piece should recede behind whatever sits on it." "Why should the piece recede?" leads to "because I build furniture, not sculpture."
Three whys, then stop.
A fourth tends to produce a rationalization rather than a value.

### 6. Contrast Probing

For any quality you name, you are asked to show the same quality done well and done lazily.
The pair makes the boundary explicit in a way a single example cannot.
Someone who claims to value "restraint" usually cannot define the word until they look at a version with too little and a version with too much.

A probe: "Show me a joint that's restrained, and one that's trying too hard to look restrained."
The second half of the pair exposes a failure mode the first half hides, since a virtue and its overcorrection often share a surface appearance.

### 7. Artifact Grounding

Interviews seeded from your real work outperform interviews built from hypotheticals.
"You did X here, why not Y?" forces an answer accountable to a decision that already happened, instead of one you are imagining for the first time.
In augment mode, an existing skill built from an earlier interview is itself an artifact: a stated preference captured before, now probed against what you say today.

A probe: "In this cabinet, the back panel is plywood but the face frame is solid stock. Why draw the line there instead of using solid stock throughout?"
The hypothetical version, "would you ever use plywood?", invites a rehearsed answer.

### 8. Contradiction Detection

The interviewer keeps a running ledger of every stated rule and every observed exception, and surfaces a conflict the moment it appears.
It asks which rule wins, and under what conditions.
It never smooths two positions into a compromise you never held.
Some contradictions depend on context rather than being mistakes, and smoothing them over destroys information the profile needs later.

Example: a woodworker says he never uses pocket screws, then two questions later mentions using them on a shop jig he will never show anyone.
The ledger flags it at once: "Earlier you said never pocket screws; this jig has them. Which rule is true, and when?"
The honest answer, "never on furniture, always on shop fixtures," is two rules and not one broken one, and the ledger holds it that way.

### 9. Register Separation

Before any substantive question, the interview asks which contexts the profile needs to cover.
One blended profile that holds your standard for a paying client's commission and your standard for a weekend shop project produces judgment that fits neither.
Multiple registers become multiple profiles, or an explicit switch inside one profile that names the trigger for each register.

A furniture maker's standard for a commissioned dining table and his standard for a jig he will never sell are different standards, not two degrees of one standard.
The interview asks which register a question belongs to before it records the answer, not after.

### 10. Saturation, Not Quotas

A fixed question count per category either stops too early, missing a category with more to say, or wastes questions on a category that emptied out early.
Question counts are floors, not targets.
A category is saturated when three consecutive answers add no new constraint, and interviews typically run 60 to 120 questions in total across every category.

If the third straight question about finish produces "yeah, same as I said before," the finish category is saturated and the interview moves on, however many questions were planned for it.
A floor guarantees minimum coverage.
Saturation decides when a category is done.

### 11. Verbatim Capture

The archive is the source of truth for the interview, and it preserves your exact words and not a summary of them.
Paraphrasing at capture time throws away the phrasing that carries the taste: your specific vocabulary, hedges, and emphasis are data the compile step needs, not noise to clean up early.

If a woodworker says "I guess dovetails are fine, but honestly, who's checking," the archive records that sentence exactly, hedge and all, and not "prefers dovetails."
Compression is a separate, later step, applied deliberately and never by accident at the moment of capture.

### 12. Interviewer Drift

Long interviews accumulate an inferred pattern that starts to feel confirmed simply because nothing has tested it recently.
Every 20 questions, the interviewer re-reads the ledger and asks at least one question built to disconfirm a pattern it thinks it has found, instead of one more question that would only confirm it.

After 20 questions suggesting a strong preference for hand tools, the disconfirming question is not "you really do prefer hand tools, right?"
It is "tell me about a project where a power tool was clearly the better call, and you took it without a second thought."
An interview that never tries to break its own pattern reports the pattern with more confidence than the evidence earns.

### 13. Unknown-Unknowns Pass

Before the substantive interview begins, the plugin names 3 to 5 dimensions you likely have real taste about but would not think to raise, because the dimension is invisible to you until it is named.
Skipping this pass leaves whole categories of judgment uncaptured, not because you had nothing to say about them, but because no one asked.

A woodworking profile scoped around "joinery and finish" might miss your opinions on shop layout discipline, tool maintenance habits, or how much a piece should reveal the maker's hand versus disappear into the room it sits in.
Naming these up front catches taste the initial scoping conversation would miss.

### 14. The Keep/Cut Test

When an interview is compressed into a profile, a line earns its place only if removing it would change how a downstream system writes, judges, edits, refuses, or decides something.
Biography, general values statements, and flattering self-description are cut, however central they felt during the interview, unless they change an actual output.

"I've been woodworking for twenty years" is cut, because it changes nothing downstream.
"Never use pocket screws on anything that will be seen" is kept, because it is a direct, checkable instruction.
The test is mechanical, not sentimental: ask what output would differ, and if the answer is nothing, the line goes.

### 15. Calibration Is the Moat

An interview alone produces a plausible-looking profile, not an accurate one.
Accuracy comes from testing the profile against real output and folding the corrections back in, repeatedly, until the corrections stop mattering as much.
A profile is not done until three calibration rounds show non-increasing correction volume.
The precise test is in the [profile.md reference](formats/profile.md).
Anything short of that is a draft wearing the shape of a finished profile.

Example: round one of a woodworking profile might produce a project plan that violates three named rules.
Round two, after fold-back, violates one.
Round three violates none.
That downward trend, and not the quality of the first draft, is what makes a profile trustworthy enough to hand to a skill.

### 16. Elicitation Technique Index

Different interviewing techniques surface different kinds of judgment, and no single technique surfaces all of them.
This table maps each technique to the situation where it earns its cost.

| Technique | When to Use |
|---|---|
| Repertory grid (triads) | Present three artifacts and ask which two share a quality the third lacks. Surfaces dimensions the person has never named on their own. |
| Critical incident | Ask for a specific time a decision went visibly right or wrong, in detail. Surfaces judgment tied to a real event rather than a general claim. |
| Think-aloud review | Have the person narrate their reaction to an artifact in real time, before they have composed an opinion. Catches instinct ahead of rationalization. |
| Sorting | Give a stack of artifacts and ask for a rank order or a grouping. The boundaries drawn reveal categories the person would not state directly if asked. |
| Boundary probing | Ask for the least acceptable version of something the person would still tolerate. Finds the edge of a standard rather than just its comfortable center. |
| Verdict battery | Three to six closed items in one category, each answerable with a stance and a sentence. Use it once a category's shape is known and what remains is collecting verdicts. |
| Evidence probe | Present researched practice with sources and ask the person to ratify, adjust, or reject it. The reaction to evidence is taste data in its own right. |

A repertory grid works early, when the category map is still forming and the goal is finding dimensions.
A critical incident works mid-interview, when a category needs grounding in something specific rather than another round of hypotheticals.
Boundary probing works well late, once enough context exists to know what "acceptable" even means for this person.
A verdict battery works once a category's shape is known, and a surprising answer to one item earns an open follow-up.
An evidence probe works whenever you defer to outside practice or ask for research: the findings are shown with their sources, and your reaction is logged as you give it.

## How the Stages Use the Rules

[Design](stages/design.md) reads the rules before it scopes an interview, so the category map and question seeds are built on them and not reinvented per domain.
[Interview](stages/interview.md) reads them before it asks a question, and returns to rule 12 every 20 questions as the disconfirmation check.
[Compile](stages/compile.md) applies rule 14 as its literal compression test, and rule 1 to decide when a divergence becomes a recorded tension and not a resolved preference.
[Calibrate](stages/calibrate.md) exists because of rule 15: an interview seeds a profile, and calibration is what earns the profile the right to be trusted.

None of the rules is optional per domain.
A domain can add category slots, change vocabulary, or skip a technique that does not fit its artifacts, but it cannot skip a rule.
The rule is what makes the resulting profile change how a system behaves instead of merely describing a person.
