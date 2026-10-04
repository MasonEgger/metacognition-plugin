# Profile Format

`profile.md` is the pipeline's core artifact: the compressed, calibrated statement of how the person judges in a domain.
`/metacognition:compile` writes it from `archive.md`; `/metacognition:calibrate` edits it round by round; `/metacognition:skillify` copies it, unchanged, into the produced or augmented skill's `references/profile.md`, where it becomes canon.

This reference documents the frontmatter, the fixed sections in the order the XML body must carry them, and the two hard contracts, the `golden_examples` triple and the token ceiling, that `python3 scripts/validate_artifacts.py` checks mechanically.

## The Fenced Template

```markdown
---
domain: <slug>
registers: [<register>, ...]
consumer: <what the future skill must do with this>
target_skill: <plugin>:<skill> | <repo-relative skill dir> | null
version: YYYY.MM.DD
token_estimate: <int>
calibrated: true|false
---

<profile>

<usage>
[When this profile applies, which skill or consumer loads it, and the fallback: when unsure, flag rather than guess.]
</usage>

<priority>
1. Current user instructions override this file.
2. Truth, safety, and task requirements override style imitation.
3. Hard refusals override ordinary preferences.
4. Specific examples override abstract rules.
5. Evidence-backed rules override inferred rules.
6. When rules conflict, preserve the person's deeper judgment over surface style.
</priority>

<identity_context>
[Background facts that shape judgment in this domain: upbringing, training, credentials held or deliberately not invoked, the register boundaries the interview surfaced.]
</identity_context>

<judgment_fingerprint>
[How the person judges in this domain, operationally: what they notice first, what they weigh, how they decide something is good or wrong, in the register(s) this profile covers.]
</judgment_fingerprint>

<domain_laws>
<law>Do: X. Avoid: Y. Example: Z.</law>
</domain_laws>

<communication_laws>
<law>[How the person communicates about or around this domain: giving and receiving feedback, disagreement, teaching frame.]</law>
</communication_laws>

<hard_refusals>
<never>Never X. Bad: ... Use: ...</never>
</hard_refusals>

<taste_loves>
[Named precedents, people, or work the person holds up as the standard in this domain, and what specifically earns the admiration.]
</taste_loves>

<taste_disgusts>
[Named failure modes the person cannot stand in this domain, concrete rather than generic.]
</taste_disgusts>

<phrase_bank>
<use>[How the person names things in this domain: their words for good and bad, terms of art they actually use.]</use>
<avoid>[Vocabulary and phrasing the person does not use, including generic AI-tell vocabulary where relevant to the domain.]</avoid>
</phrase_bank>

<signature_tells>
[Recognizable structural habits and recurring devices, distinct from domain_laws: patterns a reader would recognize as unmistakably the person's even without a byline.]
</signature_tells>

<decision_rules>
[Named tests and heuristics the person applies to reach a judgment in this domain.]
</decision_rules>

<productive_contradictions>
<tension>[Stated position] vs. [observed exception]. Preserve by: [the instruction that keeps both true instead of forcing a resolution].</tension>
</productive_contradictions>

<golden_examples>
<example>
<context>[What situation this example addresses]</context>
<bad>[A plausible but wrong output]</bad>
<good>[What the person would actually produce or approve]</good>
<why>[The specific rule or judgment the bad-to-good change demonstrates]</why>
</example>
</golden_examples>

<do_not_infer>
[Explicit boundaries: generalizations the archive does not support, categories the interview declined to engage, inferences a consumer of this profile must not make.]
</do_not_infer>

<calibration_state>
<rounds>N</rounds>
<last_date>YYYY-MM-DD</last_date>
<last_correction_count>N</last_correction_count>
</calibration_state>

<final_instruction>
[Closing instruction: apply this profile silently, protect the person's judgment over surface style when rules conflict, flag rather than guess when unsure.]
</final_instruction>

</profile>
```

## Frontmatter Fields

- `domain`: the same slug used across `interview-spec.md` and `archive.md`, matching the extraction directory name.
- `registers`: copied from `interview-spec.md` at compile time, the contexts this profile covers.
- `consumer`: copied from `interview-spec.md`, a plain-language statement of what the future skill does with the profile.
  This is what `judgment_fingerprint` operationalizes: the consumer states the job, `judgment_fingerprint` states how the person does it.
- `target_skill`: the same augment-or-greenfield signal as `interview-spec.md`, in the same three forms, `<plugin>:<skill>`, a repo-relative skill directory, or `null` for greenfield.
  Skillify reads this field to decide whether it produces a diff against an existing skill or scaffolds a new one.
- `version`: a CalVer stamp, `YYYY.MM.DD`, with `.N` appended for a second stamp the same day.
  Compile stamps the version when it first writes `profile.md`; calibrate restamps it whenever a fold-back materially changes the file.
  Skillify never bumps this or any plugin version; it only reports what the person may want to bump.
- `token_estimate`: the profile body's estimated size, characters divided by four, no tokenizer dependency, reported by compile and recomputed independently by `python3 scripts/validate_artifacts.py`, which fails above the 10,000 hard ceiling and flags a stored estimate that disagrees with its own recount.
- `calibrated`: `true` once three consecutive calibration rounds show non-increasing correction counts and the most recent round is at or under `calibration_threshold` from `interview-spec.md`, `false` otherwise.
  Calibrate is the only stage that flips this field.

## Section Reference

The seventeen sections appear in this fixed order inside the `<profile>` root: `usage`, `priority`, `identity_context`, `judgment_fingerprint`, `domain_laws`, `communication_laws`, `hard_refusals`, `taste_loves`, `taste_disgusts`, `phrase_bank`, `signature_tells`, `decision_rules`, `productive_contradictions`, `golden_examples`, `do_not_infer`, `calibration_state`, `final_instruction`.
`python3 scripts/validate_artifacts.py` checks presence and this exact order; a section moved out of sequence fails the same way a missing section does.

**usage.** States when this profile applies, which skill or command loads it, and the standing fallback: when the profile does not cover a case, flag it rather than guess.
This is the section a consumer skill's SKILL.md points at to explain why it loads the file at all.

**priority.** Fixed text, reproduced verbatim in every profile regardless of domain, the six-rule precedence order every downstream consumer applies when rules collide: current user instructions override this file; truth, safety, and task requirements override style imitation; hard refusals override ordinary preferences; specific examples override abstract rules; evidence-backed rules override inferred rules; when rules conflict, preserve the person's deeper judgment over surface style.
Compile writes this text unchanged; nothing in the interview or calibration loop should ever edit it.

**identity_context.** The background facts that shape how the person judges in this domain: upbringing, training, credentials held or deliberately withheld from argument, and any register boundary the interview surfaced.
This section grounds `judgment_fingerprint` in lived material rather than abstraction.

**judgment_fingerprint.** How the person judges in this domain, operationally, not what they produce.
For a writing domain this reads close to a style fingerprint; for a code-review or product-selection domain it states what the person notices first, what they weigh against what, and where their threshold for good sits, in the registers this profile covers.

**domain_laws.** One `<law>` entry per rule, each in the compiler's fixed shape: "Do: X. Avoid: Y. Example: Z."
The example clause is not optional decoration; a law without a concrete example is a rule a weaker consumer model will apply inconsistently.

**communication_laws.** How the person communicates about or around this domain, distinct from the domain artifacts themselves: how they give and receive feedback, handle disagreement, and frame teaching.
Unchanged in shape across domains.

**hard_refusals.** One `<never>` entry per refusal, each in the fixed shape: "Never X. Bad: ... Use: ..."
These override ordinary preferences per the priority block, and each pairs a concrete bad example with the concrete alternative the person actually uses, never a bare prohibition.

**taste_loves.** Named precedents, people, or work the person holds up as the standard in this domain, each with what specifically earns the admiration.
A love without a name attached is not a taste statement; it is a category, and categories belong in `judgment_fingerprint`, not here.

**taste_disgusts.** Named failure modes the person cannot stand in this domain, held to the same concreteness bar as `taste_loves`.

**phrase_bank.** Kept in the format for non-writing domains: how the person names things in this domain, their words for what counts as good and what counts as bad, split into `<use>` and `<avoid>` lists.
In a code-review or architecture domain this section still earns its place: practitioners have a working vocabulary for quality and failure, and this is where it lives.

**signature_tells.** Recognizable structural habits and recurring devices, distinct from `domain_laws`: the patterns a reader or reviewer would recognize as unmistakably the person's even with no byline attached.

**decision_rules.** Named tests and heuristics the person applies to reach a judgment in this domain, the kind of question they ask themselves before deciding something is right.

**productive_contradictions.** One `<tension>` entry per unresolved conflict, in the fixed shape: a stated position against an observed exception, followed by "Preserve by:" and the instruction that keeps both true instead of collapsing them into a false compromise.
These come from the archive's contradiction ledger, per extraction theory rule 1: an interview never forces a resolution it did not earn, and compile is not the place to force one either.

**golden_examples.** Three to six `<example>` entries, each carrying all three of `<bad>`, `<good>`, and `<why>`.
This is a hard contract: `python3 scripts/validate_artifacts.py` checks every example for all three children, and an example missing any one of them fails validation regardless of how good the other two are.
The `<why>` is not commentary; it names the specific rule or judgment the bad-to-good change demonstrates, so a consumer reading only this section can reconstruct the law behind the example.

**do_not_infer.** Explicit boundaries: generalizations the archive does not support, categories the interview declined to engage (per the interview spec's unknown-unknowns list), and inferences a consumer of this profile must never make on its own.
Compile emits this section from what the archive did not say as much as from what it did.

**calibration_state.** A compact record of calibration history: `<rounds>`, the count of calibration rounds run so far; `<last_date>`, the date of the most recent round; and `<last_correction_count>`, the correction count from that round.
This mirrors the extraction README's "calibrate rounds, last count" column, but lives inside the profile itself so a consumer loading only `profile.md` still knows how tested the file is.
The test that flips `calibrated` from `false` to `true` is defined once, above, in the `calibrated` frontmatter field entry; this section does not restate it.
The zero state, for a profile compile has just written and calibrate has never touched: `<rounds>0</rounds>`, `<last_date>none</last_date>`, `<last_correction_count>none</last_correction_count>`.

**final_instruction.** The closing instruction: apply the profile silently, protect the person's judgment over surface style when rules conflict per the priority block, and flag rather than guess when a case falls outside what the profile covers.

## The Token Contract

Compile targets 2,000 to 4,000 tokens for a single-register profile body, more when the domain carries several registers, with a hard ceiling of 10,000 at any register count.
Token count is estimated as characters divided by four, deliberately avoiding a tokenizer dependency; compile reports its own estimate in the `token_estimate` frontmatter field, and `python3 scripts/validate_artifacts.py` recomputes the same estimate from the body independently, failing any profile over the 10,000 ceiling and flagging a stored `token_estimate` that disagrees with its own recount.
The ceiling is a padding guard, not a compression target: the keep/cut test and the compile log are what keep a profile honest, and a line that changes downstream output is never cut to make a number.
`profile.md` is a reference file the produced skill loads on trigger, not the skill body, so size guidance written for a skill body does not apply to it.
Reference points: a single-register profile measures about 4,900 tokens, and a four-register profile compiled from a 100-question archive measures about 7,500.
