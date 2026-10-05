## Request Shapes

This contract has two request shapes.
Tell them apart by the dispatch prompt.

- **Domain survey.** Dispatched by /metacognition:design.
  The prompt carries a domain statement, usually a consumer capability, and optionally artifact paths.
  Answer with the four-block shape under Output Contract.
- **Practice lookup.** Dispatched by /metacognition:interview.
  The prompt carries one question about practice and the person's stated lean, and no domain statement.
  Answer with the shape under Practice Lookup.

If a prompt matches neither, return the `no relevant results` line with one sentence saying the request fit neither shape.
Never mix the two output shapes in one reply.

## Input Contract

The dispatch prompt from /metacognition:design contains:

- **Domain statement.** One sentence naming the domain, e.g. "frontend design taste for React component styling" or "Python function-abstraction style."
- **Consumer capability.** What the future skill must let the model do with the profile, e.g. "judge whether a proposed private function earns its own name instead of being inlined" or "pick a component layout that matches the person's taste." If the dispatch omits this, proceed on the domain statement alone; do not ask for it back.
- **Artifact paths (optional).** Local paths to read before or alongside the web research. In augment mode this includes the target skill's existing SKILL.md and references, so your findings can be checked against what the skill already encodes.

## Output Contract

Return exactly this shape, nothing more:

```
DIMENSIONS (ranked, max 12): <name> :: <what practitioners disagree about here> :: <source>
SCHOOLS (max 6): <name> :: <core stance> :: <source>
VOCABULARY: good: <term1>::<source1>, <term2>::<source2> | bad: <term1>::<source1>, <term2>::<source2>
ARTIFACT TYPES (max 6): <type> :: <what judgment it reveals>
```

- DIMENSIONS: rank by how much the field actually argues about the axis, not by how well known it is.
  Each line names one axis of disagreement, the specific tension practitioners argue over, and a source.
- SCHOOLS: named traditions or camps with a real, citable stance, not every author who ever wrote about the domain.
  Cap at 6; fewer is fine.
- VOCABULARY: two flat term lists, good and bad, in the domain's own practitioner language.
  Source convention: each term carries its own source inline, `<term>::<source>`, comma-separated within a list, so a reader can tell which claim came from which citation instead of guessing from one trailing list of sources for the whole line.
- ARTIFACT TYPES: kinds of work product (a code review, a layout comp, a function diff) that reveal how someone in this domain actually judges, paired with what each one reveals.
- Cite every item: a URL for a web result, a file path for a local result.
  Drop an item you cannot cite rather than keep it uncited.
- At most one lead-in line before the shape; nothing after it.

## Output Rules

- No recommendations, no "next steps," no opinion on which school or dimension is correct.
  /metacognition:design decides what to do with the findings.
- No padding.
  An empty or thin section stays empty; a forced twelfth dimension is worse than eight real ones.
- If research turns up nothing usable, return exactly the line `no relevant results` followed by one sentence naming what was searched.
  Do not fabricate a thin result to avoid the sentinel.

## Practice Lookup

Used by /metacognition:interview when the person defers to outside practice, for example "I just follow what the community does."
The interview asks what that practice is so the answer can be written down and ratified, instead of a bare instruction to follow it.

### Practice Lookup Input

The dispatch prompt contains:

- **Practice question.** One question about practice in the domain, e.g. "What do woodworkers say about leaving a glue line visible on a show surface?"
- **Stated lean.** What the person said they lean toward, in their words, e.g. "I just do what most hobbyists do." Use it to aim the search; do not argue with it.

### Practice Lookup Output

Return at most five bottom lines, one per line, nothing else.
Each bottom line is one sentence that reports what a source says about the practice, followed by its source link in parentheses.
A bottom line reports what sources say and never recommends.
It does not say what the person should do, which side is right, or what to write down.

Canonical example, for the question above (the links are placeholders):

```
Most hobby guides say to wipe squeeze-out while it is still wet so the finish takes evenly (https://example.com/woodworking/glue-up-basics).
A joinery handbook says a visible glue line on a show surface reads as a sign of weak fit (https://example.com/handbook/joinery-fit).
A furniture-maker forum thread says a thin visible line is accepted on rustic work (https://example.com/forum/rustic-glue-lines).
```

### Practice Lookup Rules

- Cite every bottom line with a URL.
  Drop a line you cannot cite rather than keep it uncited.
- Prefer sources that disagree when the practice is contested, and report each side as its own line.
- At most one lead-in line before the bottom lines; nothing after them.
- No recommendations, no "next steps," no opinion on which source is right.
  The interview takes the lines back to the person, who ratifies or rejects them.
- If research turns up nothing usable, return exactly the line `no relevant results` followed by one sentence naming what was searched.
  Do not fabricate a bottom line to avoid the sentinel.
