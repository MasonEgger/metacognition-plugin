# Metacognition Plugin: Implementation Plan

Phase: Interview Retro (issues 4, 9, and 10).
Done means a fresh interview run avoids the five failure modes the retro documents, every recommendation in the retro is implemented by a spec goal R1 to R9, the token estimate script and the Python 3.12 floor of issue 9 are in place (R10 and R11), skillify is grounded in the provider's skill-craft baseline per issue 10 (R12), and archives written before this phase validate unchanged.

## Current Status

Not started.
Fourteen steps across eight sections.

| Section | Steps | State |
|---|---|---|
| 1. Toolchain Floor | 1 | pending |
| 2. Formats and References | 2 | pending |
| 3. Validator | 3 | pending |
| 4. The Scripts | 4 to 6 | pending |
| 5. Research Contract and Agent | 7 | pending |
| 6. The Skills | 8 to 11 | pending |
| 7. Evals and Docs | 12 to 13 | pending |
| 8. Version and Release Readiness | 14 | pending |

## How To Read This Plan

Each step is a prompt for a code-generation LLM.
Feature steps follow RED, GREEN, REFACTOR and test application logic only, never framework or library behavior.
Task steps follow Scope, Tooling, Do, Verify, Document, for wiring, config, docs, and skill text.
Task steps carry a `(task)` marker in the title; Feature steps carry no marker.

### Sources

- `spec.md` is the authority: goals R1 to R12, Components E, G, K, and L, the archive format contract under Component E, and the "Interview retro phase" success criteria.
- `.ai-sessions/research/2026-09-30-interview-retro/retro.md` is the reasoning behind each goal.
- Issues 9 and 10 are the source for R10 to R12. Where an issue's text and the spec differ (the script's location, for one), the spec wins.
- The maintainer's rulings are a comment on issue 4 and are restated in the spec's Roadmap, with the rulings on issues 9 and 10.
- Nothing in this phase reads the private repo.

### Fences This Plan Must Not Cross

From spec Invariants, Non-goals, and the Deferred list:

- Every format change is additive. No existing fixture under `tests/fixtures/` is edited, and each one validates exactly as it does today.
- The seventeen profile sections and their order do not change. No profile section is added.
- Extraction theory keeps sixteen rules. The battery and the evidence probe are rows in rule 16's table.
- Design's scope Q&A stays one question at a time. The turn discipline changes the interview only.
- A skill reaches its own files by relative path only. No `${CLAUDE_PLUGIN_ROOT}` and no `../` in any skill. A skill names only the references and scripts in its own sync slice.
- The choice picker has no common name across surfaces, so the interview calls it "the host's choice picker, when the surface has one".
- `plugin-dev` is recommended, never required. Every instruction that uses it carries a fallback, and no stage fails without it.
- A script a skill invokes ships in that skill's `scripts/` directory, synced from `src/scripts/`. Nothing a skill needs goes in `tools/`.
- Shipped scripts under `src/scripts/` import only the Python standard library and run on Python 3.12 or newer.
- No model pins, no hooks, no MCP servers, no HTML server, no auto-chaining of stages.
- SKILL.md frontmatter carries exactly `name`, `version`, `description`, `compatibility`, within the upload limits.
- `src/` is the single source of truth. Never hand-edit a synced copy; change `src/` and run `just sync`.
- Versions stay uniform and stay at `0.1.1` until Step 14, which sets `0.2.0` everywhere at once.
- No real extraction content, and none of the doctrine guard's private tokens, in any shipped tree or fixture.
- Nothing on the Deferred list is implemented: no HTML redline page, no status dashboard, no new config keys, no `--no-archive` option.

### Order and the Guards

`uv run pytest -q` must pass at the end of every step.
Three guards shape the order:

- The manifest guard fails when a skill names a file its slice does not ship, or a slice ships a file the skill never names. So the interview slice gains `research-contract.md` and `archive_append.py` in Step 8, the same step that makes the interview skill name them, and the compile and calibrate slices gain `update_token_estimate.py` in Step 10 for the same reason. Steps 4 to 6 leave the manifest alone.
- The contract guard holds the agent's contract block equal to `src/references/research-contract.md`. Step 7 edits both together.
- The version guards hold every version source equal, including `pyproject.toml` and the README's beta notice. Step 14 changes them all in one step.

## Section 1: Toolchain Floor

Goal R11.
The Python floor moves to 3.12 before anything else is written.

**Tools:**
- Skills: python:python
- MCPs: none
- Linters: ruff check --output-format=json, uv run mypy

### Step 1: Raise the Python Floor to 3.12 (task)

**NOTE**: Goal R11. The maintainer ruled the floor is 3.12. This is first so every later step writes for 3.12. Do not touch `.ai-sessions/`, the archived plan, or fixture data. The surface check has not been run, so nobody knows the claude.ai sandbox's Python version; the skills' by-hand fallback is what covers an older sandbox, and that sentence must stay in every skill.

```text
1. Scope:
   - Artifacts: pyproject.toml, uv.lock, .github/workflows/ci.yml, the module docstrings under src/scripts/, src/references/ (any file that states the floor), the five metacognition/skills/*/SKILL.md files (the "cannot run" fallback sentences and any compatibility field that names a version), docs/ pages that state the floor, docs/surface-check.md, README.md if it states the floor, CLAUDE.md.
   - Desired end state: the floor is 3.12 everywhere it is stated, CI runs 3.12 and 3.13, and no shipped file still says 3.11.

2. Tooling:
   - Skills: python:python
   - MCPs: none
   - External: uv lock, just sync, just check

3. Do the work:
   - In pyproject.toml set requires-python to ">=3.12", the ruff target to py312, and the mypy python_version if one is set.
   - Run `uv lock`.
   - In .github/workflows/ci.yml change the matrix to 3.12 and 3.13 and update the header comment. Change no action pin.
   - Run `grep -rn "3\.11" --include="*.md" --include="*.py" --include="*.toml" --include="*.yml" . ` excluding .venv, site, dist, .ai-sessions, and uv.lock, and update each remaining statement of the floor to 3.12. A line that records history (the spec's "raised from 3.11" note) stays.
   - Run `just fmt`, since a new ruff target can change what the formatter and linter accept, and fix any new finding in the code, never by loosening the config.
   - Run `just sync`.
   - In docs/surface-check.md, make sure the claude.ai section asks for the sandbox's Python version to be recorded.

4. Verify:
   - The grep above returns only history lines; `just check` exits 0; `python3 tools/sync_skills.py --check` exits 0.

5. Document:
   - CLAUDE.md: the floor is 3.12 and CI runs 3.12 and 3.13.
```

## Section 2: Formats and References

Goals R1, R2, R4, R5, R6, R8.
The three references that define the archive, the interview spec, and the technique table, with the docs pages that restate them.

**Tools:**
- Skills: plugin-dev:skill-development
- MCPs: none
- Linters: python3 tools/prose_scrub.py, python3 tools/sync_skills.py --check

### Step 2: Extend the Archive, Interview Spec, and Technique References (task)

**NOTE**: The contract is the fenced block under "The archive format after the interview retro phase" in spec Component E. The references describe counting and checks that Step 3 implements; that gap inside the branch is expected. Keep every existing rule in these files. The fenced templates are copied verbatim by weaker models, so every example must be canonical.

```text
1. Scope:
   - Artifacts: src/references/archive-format.md, src/references/interview-spec-format.md, src/references/extraction-theory.md, the synced copies under metacognition/skills/*/references/, docs/formats/archive.md, docs/formats/interview-spec.md, docs/method.md.
   - Desired end state: the three references state the format and rules of goals R1, R2, R4, R5, R6, and R8; the three docs pages say the same; the synced copies match src/.

2. Tooling:
   - Skills: plugin-dev:skill-development
   - MCPs: none
   - External: just sync, python3 tools/prose_scrub.py, just docs-build

3. Do the work:
   - In src/references/archive-format.md:
     - Extend the fenced template with the optional "## Open research" and "## Exports" sections, in that order, between the ledger and "## Questions", using the exact line shapes from spec Component E, and add one battery entry and one evidence entry to the template.
     - In the Questions section, add `battery` and `evidence` to the probe type list, state that a battery heading carries `[items: n]` with n from 3 to 6 after the probe tag, and give the battery body shape: the stem on the Q line, n numbered items, a bare A line, n numbered answers. State that every other entry keeps the two-line body.
     - In Frontmatter Fields, state the counting rule (R4): `questions_asked` counts `### Qnn` entries; a category's `asked` counts probes, where a battery counts its items and every other entry counts one. Update the sentence about what the validator recounts to say probes.
     - Add a section for Open research (one line per deferral that could not be researched in the same turn, with status `unresolved` or `resolved in Qnn`) and a section for Exports (one line per topic the person assigned to another skill, destination a skill name or `unassigned`), each saying who writes it and who reads it.
     - Add the picker provenance rule (R3): a picked answer is the selected label verbatim plus any words the person added; option description text belongs in the Q line.
     - Add the capture conventions (R8): a re-dictated answer replaces the earlier one; a question the person did not understand is not logged; archive numbering is authoritative over labels used in conversation.
     - Replace the sentence that says the archive is written "one question at a time" with wording that covers one entry at a time, a battery being one entry.
     - State that `registers` may gain a register that surfaces mid-interview once the person accepts it, replacing "unchanged for the life of the archive".
   - In src/references/interview-spec-format.md:
     - Add a Registers column to the category map: the registers each category's questions target. State that every register in the frontmatter must appear in at least one row.
     - Beside the floor definition, state that floors count probes and that a battery counts its items.
     - In the artifact plan's definition, add the availability note: each local path is recorded as available or unavailable, with the reason.
     - In the README status table rules, state that the `interview n/floor` cell shows probes over the floor sum, may exceed the floor, and is marked complete when the archive's status flips.
   - In src/references/extraction-theory.md, add two rows to rule 16's table and one sentence each to the paragraph after it:
     - Verdict battery: three to six closed items in one category, each answerable with a stance and a sentence; use once a category's shape is known and what remains is collecting verdicts.
     - Evidence probe: present researched practice with sources and ask the person to ratify, adjust, or reject; the reaction to evidence is taste data in its own right.
     - Do not add a rule and do not renumber.
   - Run `just sync`.
   - Update docs/formats/archive.md, docs/formats/interview-spec.md, and docs/method.md to restate the same changes in the reader-facing voice those pages already use. The Method page still says there are sixteen rules.

4. Verify:
   - `python3 tools/sync_skills.py --check` exits 0, `python3 tools/prose_scrub.py` exits 0, and `just check` exits 0.

5. Document:
   - CLAUDE.md: note that the archive format now has two optional sections and two more probe types, and that the validator does not yet enforce them until Step 3.
```

## Section 3: Validator

Goal R4 and Component E.
The validator learns probe counting, the battery check, and the optional sections.

**Tools:**
- Skills: python:python
- MCPs: none
- Linters: ruff check --output-format=json, uv run mypy

### Step 3: Probe Counts, the Battery Check, and Optional Sections in validate_artifacts.py

**NOTE**: An archive with no battery and neither optional section must validate exactly as before; the existing tests are the proof and none of them may change. Build tmp_path archives in tests with a small helper in the test module, the way `_minimal_profile_markdown` does for profiles. The two new fixture directories are synthetic woodworking data in the existing persona's voice; copy `tests/fixtures/extractions/woodworking/interview-spec.md` and `README.md` as the starting point and adapt them.

```text
1. RED: Write validator tests first:
   - Modify tests/test_validate_artifacts.py:
     - Test that an archive whose category frontmatter says asked=6 passes when the body holds one open probe and one battery with [items: 5] in that category.
     - Test that the same archive with asked=2 (counting entries, not probes) fails with archive-category-count only.
     - Test that a battery heading with no [items: n] tag fails with archive-battery-items.
     - Test that [items: 2] and [items: 7] each fail with archive-battery-items.
     - Test that [items: 4] over three numbered items, and over four items but three numbered answers, each fail with archive-battery-items.
     - Test that an [items: 3] tag on a ladder probe fails with archive-battery-items.
     - Test that a well-formed battery passes with no finding.
     - Test that an evidence entry counts one probe toward its category.
     - Test that "## Open research" lines R01, R02 and "## Exports" lines E01, E02 pass, that R01 followed by R03 fails with a finding naming the section, and that an archive with neither section passes.
     - Test that a [closing] battery, if present, touches no category count.
     - Test that tests/fixtures/extractions/woodworking-battery exits 0 with no output.
     - Test that tests/fixtures/extractions-bad/battery-item-mismatch exits 1 with exactly ["archive-battery-items"].
   - Run the tests and confirm the new ones fail for the expected reason before writing any implementation.

2. Document:
   - Update the module docstring's check list in src/scripts/validate_artifacts.py: archive-category-count counts probes, and add archive-battery-items and the optional-section ID check with the exact finding names.

3. GREEN: Write minimal code:
   - In src/scripts/validate_artifacts.py, parse the optional [items: n] tag from question headings, count a battery as n probes in check for category counts, and add the battery check and the section ID contiguity check as named check functions wired into the existing run order after the numbering check.
   - Create tests/fixtures/extractions/woodworking-battery/ with README.md, interview-spec.md (category map with a Registers column), and archive.md holding open probes, at least one battery, one evidence entry, one Open research line, and one Exports line, with frontmatter counts that match by the probe rule.
   - Create tests/fixtures/extractions-bad/battery-item-mismatch/ as a copy of that fixture whose one battery says [items: 4] over three items, and nothing else wrong.
   - Add both to the fixture READMEs under tests/fixtures/extractions/README.md and the bad-case listing, in the style of the existing entries.

4. RED: Add integration tests:
   - Test that every fixture that existed before this step produces the same exit code and the same findings as before (the existing parametrized tests already assert this; confirm they still pass unchanged and add nothing if so).
   - Confirm tests/test_yaml_parity.py covers the two new fixtures' frontmatter and passes.

5. GREEN: Fix anything the integration run exposes, in the validator, never in an existing fixture.

6. REFACTOR: Keep heading parsing in one place: one function that turns a "### Qnn ..." heading into its number, category, register, probe type, and item count, used by every check that reads headings.

7. Update documentation: run `just sync` so the three skills that ship the validator get the new copy.

8. Verify meaningful coverage of the probe count, each battery failure, and the optional sections, then run `just check`.
```

## Section 4: The Scripts

Goals R7 and R10, Components K and L.
Two scripts that replace hand bookkeeping: one appends an archive entry, one keeps a profile's token estimate current.

**Tools:**
- Skills: python:python
- MCPs: none
- Linters: ruff check --output-format=json, uv run mypy

### Step 4: archive_append.py for a Single Entry

**NOTE**: Read spec Component K in full before writing tests. The script edits the frontmatter in place: it rewrites only the `questions_asked` line and the `categories` line and leaves every other byte of the frontmatter alone. Follow the import pattern the other shipped scripts use so the file works both under pytest and as `python3 scripts/archive_append.py` from another directory. Do not add the script to the sync manifest in this step.

```text
1. RED: Write tests first, each working on a copy of a fixture extraction under tmp_path:
   - Create tests/test_archive_append.py:
     - Test that appending an open probe to a copy of tests/fixtures/extractions/woodworking-battery prints the next Qnn (zero-padded, one more than the last heading) on stdout and exits 0.
     - Test that the new entry is the last thing under "## Questions", with the heading "### Qnn [category] [register] [probe: type]" and the two-line Q and A body.
     - Test that questions_asked rises by one and that category's asked rises by one, while every other category's counts and every other frontmatter line are unchanged.
     - Test that the README's interview cell shows the new probe total over the floor sum, and that no other cell changes.
     - Test that validate_artifacts.main on the directory returns 0 after the append.
     - Test that --question-file and --answer-file read UTF-8 files and give the same result as the inline flags.
     - Test that en-dash, em-dash, and curly-quote codepoints in the question and the answer are normalized to their plain forms, and that every other character, including leading and trailing spaces inside the answer and non-ASCII letters, is preserved.
     - Test each error: a missing archive.md, an unparseable frontmatter, a category not in the frontmatter, a missing answer. Each exits 2, prints one line naming the problem, and leaves archive.md and README.md byte-identical.
     - Test that no temporary file is left in the directory after a success or after an error.

2. Document:
   - Module docstring in src/scripts/archive_append.py: the CLI, the effect, the exit codes, and the statement that nothing is written on an error.

3. GREEN: Write minimal code:
   - Create src/scripts/archive_append.py, standard library only, built on scripts.yaml_subset for reading the frontmatter.
   - Validate everything first, then build both new file contents in memory, then write each to a temporary name in the same directory and rename it, archive first.

4. RED: Add integration tests:
   - Test three appends in a row across two categories: numbering stays contiguous, counts add up, and the validator returns 0.
   - Test a subprocess run of the script from another working directory, as tests/test_validate_artifacts.py does for the validator.

5. GREEN: Wire the CLI entry point (`main(argv)` returning the exit code, and the `__main__` guard).

6. REFACTOR: Separate parsing the request, computing the new archive text, and computing the new README text into three functions with no file access, so only one function touches the disk.

7. Update documentation: none beyond the docstring.

8. Verify meaningful coverage of the counters, the README cell, the normalization, and each error, then run `just check`.
```

### Step 5: Batteries, Closing Questions, and Section Lines in archive_append.py

**NOTE**: Builds on Step 4. A battery's question text is the stem followed by numbered item lines; its answer text is numbered answer lines. The script counts the numbered lines itself and refuses a mismatch with `--items`.

```text
1. RED: Write tests first:
   - Modify tests/test_archive_append.py:
     - Test that --probe battery --items 3 with three numbered items and three numbered answers writes the heading with "[probe: battery] [items: 3]" and the battery body shape from spec Component E, raises questions_asked by one and the category's asked by three, and leaves the validator at 0.
     - Test that --items outside 3 to 6, --items that disagrees with the numbered lines, and --items with a probe type other than battery each exit 2 and write nothing.
     - Test that --probe battery without --items exits 2 and writes nothing.
     - Test that --closing writes the heading with the [closing] pseudo-category, raises questions_asked by one, changes no category count, and leaves the README cell's probe total unchanged.
     - Test that --saturated sets that category's saturated flag to true and leaves the others alone.
     - Test that --ledger, --export, and --research each append one line to the matching section with the next ID (L, E, R), and that the Open research and Exports sections are created in the spec's order the first time a line is added to them.
     - Test that an evidence entry (--probe evidence) counts one probe.
     - Test that a run combining a battery, --saturated, and --export applies all three in one write and the validator returns 0.

2. Document:
   - Extend the module docstring with the battery, closing, and section-line flags.

3. GREEN: Extend src/scripts/archive_append.py to pass the new tests.

4. RED: Add integration tests:
   - Test a short scripted interview on a copy of the woodworking-battery fixture: an open probe, a battery, an evidence entry with a research line resolved, an export, a saturated flip, and a closing question, then the validator returns 0 and the README cell matches the probe total.

5. GREEN: Fix anything the scripted run exposes.

6. REFACTOR: One table that maps a section flag to its heading and ID prefix, used for all three sections.

7. Update documentation: none beyond the docstring.

8. Verify meaningful coverage of every flag and every refusal, then run `just check`.
```

### Step 6: update_token_estimate.py

**NOTE**: Goal R10 and spec Component L. The estimate must be the validator's own number, so both call one function; put it where both can import it without a new module in any slice that does not ship both. Follow the conventions Steps 4 and 5 set in archive_append.py: `main(argv)` returning the exit code, exit 2 with one line for a bad input, a write by temporary file and rename, and the sibling-import pattern. Do not add the script to the sync manifest in this step; Step 10 does that with the skill text.

```text
1. RED: Write tests first, each on a profile under tmp_path built with a small helper:
   - Create tests/test_update_token_estimate.py:
     - Test the arithmetic: a body of exactly 4,000 characters gives 1000, and 4,003 characters gives 1000 (integer division), counting characters, not bytes, with a non-ASCII character in the body.
     - Test that a profile whose stored estimate matches exits 0, reports it is current, and leaves the file byte-identical.
     - Test that a stale profile is rewritten in default mode: exit 0, the report names the old and new values, the token_estimate line holds the new value, and every other byte of the file is unchanged.
     - Test that a body line that begins with "token_estimate:" is not touched, and that the frontmatter line is.
     - Test that --check and -c on a stale profile exit 1, name the file, and leave it byte-identical.
     - Test exit 2 with one line naming the file for: a missing path, a file with no frontmatter, a file with no closing delimiter, and a frontmatter with no token_estimate line.
     - Test several paths in one call: a current one, a stale one, and a malformed one give exit 2, the stale one is still rewritten in default mode, and under --check nothing is written and the exit code is still 2.
     - Test that after a rewrite, validate_artifacts reports no profile-token-estimate-mismatch for that profile.
     - Test that no temporary file is left behind.
   - Run the tests and confirm they fail before writing the implementation.

2. Document:
   - Module docstring: the CLI, the three exit codes, and the statement that only the token_estimate frontmatter line is ever changed.

3. GREEN: Write minimal code:
   - Create src/scripts/update_token_estimate.py, standard library only.
   - Split on the frontmatter delimiters and find the token_estimate line by its prefix; no regular-expression parsing and no YAML round trip.
   - Make the validator and this script call one estimate function, and keep every existing validator test passing unchanged.

4. RED: Add integration tests:
   - Create or extend a test that runs main(["--check", ...]) over every profile.md under tests/fixtures/extractions/ and expects exit 0, so a committed good fixture with a stale estimate fails the suite.
   - Test a subprocess run from another working directory.

5. GREEN: Wire the CLI entry point.

6. REFACTOR: One pure function that takes file text and returns the new text and the old and new values, so only one function touches the disk.

7. Update documentation: none beyond the docstring.

8. Verify meaningful coverage of the arithmetic, the frontmatter-only replacement, and all three exit codes, then run `just check`.
```

## Section 5: Research Contract and Agent

Goal R2 and Component G.
The research contract gains the practice lookup.

**Tools:**
- Skills: plugin-dev:agent-development
- MCPs: none
- Linters: python3 tools/prose_scrub.py, python3 tools/sync_skills.py --check

### Step 7: Add the Practice Lookup to the Research Contract and the Agent

**NOTE**: `tests/test_research_contract.py` holds the block between the `research-contract:begin` and `research-contract:end` markers in `metacognition/agents/domain-research.md` equal to `src/references/research-contract.md`. Edit the reference, then copy it into the agent. The domain survey shape must not change.

```text
1. RED: Write contract tests first:
   - Modify tests/test_research_contract.py:
     - Test that the contract names both request shapes, the domain survey and the practice lookup.
     - Test that the practice lookup section states its input (one question about practice and the person's stated lean), its output (at most five bottom lines, each with a source link), and the no relevant results line.
     - Confirm the existing equality test fails once only the reference is edited, which proves the guard covers the new text.

2. Document:
   - In src/references/research-contract.md, add the practice lookup beside the domain survey: when it is used (the interview, on a deferral to outside practice), the input, the output shape with one canonical example in woodworking terms, and the no relevant results line. State that a bottom line never recommends; it reports what sources say.

3. GREEN: Write minimal changes:
   - Copy the reference into the agent's contract block.
   - Update the agent's description and body in metacognition/agents/domain-research.md so it says the interview also dispatches it for practice lookups. Keep the tools read-only and add no model line.
   - Run `just sync` (the design slice ships the contract).

4. RED: Add integration tests:
   - None needed beyond the equality test now passing.

5. GREEN: Nothing further.

6. REFACTOR: None.

7. Update documentation: none.

8. Verify with `just check` and `claude plugin validate ./metacognition`.
```

## Section 6: The Skills

Goals R1 to R8, R10, and R12.
The interview, design, compile, calibrate, and skillify skills take the new rules.

**Tools:**
- Skills: plugin-dev:skill-development, skill-creator:skill-creator
- MCPs: none
- Linters: python3 tools/prose_scrub.py, python3 tools/sync_skills.py --check

### Step 8: Rewrite the Interview Loop and Wire the Interview Slice (task)

**NOTE**: This is the center of the phase. Read the retro's sections on what failed and recommendations 1, 2, 3, 7, and 8 before editing. Keep every existing rule of the skill that this step does not explicitly change: verbatim capture, pushback, ledger callouts, thread following, the 20-question disconfirmation, resume, the closing questions, and the closing self-check. The skill body and its description must stay within the upload limits. The manifest change and the skill text land together or the manifest guard fails.

```text
1. Scope:
   - Artifacts: metacognition/skills/interview/SKILL.md, tools/sync_skills.py (the MANIFEST entry for interview), tests/test_sync_manifest.py (EXPECTED), the synced files under metacognition/skills/interview/.
   - Desired end state: the interview skill states the turn discipline, the live-research protocol with the three-way fallback, picker use and provenance, probe counting, register rules, the capture conventions, exports, and the append script with its by-hand fallback; its slice ships research-contract.md and archive_append.py.

2. Tooling:
   - Skills: plugin-dev:skill-development
   - MCPs: none
   - External: just sync, uv run pytest tests/test_sync_manifest.py tests/test_sync_drift.py, claude plugin validate ./metacognition

3. Do the work:
   - In tools/sync_skills.py, add `research-contract.md` to the interview references and `archive_append.py` to the interview scripts. In tests/test_sync_manifest.py, update EXPECTED to match spec G2's table. Run the manifest tests and see them fail until the skill names both files.
   - In metacognition/skills/interview/SKILL.md:
     - Replace loop rule 1 with the turn discipline (R1): a turn is one open probe or one battery of three to six closed verdict items in one category; never two open probes in a turn; never mixed categories in a battery. Say when each leads, that a surprising battery answer earns an open follow-up, and that a request for more concrete questions is a standing instruction. Include one canonical battery example in woodworking terms.
     - Add the live-research protocol (R2): the trigger (a deferral to outside practice or a request for research), the three-way fallback worded as design's step 2 words it, the presentation of bottom lines with sources, ratification, and logging as an evidence entry. State that a deferral is never banked, and that with no web access the deferral is recorded under Open research as unresolved. Change the "Dispatches" line under Inputs and Outputs to name the research agent for practice lookups.
     - Add picker use and provenance (R3): forced choices, chosen battery items, and ratifications go through the host's choice picker when the surface has one, and are written as a lettered list when it does not; open probes never use it; the A line holds the selected label and the person's own words only.
     - State the counting rule (R4) where the skill describes its tallies and the README cell.
     - Add the register rules (R5): a question with no register-specific content takes the primary register, the first in `registers`; a register that surfaces mid-interview is raised with the person and added on acceptance.
     - Change the 20-question progress note to report category coverage, register coverage, and the running count of research rounds.
     - Add the Exports rule (R6): when the person assigns a topic to another skill, add a line and move on.
     - Add the capture conventions (R8).
     - Replace the per-answer editing instructions with one call to `python3 scripts/archive_append.py`, showing the canonical invocation for an open probe and for a battery, and the by-hand fallback: one edit to archive.md carrying the body and the frontmatter counters together, then one edit to the README cell.
     - Update "Inputs and Outputs" and "Resources" so they name `references/research-contract.md` and `scripts/archive_append.py`, and update the description only if it still says one question at a time.
   - Run `just sync`.

4. Verify:
   - `uv run pytest -q` passes, including both manifest tests; `python3 tools/sync_skills.py --check` exits 0; `claude plugin validate ./metacognition` passes; `just check` exits 0.

5. Document:
   - CLAUDE.md: the interview slice now ships four scripts and five references, and the synced file count; the append script is the interview's write path.
```

### Step 9: Design Checks Artifacts and Plans Register Coverage (task)

**NOTE**: Design's scope Q&A stays one question at a time; do not touch that section. Read retro recommendations 4 and 5.

```text
1. Scope:
   - Artifacts: metacognition/skills/design/SKILL.md.
   - Desired end state: design verifies artifact paths, writes a Registers column, refuses to finish with an untargeted register, states that floors count probes, and writes concrete seeds.

2. Tooling:
   - Skills: plugin-dev:skill-development
   - MCPs: none
   - External: python3 tools/prose_scrub.py, claude plugin validate ./metacognition

3. Do the work:
   - In step 4 (Category Map): add the Registers column and the rule that every register must be targeted by at least one category; when one is not, design raises it with the person and either adds questions or drops the register before writing. State that floors count probes and that a battery counts its items.
   - In step 5 (Question Seeds) and step 7 (Forced-Choice Bank): seeds and bank entries are concrete scenarios, not abstract framings, with one bad and one good example in woodworking terms. Note which seeds suit a battery.
   - In step 6 (Artifact Plan): before writing the plan, check each local path exists and holds real content; record a missing path or an empty skeleton as unavailable with the reason and tell the person now; where the surface has no file access, say the paths could not be checked.
   - In step 8 (Closure Pass): add the register coverage check and the artifact availability check to what the pass confirms.
   - Keep the template the skill writes in step with src/references/interview-spec-format.md from Step 2.

4. Verify:
   - `just check` exits 0 and `claude plugin validate ./metacognition` passes.

5. Document:
   - none
```

### Step 10: Compile and Calibrate Read the New Archive and Use the Estimate Script (task)

**NOTE**: Goals R2, R3, R6, R8, and R10. Compile's keep/cut test, its log of every cut, and its rule of never resolving a tension do not change. The profile format's seventeen sections do not change. Check `src/references/profile-format.md` and the compile skill for where `compile-log.md` is described, and put the exports list there. The manifest change and the skill text land together or the manifest guard fails.

```text
1. Scope:
   - Artifacts: metacognition/skills/compile/SKILL.md, metacognition/skills/calibrate/SKILL.md, tools/sync_skills.py (the MANIFEST entries for compile and calibrate), tests/test_sync_manifest.py (EXPECTED), the synced files, and src/references/profile-format.md only if it defines the compile log's contents or names the one-liner.
   - Desired end state: compile handles batteries, evidence entries, open research, exports, and meta-rules; compile and calibrate keep the token estimate current with the script; both slices ship it.

2. Tooling:
   - Skills: plugin-dev:skill-development
   - MCPs: none
   - External: just sync, python3 tools/prose_scrub.py, claude plugin validate ./metacognition

3. Do the work:
   - In tools/sync_skills.py add `update_token_estimate.py` to the compile and calibrate scripts, and update EXPECTED in tests/test_sync_manifest.py to match spec G2's table.
   - In metacognition/skills/compile/SKILL.md:
     - State that a battery entry holds several verdicts, each a candidate rule traced to its Qnn and item number.
     - State the evidence rule: a ratified practice compiles to the written practice with its citation; compile never writes a bare instruction to follow community practice; an unresolved Open research line is listed in the do_not_infer section as not yet settled.
     - State the exports rule: export content stays out of the profile body, and the list is copied into compile-log.md under its own heading.
     - State the meta-rule routing: rules about how the person wants judgment exercised are profile content, and name which existing sections take them.
     - State the picker reading rule: an answer that is only a selected label is the person's choice, and the option text in the Q line is the interviewer's wording, not a quote.
     - In the token-estimate step, replace the one-liner as the primary instruction with `python3 scripts/update_token_estimate.py <extractions-root>/<slug>/profile.md`, report the value it prints, and keep the one-liner as the stated by-hand fallback for when the script cannot run.
     - Name the script under Inputs and Outputs and Resources.
   - In metacognition/skills/calibrate/SKILL.md:
     - In the fold-back step, after profile.md is edited, run `python3 scripts/update_token_estimate.py` on it, and keep a by-hand fallback sentence that matches compile's.
     - Name the script under Inputs and Outputs and Resources.
   - Run `just sync`. If src/references/profile-format.md changed, update docs/formats/profile.md in the same step.

4. Verify:
   - `uv run pytest -q` passes, including both manifest tests; `just check` exits 0; `claude plugin validate ./metacognition` passes.

5. Document:
   - CLAUDE.md: the compile and calibrate slices ship the estimate script, and the synced file count.
```

### Step 11: Ground Skillify in the Provider Baseline (task)

**NOTE**: Goals R6 and R12, issue 10. `plugin-dev` is a public plugin and is recommended, never required: every sentence that uses it carries the fallback. On claude.ai chat another plugin's skill cannot be loaded, so the fallback is the normal path there. The `exemplar` setting and `resolve_config.py` do not change; only what skillify does with a missing exemplar changes. `src/references/settings.md` must stay in step with `resolve_config.py`. An augment never changes a SKILL.md without a diff the person has reviewed; that invariant stands, and this step adds a decision before the diff, not a way around it.

```text
1. Scope:
   - Artifacts: metacognition/skills/skillify/SKILL.md, src/references/settings.md, src/references/skill-scaffold.md if it describes the exemplar, the synced copies.
   - Desired end state: skillify loads the provider baseline with a stated fallback, treats the exemplar as an advanced option and skips a missing one silently, states the precedence order, assesses structure before an augment diff, and reports exports.

2. Tooling:
   - Skills: plugin-dev:skill-development
   - MCPs: none
   - External: just sync, python3 tools/prose_scrub.py, claude plugin validate ./metacognition

3. Do the work:
   - In metacognition/skills/skillify/SKILL.md:
     - In Read First, add the baseline load: before writing a scaffold or proposing a structure, load `plugin-dev:skill-development` through the Skill tool. When it is not installed, or the surface cannot load another plugin's skill, say so in one line, continue on `references/skill-scaffold.md`, and recommend the install in the finish message.
     - Rewrite the exemplar paragraph: the exemplar is an advanced option; with no setting, or a setting whose path does not exist, skip the read with no message; when one exists it may shape the output, and the baseline review still runs and its findings are answered, not skipped.
     - State the precedence order in one place: the person's decision, then the provider baseline review, then the exemplar, then the bundled templates.
     - In the augment path, before the content diff is drafted, add the structural assessment: description triggering, progressive disclosure, size, and reference layout, using the `plugin-dev:skill-reviewer` agent where it can be dispatched and the loaded baseline otherwise. When the structure holds, say so in one line and continue. When it does not, present the best alternative layout beside keep-as-is with the findings as the reasoning, and wait for the person's choice. State that a restructure is applied only on that explicit choice and still goes through a reviewed diff.
     - State that --dry-run shows the assessment and the options and applies nothing.
     - In the finish message, list the archive's exports as follow-up work for other skills, and state that exports are never written into the produced skill.
     - Confirm in the text that the section map reads `### Qnn [<category>]` and ignores the tags after the category.
     - Update Inputs and Outputs: the baseline skill and the reviewer agent are optional and external, never files in this skill's slice.
   - In src/references/settings.md: describe `exemplar` as an advanced option most people will not set, and say a path that does not exist is skipped silently. Change nothing about the tiers, the keys, or the `exists` field.
   - Run `just sync`.

4. Verify:
   - `just check` exits 0; `claude plugin validate ./metacognition` passes; `grep -n "not found" metacognition/skills/skillify/SKILL.md` shows no instruction to tell the person about a missing exemplar.

5. Document:
   - CLAUDE.md: skillify uses plugin-dev when present, and the exemplar is an advanced option.
```

## Section 7: Evals and Docs

Goals R9 and R12.
The evals follow the skill text, and the reader-facing pages say what the skills now do.

**Tools:**
- Skills: plugin-dev:skill-development
- MCPs: none
- Linters: python3 tools/prose_scrub.py

### Step 12: Update the Evals (task)

**NOTE**: An eval expectation must be something the skill text states; check each one against the exact wording of the skill it tests. `tests/test_evals.py` requires every fixture path an eval names to exist. Evals are not a gate and are not run in this step.

```text
1. Scope:
   - Artifacts: evals/interview/evals.json, evals/design/evals.json, evals/compile/evals.json, evals/skillify/evals.json, evals/README.md, and a new fixture plugin under tests/fixtures/plugins/.
   - Desired end state: the evals describe the behavior of Steps 8 to 11.

2. Tooling:
   - Skills: none
   - MCPs: none
   - External: uv run pytest tests/test_evals.py

3. Do the work:
   - In evals/interview/evals.json: revise any expectation that says one question per turn; add one eval that runs against a scratch copy of tests/fixtures/extractions/woodworking-battery and expects a battery once the category's shape is known, logged with the items tag and counted as probes; add one eval where the person defers to standard practice and the expected output is same-turn research, ratification, and an evidence entry, or an Open research line marked unresolved when the session has no web access.
   - In evals/design/evals.json: add expectations that an artifact path with no content is reported as unavailable at design time and that every register is targeted in the category map.
   - In evals/compile/evals.json: add an eval on the woodworking-battery fixture expecting exports in compile-log.md and absent from the profile body.
   - Create tests/fixtures/plugins/woodshop-sprawl/, a synthetic fixture plugin with one skill whose structure is deliberately poor: a vague description with no trigger phrases, one oversized SKILL.md, and no references. Do not edit the existing woodshop fixture.
   - In evals/skillify/evals.json: add two augment evals. One targets the existing woodshop fixture skill and expects the one-line verdict that the structure holds, followed by the diff path. The other targets woodshop-sprawl and expects the findings, the alternative layout beside keep-as-is, and no diff drafted before the person chooses. Add expectations that a missing exemplar produces no message and that the finish message recommends the companion install when the baseline could not be loaded.
   - In evals/compile/evals.json and evals/calibrate/evals.json: where an expectation describes the token estimate step, say it is produced by the script or by the stated fallback.
   - In evals/README.md: describe the new evals and the new fixture in the style of the existing entries.

4. Verify:
   - `uv run pytest tests/test_evals.py -q` passes and `just check` exits 0.

5. Document:
   - none
```

### Step 13: Update the Stage Pages and the Front Door (task)

**NOTE**: The format pages and the Method page changed in Step 2. This step covers the pages that describe what the stages do. The doctrine guard scans `docs/`, so the repo slug and the credit line stay in the README's marked sections.

```text
1. Scope:
   - Artifacts: docs/stages/interview.md, docs/stages/design.md, docs/stages/compile.md, docs/stages/calibrate.md, docs/stages/skillify.md, docs/stages/index.md, docs/index.md, docs/configuration.md, docs/getting-started.md, README.md.
   - Desired end state: no page says the interview asks one question at a time; each stage page describes the new behavior in the page's existing voice.

2. Tooling:
   - Skills: none
   - MCPs: none
   - External: just docs-build, python3 tools/prose_scrub.py

3. Do the work:
   - docs/stages/interview.md: describe turns (an open question, or a short battery of three to six verdict items), same-turn research with ratification and what happens with no web access, the picker and its fallback, the progress note's contents, exports, and that each entry is saved as it is answered.
   - docs/stages/design.md: the artifact check and the register coverage rule. Leave "one scoping question at a time" as it is; that is still true.
   - docs/stages/compile.md: evidence compiles to the written practice with its citation, exports go to the compile log, and the token estimate is kept current by a script.
   - docs/stages/calibrate.md: the token estimate is refreshed by the same script after a fold-back.
   - docs/stages/skillify.md: exports are reported as follow-up work; skillify consults the provider's skill-craft guidance when the companion plugin is installed and says so when it is not; augment assesses the existing skill's structure first and never restructures without the person's choice.
   - docs/configuration.md: present `exemplar` as an advanced option most people will not set, and say a missing exemplar is skipped silently. Keep the page in step with src/references/settings.md from Step 11.
   - README.md: add the plugin-dev plugin as a highly recommended companion install, with the stage that uses it (skillify) and the statement that nothing requires it. Put the sentence where the docs can show it too: inside the install snippet section if it reads well on Getting Started, otherwise in its own short section.
   - docs/index.md, docs/stages/index.md, and README.md: change the lines that say the interview asks or you answer "one question at a time" to wording that is true for batteries, keeping each sentence short. Keep the README's three snippet marker pairs intact.

4. Verify:
   - `grep -rn "one question at a time" README.md docs` returns only lines about design's scoping questions or skillify's role questions; `just check` exits 0.

5. Document:
   - none
```

## Section 8: Version and Release Readiness

Goal R9.
The version moves once, everywhere.

**Tools:** none

### Step 14: Set Version 0.2.0 and Refresh the Release Record (task)

**NOTE**: The maintainer ruled `0.2.0` for this phase. Merging a manifest version with no tag publishes a release, so this step makes the pull request a release. `tests/test_skill_versions.py` fails until every source agrees, including `pyproject.toml` and the README's beta notice.

```text
1. Scope:
   - Artifacts: the five metacognition/skills/*/SKILL.md files, metacognition/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, pyproject.toml, uv.lock, README.md (the beta section), docs/surface-check.md, CLAUDE.md.
   - Desired end state: every version source reads 0.2.0 and the release zip builds.

2. Tooling:
   - Skills: none
   - MCPs: none
   - External: uv lock, just check, just release-dry, claude plugin validate ./metacognition

3. Do the work:
   - Change 0.1.1 to 0.2.0 in each version source listed above.
   - Run `uv lock` so the lockfile carries the new project version.
   - In docs/surface-check.md, update the version in the build instructions and the upload steps, re-run the four automated checks listed at the bottom, and record their real output and today's date. Leave every surface result slot reading "Not yet run".

4. Verify:
   - `just check` exits 0; `just release-dry` writes dist/metacognition-0.2.0.zip; `claude plugin validate ./metacognition` passes; `python3 tools/sync_skills.py --check` exits 0.

5. Document:
   - CLAUDE.md: the phase is built, the version is 0.2.0, the five shipped scripts, the new fixtures, and that the plan is ready to archive after the merge.
```

## Implementation Guidelines

- Work on the `interview-retro` branch through a pull request; only the maintainer merges to main.
- `src/` is the single source of truth. Change `src/` and run `just sync`; never hand-edit a synced copy.
- Test-first for `src/scripts/`: write the tests, run them, and see them fail for the expected reason before writing the implementation. Log any deviation to `.ai-sessions/implementation-notes.md` when it happens.
- Never edit an existing fixture to make a test pass. A new behavior gets a new fixture or a tmp_path case.
- Every example in a skill or reference is canonical and in woodworking terms, matching the existing fixtures' persona.
- An eval expectation and a docs sentence must each trace to text in the skill or reference they describe.
- Keep prose to the vendored writing rules: no em-dash or en-dash, straight quotes, Title Case headings, one sentence per line in committed Markdown. Run `python3 tools/prose_scrub.py` before finishing a step.
- Run `just fmt` before `just check` whenever a Python file changed.
- When a decision is unresolved, list it under "Open questions" at the end of the step and do not guess.

## Success Metrics

- `just check` exits 0 locally and CI is green on the pull request that lands the phase.
- `claude plugin validate ./metacognition` passes with no errors.
- `archive_append.py` followed by `validate_artifacts.py` exits 0 for an open probe, a battery, an evidence entry, a closing question, and each section line; each documented error exits 2 and leaves both files byte-identical.
- `validate_artifacts.py` exits 0 on `woodworking-battery`, exits non-zero with `archive-battery-items` only on `battery-item-mismatch`, and gives the same result as before on every earlier fixture.
- The agent's contract block equals `src/references/research-contract.md`, both request shapes included.
- `sync_skills.py --check` is clean with the interview slice holding `research-contract.md` and `archive_append.py`, and the compile and calibrate slices holding `update_token_estimate.py`.
- The interview skill states the turn discipline, the three-way research fallback, the picker provenance rule, the probe-counting rule, and the capture conventions; the design skill states the artifact check and the register column.
- The docs pages say what their sources say, and the Method page still counts sixteen rules.
- `update_token_estimate.py` exits 0, 1, and 2 as Component L states, rewrites only the `token_estimate` line, and a `--check` run over the good fixtures is part of the test suite.
- The floor is Python 3.12 everywhere it is stated, and CI runs 3.12 and 3.13.
- Skillify loads the provider baseline with its fallback, skips a missing exemplar silently, and presents keep-or-restructure before an augment diff when the structure is challenged; the skillify eval covers both verdict paths.
- Every version source reads `0.2.0`.
