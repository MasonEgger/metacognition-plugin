---
name: compile
version: 0.2.0
description: 'This skill should be used when the user asks to "compile the archive for a domain", "compress the interview into a profile", "compile a domain slug into profile.md", "run compile on the completed interview", or runs `/metacognition:compile`. Compresses a completed interview archive into the compressed `profile.md`, applying the keep/cut test to every candidate line and logging every cut to `compile-log.md`. It never asks the person a new taste question; that is the job of `/metacognition:interview`.'
compatibility: 'Runs on Claude Code, Cowork, and claude.ai. The scripts need code execution and Python 3.12 or newer; without them the skill applies the same rules by hand. It reads the extraction files design and interview wrote and writes profile.md and compile-log.md in the same directory, so it needs file access or the files uploaded to the conversation.'
---

# Compile

Compress a completed interview archive into `profile.md`, the pipeline's core artifact.
Compile is the compressor, not the interviewer.
It reads `archive.md` end to end and decides what survives; it never opens a new line of questioning the person has not already answered.

## Arguments

- `[domain-slug]`: optional. The extraction to compile; see Preflight for how it defaults.
- `--extractions-root <dir>`: optionally overrides the extraction root.

## Read First

Read `references/extraction-theory.md` rule 14, the keep/cut test, before applying it to a single candidate line.
The test in one line: a line earns its place in `profile.md` only if removing it would change how a downstream system writes, judges, edits, refuses, or decides something; biography and flattering self-description are cut regardless of how central they felt in the interview.
Also read extraction theory rule 1 (stated vs revealed preference) and rule 8 (contradiction detection): together they govern how a divergence in the archive becomes a `<tension>` entry rather than a line compile quietly resolves on the person's behalf.
This skill does not re-derive any of the three rules; `extraction-theory.md` is the single source.

Then read `references/profile-format.md` in full.
It is the single source for `profile.md`'s frontmatter fields, its seventeen sections in fixed order, the `golden_examples` triple contract, and the token ceiling; this skill does not restate any of it, only applies it.

## Preflight

1. Read the arguments: `[domain-slug]` is optional; `--extractions-root <dir>` optionally overrides the default root.
2. Resolve settings and the extraction root.
Run `python3 scripts/resolve_config.py`, passing `--extractions-root <dir>` when that flag was given and `--set key=value` for any setting the person stated in the conversation or in Project instructions.
Read the JSON it prints, relay any `Loaded config from: <path>` line it printed, and state the root in one line: "Extraction root: `<path>`".
When the script cannot run (no code execution, or an interpreter older than Python 3.12), apply the same tiers by hand from `references/settings.md`, and say so in one line.
3. Resolve the slug: if `[domain-slug]` was passed, use it directly; if it was omitted, use the only extraction under the root and error if there are zero or several, naming each candidate slug in the error so the person can retry with one named.
4. Load `<extractions-root>/<slug>/interview-spec.md`.
Missing means there is nothing compile can ground its frontmatter in; stop and name `/metacognition:design <domain>` as the prerequisite.
Read `registers`, `target_skill`, and `consumer` from its frontmatter; the profile's own frontmatter carries these three unchanged, per `references/profile-format.md`.
5. Load `<extractions-root>/<slug>/archive.md`.
Missing means there is nothing to compile yet; stop and name `/metacognition:interview <domain-slug>` as the prerequisite.
6. Check the archive's `status` field.
`status: complete` continues to compression.
`status: in-progress` is a hard refusal: state that the interview is not finished and name `/metacognition:interview <domain-slug> --resume` as the prerequisite, then stop.
Compile never compresses a partial archive; a partial archive means categories the interview has not saturated yet, and compiling early would bake gaps into `profile.md` that read as settled judgment.

## Runs In-Session

Compile runs in-session, never dispatched as a subagent.
The archive runs 20,000 to 30,000 tokens, and the person may want to answer a clarifying question mid-compression, for example when a candidate line's context is ambiguous or a cut needs their confirmation before it is logged.
A subagent dispatch would lose that back and forth entirely.
Clarifying questions about material already in the archive are allowed at any point in the procedure below.
What compile never does, in-session or otherwise, is ask a new taste question: any question that would extend the interview's substantive content belongs to `/metacognition:interview`, not here.

## The Seven-Step Procedure

### 1. Read the Inputs

Read extraction theory rule 14 and `references/profile-format.md` per Read First above, then read the extraction's `interview-spec.md` for the three frontmatter fields `profile.md` carries forward unchanged: `registers`, `target_skill`, and `consumer`, the plain-language statement of what the future skill must do with the profile.
`consumer` is what `judgment_fingerprint` operationalizes in step 6; read it before drafting that section, not after.

### 2. Extract Every Candidate Line

Read `archive.md` end to end and pull out every candidate: a rule, a refusal, a phrase the person actually uses, a concrete example, a decision rule or named test, and every entry already flagged in the `## Contradiction ledger`.
A candidate is a claim traceable to a specific `### Qnn` answer, never a paraphrase invented to fill a section the archive did not actually earn.
A battery entry holds several verdicts; each is its own candidate rule, traced to its `Qnn` and item number.
An answer that is only a selected label is the person's choice, and the option text in the `Q:` line is the interviewer's wording, not a quote of the person; never put it in the profile as their phrase.
Read the archive's `## Open research` and `## Exports` sections here too; steps 3 and 7 say what each becomes.
A ratified practice (an `evidence` entry) compiles to the written practice with its citation.
Never write a bare instruction to follow community practice.

Rules about how the person wants judgment exercised are profile content, not cuts: when to reconsider a past decision, whose decisions outrank an adopted outside reference, removing before adding, how to raise a discouraged pattern, and what posture to take where nothing is codified.
Place them in the existing sections, and add none.
`decision_rules` takes the first three, `communication_laws` takes how to raise a discouraged pattern, and `usage` takes the posture for uncodified ground.

### 3. Apply the Keep/Cut Test

Run extraction theory rule 14 against every candidate from step 2: does removing this line change how a downstream system writes, judges, edits, refuses, or decides something?
A line that passes is kept; a line that only describes the person, states a general value, or flatters without a checkable instruction attached is cut.
Log every cut to `<extractions-root>/<slug>/compile-log.md`, one entry per cut, each naming the candidate line, its source `### Qnn`, and the reason it failed the test, so the person can rescue anything wrongly cut on first read of the log.
Export content (taste voiced about another skill's territory) stays out of the profile body; copy the archive's `## Exports` list into `compile-log.md` under its own `## Exports` heading, apart from the cuts.
A cut with no logged reason is not a completed cut; the log is the record of every judgment call this step made, not only the ones compile is confident about.

### 4. Encode Tensions, Never Resolve Them

For every divergence the archive surfaced between what the person said about themselves and what an artifact or the contradiction ledger actually shows, per extraction theory rule 1, write a `<tension>` entry in `profile.md`'s `productive_contradictions` section rather than picking a winner.
Draw the register-dependent and unresolved entries from the archive's `## Contradiction ledger` directly, per extraction theory rule 8: an `unresolved` ledger entry becomes a `<tension>` here, never a forced single rule.
Every `<tension>` entry states the stated position, the observed exception, and a "Preserve by:" instruction that keeps both true, per `references/profile-format.md`'s fixed shape.
Compile never resolves a tension on the person's behalf; that is what the fixed shape exists to prevent.

### 5. Golden Examples

Assemble three to six `<example>` entries for `golden_examples`, each a bad/good pair drawn from the archive's own artifact-grounded answers or the interview spec's forced-choice bank, never invented from scratch.
Every entry carries all three children, `<bad>`, `<good>`, and `<why>`; `references/profile-format.md` treats this as a hard contract, and `python3 scripts/validate_artifacts.py` fails an example missing any one of the three regardless of how strong the other two read.
The `<why>` names the specific rule or judgment the bad-to-good change demonstrates, so a consumer reading only this section can reconstruct the law behind the example without reading the rest of the profile.

### 6. Emit profile.md

Write `<extractions-root>/<slug>/profile.md` per the fenced template and section order in `references/profile-format.md`: frontmatter (`domain`, `registers`, `consumer`, `target_skill`, `version` stamped `YYYY.MM.DD`, `token_estimate`, `calibrated: false`, since no calibration round has run yet), then the seventeen fixed sections in order.
The `priority` section is fixed text, reproduced verbatim per `references/profile-format.md`; nothing in compile edits it.
Target the profile body at 2,000 to 4,000 tokens for a single-register domain, more for several registers, with a hard ceiling of 10,000.
Write `profile.md` with a `token_estimate` line, then correct that line by command, never by eyeballing the file: run `python3 scripts/update_token_estimate.py <extractions-root>/<slug>/profile.md`.
The script requires the line to exist, counts everything after the closing frontmatter delimiter in characters divided by four, the number `scripts/validate_artifacts.py` recounts independently, and rewrites the line when it is stale.
It prints `<path>: updated <old> -> <new>` or `<path>: current (<n>)`.
When the script cannot run (no code execution, or an interpreter older than Python 3.12), compute the same figure by hand and write it to the line: `python3 -c "import pathlib; print(len(pathlib.Path('<extractions-root>/<slug>/profile.md').read_text(encoding='utf-8').split('---\n', 2)[2]) // 4)"`, or equivalently `wc -m` on the same tail slice.
Report the value the script printed to the person directly at the end of the run, alongside the compiled section count, so they see the number compile is claiming before they ever open the file.
A profile over the 10,000-token ceiling means step 3 kept biography or self-description; return to step 3 and re-read the log, but never cut a line that passes the keep/cut test to make the number, and never merge two laws into one to save space, since a merged law is applied less reliably than two atomic ones.
Update the extraction README's `compile tokens` cell with the same figure, per `references/interview-spec-format.md`'s standing rule that every pipeline stage updates the table as its last action.
Set the body's `<calibration_state>` section to `profile-format.md`'s zero state, since no calibration round has run yet: `<rounds>0</rounds>`, `<last_date>none</last_date>`, `<last_correction_count>none</last_correction_count>`.

### 7. Emit do_not_infer

Write the `<do_not_infer>` section from what the archive did not say as much as from what it did: generalizations the archive does not support, categories the interview spec's unknown-unknowns pass marked `declined`, and any inference a consumer of `profile.md` must not make on its own.
A domain the archive never touched belongs here, explicitly named, rather than left for a consumer to guess at.
An `## Open research` line still marked `unresolved` is listed here as not yet settled.

### Closing Self-Check

After `profile.md` and `compile-log.md` are both written, run `python3 scripts/validate_artifacts.py <extractions-root>/<slug>` against the extraction and resolve every finding it reports before telling the person compile is done.
A finding here, a missing section, an out-of-order section, an incomplete golden example, a stale `token_estimate`, means the just-written `profile.md` does not satisfy the structural contract downstream stages assume; fix it now, while this session's context is still loaded, rather than leaving it for calibrate or skillify to trip over.
When the script cannot run (no code execution, or an interpreter older than Python 3.12), say so in one line and check the same things by hand against `references/profile-format.md`: the frontmatter parses, the body stays at or under the 10,000-token ceiling counted as characters divided by four, the stored `token_estimate` equals that same count, all seventeen sections are present in the fixed order, and every golden example carries `<bad>`, `<good>`, and `<why>`.

## Finish

End by naming the files written, `<extractions-root>/<slug>/profile.md` and `<extractions-root>/<slug>/compile-log.md`, and the next stage's command, `/metacognition:calibrate <slug>`.
Then stop.

## Inputs and Outputs

- Reads: `references/settings.md` (to resolve settings by hand when the script cannot run); `references/extraction-theory.md` rule 14 (and rules 1 and 8, for the tension shape); `references/profile-format.md` (always, first); `<extractions-root>/<slug>/interview-spec.md` (`registers`, `target_skill`, `consumer`); `<extractions-root>/<slug>/archive.md` (the compiled source, read only, never edited).
All extraction paths resolve against the extraction root, `extractions` under the working directory by default or the configured or passed root.
- Scripts: `python3 scripts/resolve_config.py` resolves the settings, `python3 scripts/update_token_estimate.py` corrects the profile's `token_estimate`, and `python3 scripts/validate_artifacts.py` runs the closing self-check. All three import the sibling parser `scripts/yaml_subset.py`, which a skill never runs on its own.
- Writes: `<extractions-root>/<slug>/profile.md`; `<extractions-root>/<slug>/compile-log.md` (the cuts, then the `## Exports` list); the extraction README's `compile tokens` cell.
- Dispatches: nothing.
Compile runs entirely in-session; it never hands work to a subagent.

## What This Skill Never Does

- Never asks a new taste question.
Every clarifying question in this session is about material already in the archive; the taste questions belong to `/metacognition:interview` alone.
- Never resolves a tension.
A stated/revealed divergence or an `unresolved` ledger entry becomes a `<tension>` entry, per extraction theory rules 1 and 8, and stays unresolved in the profile the same way it stayed unresolved in the archive.
- Never runs as a subagent.
The in-session shape above is deliberate, not a default; the archive's size and the chance the person wants to weigh in mid-compression are why.
- Never authors the person's prose.
Every golden example, phrase, and law in `profile.md` traces back to a specific archive answer or forced-choice entry; compile compresses what is already there, it does not invent new material to fill a section the archive left thin.
- Never auto-chains into calibration.
The person runs `/metacognition:calibrate` on their own schedule; this session's completion is `profile.md` and `compile-log.md` existing on disk, nothing more.
- Never edits `archive.md`.
The archive is read-only from compile's side; any correction to the interview record belongs to a new or resumed `/metacognition:interview` session, not to compile.

## Resources

- [references/settings.md](references/settings.md): the five tiers and two keys, for resolving settings by hand.
- [references/extraction-theory.md](references/extraction-theory.md): rule 14 (the keep/cut test) and rules 1 and 8 (stated vs revealed, contradiction detection), the three rules this skill applies directly.
- [references/profile-format.md](references/profile-format.md): the frontmatter, seventeen-section order, and the golden-examples and token-ceiling contracts this skill writes to.
- [references/archive-format.md](references/archive-format.md): the shape of the input `archive.md` this skill reads, including the contradiction ledger this skill draws tensions from.
- [references/interview-spec-format.md](references/interview-spec-format.md): the format of `interview-spec.md`, the source of the `registers`, `target_skill`, and `consumer` fields this skill copies forward, and the extraction README status table this skill updates.
- [scripts/resolve_config.py](scripts/resolve_config.py), [scripts/update_token_estimate.py](scripts/update_token_estimate.py), and [scripts/validate_artifacts.py](scripts/validate_artifacts.py): the settings resolver, the token-estimate updater, and the structural validator; each imports [scripts/yaml_subset.py](scripts/yaml_subset.py) directly or through `validate_artifacts.py`.
