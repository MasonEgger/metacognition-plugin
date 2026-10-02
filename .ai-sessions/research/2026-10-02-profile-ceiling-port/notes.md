# Profile Ceiling Port: Intake Notes

Written 2026-10-02, the day the first phase shipped as `v0.1.0`.
This is the "python-branch port" on the spec's Upcoming list.
Nothing here has been implemented.

## What Changes

The profile token ceiling rises from 5,000 to 10,000.
The compile target of 2,000 to 4,000 tokens stays, but it becomes the target for a single-register profile, with more allowed when the domain carries several registers.
The 10,000 ceiling holds at any register count.

The reason, from the private spec's note dated 2026-09-30: a four-register profile compiled from a 100-question archive could not fit under 5,000 without cutting lines that passed the keep/cut test.

Two measured reference points come with the change:

- A single-register profile measures about 4,900 tokens.
- A four-register profile compiled from a 100-question archive measures about 7,500 tokens.

## The Reasoning That Comes With The Number

The private edit rewrites more than the number, and the port should carry the reasoning too.

- The ceiling is a padding guard, not a compression target. The keep/cut test and the compile log keep a profile honest, and a line that changes downstream output is never cut to make a number.
- `profile.md` is a reference file the produced skill loads on trigger. It is not the skill body, so size guidance written for a SKILL.md body does not apply to it.
- The old sentence said a profile that will not fit means compile cut too little. The new one says a profile over the ceiling means compile kept biography or self-description, so compile returns to the cut step and reads the log again.
- Compile never merges two laws into one to save space, because a merged law is applied less reliably than two atomic ones.

## State Of The Source

The edits sit uncommitted in the private repo's working tree, on the `python-taste-extraction` branch, on top of commit `0ac7f20`.
There is no commit to pin them to.
The first phase read the private repo only through `git show` at a pinned commit and never from the working tree, so this port needs one of two things before it starts:

1. The maintainer commits the private edits, and the port reads that commit.
2. The port is written here from these notes, with no further read of the private repo.

Option 2 is workable, since the change is nine files and under twenty lines and everything it says is recorded above.
The private diff also touches the private spec and an eval file layout this repo does not share, so a line-for-line port would not apply cleanly anyway.

## Files To Change Here

Source of truth, then re-sync with `just sync`:

- `src/references/profile-format.md`: the `token_estimate` field note (line 118) and the Token Contract section (lines 179 to 181), which gains the padding-guard and reference-file sentences and the two reference points.
- `src/references/interview-spec-format.md`: the `compile tokens` column note (line 111).
- `src/scripts/validate_artifacts.py`: the docstring line that says the ceiling is 5,000 in this phase (line 17) and `TOKEN_CEILING` (line 63).

Skills:

- `metacognition/skills/compile/SKILL.md`: the target sentence (line 91), the over-ceiling sentence (line 95), and the by-hand fallback (line 108).
- `metacognition/skills/calibrate/SKILL.md`: the by-hand fallback (line 102).

Tests and fixtures:

- `tests/test_validate_artifacts.py`: the oversize test's docstring and its assertion on the finding text (lines 225 and 230).
- `tests/fixtures/extractions-bad/oversize-profile/profile.md`: the body must exceed 10,000 tokens, and `token_estimate` (now 5263) must be recomputed from the new body so the case still yields the ceiling finding only.

Evals:

- `evals/compile/evals.json` and `evals/README.md`.

Docs pages that restate the references, in the same pull request:

- `docs/stages/compile.md` (line 31), `docs/formats/profile.md` (lines 96 and 175), `docs/formats/interview-spec.md` (line 146).

Project documents:

- `spec.md`: the Upcoming entry (line 104), the `validate_artifacts.py` component line (line 150), and the checks list (line 281).
- `CLAUDE.md`: the Conventions line that says the ceiling is 5,000 in this phase.

## What To Watch

- The validator change is test-first: change the test and the fixture, see the failure, then change the constant.
- The validator's finding text includes the ceiling value, and one test asserts on it.
- The fixture is the only bad case that should fire the ceiling finding, and it should fire that finding only. The estimate mismatch check runs on the same file, so the stored estimate has to match the recount exactly.
- The reference points in the private text name a private skill and a private extraction. The public text keeps the two measurements and drops the names.
- This repo's compile skill tells the reader to count characters, not bytes. Keep that wording; do not copy the private sentence that says byte length.
- 37 synced files are generated. Change `src/`, run `just sync`, and commit the copies.
- Whether the change ships as a new beta version is the maintainer's ruling. A version change in the manifests publishes a release on merge.

## Relation To The Interview Retro

The interview retro (`.ai-sessions/research/2026-09-30-interview-retro/retro.md`) came out of the same extraction.
The two pieces of work are independent: this one is small and mechanical, and the retro changes a spec invariant and needs the maintainer's answers first.
The ceiling port can land on its own, ahead of the retro work.
