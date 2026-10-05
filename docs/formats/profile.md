# profile.md

`profile.md` is the pipeline's core artifact: the compressed, calibrated statement of how you judge in a domain.
[Compile](../stages/compile.md) writes it from `archive.md`.
[Calibrate](../stages/calibrate.md) edits it round by round.
[Skillify](../stages/skillify.md) copies it, unchanged, into the produced or augmented skill's `references/profile.md`, where it becomes canon.

This page covers the frontmatter, the fixed sections in the order the XML body must carry them, and the two hard contracts that the structure check tests mechanically: the `golden_examples` triple and the token ceiling.

## Template

The body is XML-style tags inside one `<profile>` root.
This is the skeleton, with the section contents shortened.

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

<identity_context>...</identity_context>
<judgment_fingerprint>...</judgment_fingerprint>
<domain_laws>
<law>Do: X. Avoid: Y. Example: Z.</law>
</domain_laws>
<communication_laws>
<law>...</law>
</communication_laws>
<hard_refusals>
<never>Never X. Bad: ... Use: ...</never>
</hard_refusals>
<taste_loves>...</taste_loves>
<taste_disgusts>...</taste_disgusts>
<phrase_bank>
<use>...</use>
<avoid>...</avoid>
</phrase_bank>
<signature_tells>...</signature_tells>
<decision_rules>...</decision_rules>
<productive_contradictions>
<tension>[Stated position] vs. [observed exception]. Preserve by: [the instruction that keeps both true instead of forcing a resolution].</tension>
</productive_contradictions>
<golden_examples>
<example>
<context>...</context>
<bad>...</bad>
<good>...</good>
<why>...</why>
</example>
</golden_examples>
<do_not_infer>...</do_not_infer>
<calibration_state>
<rounds>N</rounds>
<last_date>YYYY-MM-DD</last_date>
<last_correction_count>N</last_correction_count>
</calibration_state>
<final_instruction>...</final_instruction>

</profile>
```

## Frontmatter Fields

- `domain`: the same slug used across `interview-spec.md` and `archive.md`, matching the extraction directory name.
- `registers`: copied from `interview-spec.md` at compile time, the contexts this profile covers.
- `consumer`: copied from `interview-spec.md`, a plain-language statement of what the future skill does with the profile.
  The consumer states the job, and `judgment_fingerprint` states how you do it.
- `target_skill`: the same augment-or-greenfield signal as `interview-spec.md`, in the same three forms.
  Skillify reads it to decide whether to produce a diff against an existing skill or scaffold a new one.
- `version`: a date stamp, `YYYY.MM.DD`, with `.N` appended for a second stamp the same day.
  Compile stamps it when it first writes `profile.md`.
  Calibrate restamps it whenever a fold-back materially changes the file.
  Skillify never bumps this or any plugin version.
- `token_estimate`: the profile body's estimated size, characters divided by four, with no tokenizer dependency.
  Compile reports it, and compile and calibrate keep the line current with `scripts/update_token_estimate.py`.
  The structure check recomputes it independently.
  The check fails above the 10,000 hard ceiling and flags a stored estimate that disagrees with its own recount.
- `calibrated`: `true` once three consecutive calibration rounds show non-increasing correction counts and the most recent round is at or under `calibration_threshold` from `interview-spec.md`.
  Otherwise `false`.
  Calibrate is the only stage that flips this field.

## Section Reference

The seventeen sections appear in this fixed order inside the `<profile>` root: `usage`, `priority`, `identity_context`, `judgment_fingerprint`, `domain_laws`, `communication_laws`, `hard_refusals`, `taste_loves`, `taste_disgusts`, `phrase_bank`, `signature_tells`, `decision_rules`, `productive_contradictions`, `golden_examples`, `do_not_infer`, `calibration_state`, `final_instruction`.
The structure check tests presence and this exact order.
A section moved out of sequence fails the same way a missing section does.

**usage.**
States when this profile applies, which skill or command loads it, and the standing fallback: when the profile does not cover a case, flag it rather than guess.

**priority.**
Fixed text, reproduced verbatim in every profile regardless of domain: the six-rule precedence order every downstream consumer applies when rules collide.
Compile writes it unchanged, and nothing in the interview or calibration loop edits it.

**identity_context.**
The background facts that shape how you judge in this domain: upbringing, training, credentials held or deliberately withheld from argument, and any register boundary the interview surfaced.

**judgment_fingerprint.**
How you judge in this domain, operationally, and not what you produce.
It states what you notice first, what you weigh against what, and where your threshold for good sits, in the registers this profile covers.

**domain_laws.**
One `<law>` entry per rule, each in the fixed shape "Do: X. Avoid: Y. Example: Z."
The example clause is not optional decoration.
A law without a concrete example is a rule a weaker consumer model will apply inconsistently.

**communication_laws.**
How you communicate about or around this domain, distinct from the domain artifacts themselves: how you give and receive feedback, handle disagreement, and frame teaching.

**hard_refusals.**
One `<never>` entry per refusal, each in the fixed shape "Never X. Bad: ... Use: ..."
These override ordinary preferences per the priority block.
Each pairs a concrete bad example with the concrete alternative you actually use, never a bare prohibition.

**taste_loves.**
Named precedents, people, or work you hold up as the standard in this domain, each with what specifically earns the admiration.
A love without a name attached is a category, and categories belong in `judgment_fingerprint`.

**taste_disgusts.**
Named failure modes you cannot stand in this domain, held to the same concreteness bar as `taste_loves`.

**phrase_bank.**
How you name things in this domain: your words for what counts as good and what counts as bad, split into `<use>` and `<avoid>` lists.
It stays in the format for non-writing domains, since practitioners have a working vocabulary for quality and failure everywhere.

**signature_tells.**
Recognizable structural habits and recurring devices, distinct from `domain_laws`: the patterns a reader or reviewer would recognize as yours with no byline attached.

**decision_rules.**
Named tests and heuristics you apply to reach a judgment in this domain, the kind of question you ask yourself before deciding something is right.

**productive_contradictions.**
One `<tension>` entry per unresolved conflict: a stated position against an observed exception, followed by "Preserve by:" and the instruction that keeps both true instead of collapsing them into a false compromise.
These come from the archive's contradiction ledger, per [rule 1](../method.md#1-stated-vs-revealed-preference).

**golden_examples.**
Three to six `<example>` entries, each carrying all three of `<bad>`, `<good>`, and `<why>`.
This is a hard contract.
The structure check tests every example for all three children, and an example missing any one fails regardless of how good the other two are.
The `<why>` names the specific rule or judgment the bad-to-good change demonstrates.

**do_not_infer.**
Explicit boundaries: generalizations the archive does not support, categories the interview declined to engage, and inferences a consumer of this profile must never make on its own.
Compile writes this section from what the archive did not say as much as from what it did.

**calibration_state.**
A compact record of calibration history: `<rounds>`, the count of rounds run so far, `<last_date>`, the date of the most recent round, and `<last_correction_count>`, the correction count from that round.
It mirrors the README's "calibrate rounds, last count" column, but lives inside the profile so a consumer loading only `profile.md` still knows how tested the file is.
The zero state, for a profile compile has just written, is `<rounds>0</rounds>`, `<last_date>none</last_date>`, `<last_correction_count>none</last_correction_count>`.

**final_instruction.**
The closing instruction: apply the profile silently, protect your judgment over surface style when rules conflict per the priority block, and flag rather than guess when a case falls outside what the profile covers.

## The Token Contract

Compile targets 2,000 to 4,000 tokens for a single-register profile body, more when the domain carries several registers, with a hard ceiling of 10,000 at any register count.
Token count is estimated as characters divided by four, with no tokenizer dependency.
Compile reports its estimate in the `token_estimate` frontmatter field, and `scripts/update_token_estimate.py` corrects that line after compile and after each calibration fold-back.
The structure check recomputes the same estimate from the body.
The ceiling is a padding guard, not a compression target: the keep/cut test and the compile log keep a profile honest, and a line that changes downstream output is never cut to make a number.
`profile.md` is a reference file the produced skill loads on trigger, not the skill body, so size guidance written for a skill body does not apply to it.
Reference points: a single-register profile measures about 4,900 tokens, and a four-register profile compiled from a 100-question archive measures about 7,500.
It is not a reason to raise the ceiling.
