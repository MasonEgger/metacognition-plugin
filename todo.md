# Metacognition Plugin: Todo

Mirrors plan.md.
Check a step only when every sub-step under it is done.

## Section 1: Toolchain Floor

- [x] Step 1: Raise the Python Floor to 3.12 (task)
  - [x] pyproject.toml: requires-python, ruff target, mypy version
  - [x] uv lock
  - [x] ci.yml matrix 3.12 and 3.13
  - [x] Every remaining statement of the 3.11 floor in scripts, references, skills, docs
  - [x] just fmt, just sync
  - [x] docs/surface-check.md asks for the sandbox Python version
  - [x] Verify: grep shows history lines only, just check, sync check
  - [x] Document: CLAUDE.md note

## Section 2: Formats and References

- [x] Step 2: Extend the Archive, Interview Spec, and Technique References (task)
  - [x] archive-format.md: optional Open research and Exports sections, battery and evidence entries in the template
  - [x] archive-format.md: probe types, items tag, battery body shape, counting rule
  - [x] archive-format.md: picker provenance, capture conventions, registers may grow
  - [x] interview-spec-format.md: Registers column, floors count probes, artifact availability, README cell rule
  - [x] extraction-theory.md: battery and evidence rows in rule 16's table, still sixteen rules
  - [x] just sync
  - [x] docs/formats/archive.md, docs/formats/interview-spec.md, docs/method.md restate the changes
  - [x] Verify: sync check, prose gate, just check
  - [x] Document: CLAUDE.md note

## Section 3: Validator

- [x] Step 3: Probe Counts, the Battery Check, and Optional Sections in validate_artifacts.py
  - [x] RED: probe count, battery failures, items tag misuse, evidence count, section IDs, closing battery, two new fixtures
  - [x] Document: module docstring check list
  - [x] GREEN: heading parsing, probe counting, archive-battery-items, section ID check
  - [x] Create tests/fixtures/extractions/woodworking-battery
  - [x] Create tests/fixtures/extractions-bad/battery-item-mismatch
  - [x] Add both to the fixture READMEs
  - [x] RED: earlier fixtures unchanged, yaml parity covers the new ones
  - [x] GREEN: fix in the validator only
  - [x] REFACTOR: one heading parser
  - [x] just sync
  - [x] Verify coverage and just check

## Section 4: The Scripts

- [x] Step 4: archive_append.py for a Single Entry
  - [x] RED: Qnn output, entry placement, counters, README cell, validator round trip, file flags, normalization, errors write nothing, no temp files left
  - [x] Document: module docstring
  - [x] GREEN: archive_append.py, validate then write by rename
  - [x] RED: three appends in a row, subprocess from another directory
  - [x] GREEN: CLI entry point
  - [x] REFACTOR: request parsing, archive text, README text as pure functions
  - [x] Verify coverage and just check
- [x] Step 5: Batteries, Closing Questions, and Section Lines in archive_append.py
  - [x] RED: battery write and counts, items refusals, closing, saturated, ledger, export, research lines, evidence, combined run
  - [x] Document: docstring flags
  - [x] GREEN: extend the script
  - [x] RED: scripted short interview round trip
  - [x] GREEN: fix what the run exposes
  - [x] REFACTOR: one table for section flags
  - [x] Verify coverage and just check
- [x] Step 6: update_token_estimate.py
  - [x] RED: arithmetic, current profile untouched, stale rewrite, body line untouched, check mode, three exit-2 cases, several paths, validator agrees, no temp files
  - [x] Document: module docstring
  - [x] GREEN: the script, one estimate function shared with the validator
  - [x] RED: --check over every good-fixture profile, subprocess from another directory
  - [x] GREEN: CLI entry point
  - [x] REFACTOR: one pure text-in, text-out function
  - [x] Verify coverage and just check

## Section 5: Research Contract and Agent

- [x] Step 7: Add the Practice Lookup to the Research Contract and the Agent
  - [x] RED: both request shapes named, practice lookup input, output, and no-results line
  - [x] Document: research-contract.md practice lookup with one canonical example
  - [x] GREEN: copy into the agent block, update the agent description and body
  - [x] just sync
  - [x] Verify: just check, claude plugin validate

## Section 6: The Skills

- [x] Step 8: Rewrite the Interview Loop and Wire the Interview Slice (task)
  - [x] MANIFEST and EXPECTED: interview gains research-contract.md and archive_append.py
  - [x] Turn discipline with one canonical battery example
  - [x] Live-research protocol with the three-way fallback and the Dispatches line
  - [x] Picker use and provenance
  - [x] Counting rule, register rules, progress note contents
  - [x] Exports rule and capture conventions
  - [x] Append script invocation and by-hand fallback
  - [x] Inputs and Outputs, Resources, description
  - [x] just sync
  - [x] Verify: pytest, sync check, claude plugin validate, just check
  - [x] Document: CLAUDE.md note
- [x] Step 9: Design Checks Artifacts and Plans Register Coverage (task)
  - [x] Category map: Registers column, untargeted register rule, floors count probes
  - [x] Seeds and forced-choice bank: concrete scenarios, battery-suited seeds
  - [x] Artifact plan: availability check
  - [x] Closure pass: register and artifact checks
  - [x] Verify: just check, claude plugin validate
- [x] Step 10: Compile and Calibrate Read the New Archive and Use the Estimate Script (task)
  - [x] MANIFEST and EXPECTED: compile and calibrate gain update_token_estimate.py
  - [x] Compile: battery verdicts, evidence rule, exports rule, meta-rule routing, picker reading rule
  - [x] Compile: token-estimate step runs the script, one-liner kept as fallback
  - [x] Calibrate: fold-back runs the script, fallback sentence
  - [x] Inputs and Outputs and Resources name the script in both skills
  - [x] just sync, and docs/formats/profile.md if profile-format.md changed
  - [x] Verify: pytest, just check, claude plugin validate
  - [x] Document: CLAUDE.md note
- [x] Step 11: Ground Skillify in the Provider Baseline (task)
  - [x] Read First: load the baseline skill, with the stated fallback
  - [x] Exemplar as an advanced option, missing one skipped silently
  - [x] Precedence order stated once
  - [x] Augment: structural assessment, keep-or-restructure, explicit choice only
  - [x] Dry run shows the assessment and applies nothing
  - [x] Finish message: exports as follow-up, install recommendation when the baseline was absent
  - [x] settings.md: exemplar as an advanced option
  - [x] just sync
  - [x] Verify: just check, claude plugin validate, grep
  - [x] Document: CLAUDE.md note

## Section 7: Evals and Docs

- [x] Step 12: Update the Evals (task)
  - [x] Interview evals: battery eval, deferral eval, revised turn expectations
  - [x] Design evals: unavailable artifact, register coverage
  - [x] Compile eval: exports in the compile log
  - [x] New fixture plugin tests/fixtures/plugins/woodshop-sprawl
  - [x] Skillify evals: structure holds, structure challenged, silent exemplar skip, install recommendation
  - [x] Compile and calibrate evals: token estimate by script or fallback
  - [x] evals/README.md
  - [x] Verify: test_evals, just check
- [ ] Step 13: Update the Stage Pages and the Front Door (task)
  - [ ] docs/stages/interview.md
  - [ ] docs/stages/design.md, compile.md, calibrate.md, skillify.md
  - [ ] docs/configuration.md: exemplar as an advanced option
  - [ ] docs/index.md, docs/stages/index.md, README.md wording
  - [ ] README.md: plugin-dev as a recommended companion install
  - [ ] docs/privacy.md: research findings and exports travel with the archive
  - [ ] Closing sweep: every docs page checked against the changed skills, references, and scripts
  - [ ] Verify: grep for the old wording, docs build, just check

## Section 8: Version and Release Readiness

- [ ] Step 14: Set Version 0.2.0 and Refresh the Release Record (task)
  - [ ] 0.2.0 in five SKILL.md files, both manifests, pyproject.toml, README beta section
  - [ ] uv lock
  - [ ] docs/surface-check.md version and automated-checks record
  - [ ] Verify: just check, release-dry, claude plugin validate, sync check
  - [ ] Document: CLAUDE.md note
