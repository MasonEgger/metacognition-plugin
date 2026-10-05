# Metacognition Plugin: Todo

Mirrors plan.md.
Check a step only when every sub-step under it is done.

## Section 1: Formats and References

- [ ] Step 1: Extend the Archive, Interview Spec, and Technique References (task)
  - [ ] archive-format.md: optional Open research and Exports sections, battery and evidence entries in the template
  - [ ] archive-format.md: probe types, items tag, battery body shape, counting rule
  - [ ] archive-format.md: picker provenance, capture conventions, registers may grow
  - [ ] interview-spec-format.md: Registers column, floors count probes, artifact availability, README cell rule
  - [ ] extraction-theory.md: battery and evidence rows in rule 16's table, still sixteen rules
  - [ ] just sync
  - [ ] docs/formats/archive.md, docs/formats/interview-spec.md, docs/method.md restate the changes
  - [ ] Verify: sync check, prose gate, just check
  - [ ] Document: CLAUDE.md note

## Section 2: Validator

- [ ] Step 2: Probe Counts, the Battery Check, and Optional Sections in validate_artifacts.py
  - [ ] RED: probe count, battery failures, items tag misuse, evidence count, section IDs, closing battery, two new fixtures
  - [ ] Document: module docstring check list
  - [ ] GREEN: heading parsing, probe counting, archive-battery-items, section ID check
  - [ ] Create tests/fixtures/extractions/woodworking-battery
  - [ ] Create tests/fixtures/extractions-bad/battery-item-mismatch
  - [ ] Add both to the fixture READMEs
  - [ ] RED: earlier fixtures unchanged, yaml parity covers the new ones
  - [ ] GREEN: fix in the validator only
  - [ ] REFACTOR: one heading parser
  - [ ] just sync
  - [ ] Verify coverage and just check

## Section 3: The Append Script

- [ ] Step 3: archive_append.py for a Single Entry
  - [ ] RED: Qnn output, entry placement, counters, README cell, validator round trip, file flags, normalization, errors write nothing, no temp files left
  - [ ] Document: module docstring
  - [ ] GREEN: archive_append.py, validate then write by rename
  - [ ] RED: three appends in a row, subprocess from another directory
  - [ ] GREEN: CLI entry point
  - [ ] REFACTOR: request parsing, archive text, README text as pure functions
  - [ ] Verify coverage and just check
- [ ] Step 4: Batteries, Closing Questions, and Section Lines in archive_append.py
  - [ ] RED: battery write and counts, items refusals, closing, saturated, ledger, export, research lines, evidence, combined run
  - [ ] Document: docstring flags
  - [ ] GREEN: extend the script
  - [ ] RED: scripted short interview round trip
  - [ ] GREEN: fix what the run exposes
  - [ ] REFACTOR: one table for section flags
  - [ ] Verify coverage and just check

## Section 4: Research Contract and Agent

- [ ] Step 5: Add the Practice Lookup to the Research Contract and the Agent
  - [ ] RED: both request shapes named, practice lookup input, output, and no-results line
  - [ ] Document: research-contract.md practice lookup with one canonical example
  - [ ] GREEN: copy into the agent block, update the agent description and body
  - [ ] just sync
  - [ ] Verify: just check, claude plugin validate

## Section 5: The Skills

- [ ] Step 6: Rewrite the Interview Loop and Wire the Interview Slice (task)
  - [ ] MANIFEST and EXPECTED: interview gains research-contract.md and archive_append.py
  - [ ] Turn discipline with one canonical battery example
  - [ ] Live-research protocol with the three-way fallback and the Dispatches line
  - [ ] Picker use and provenance
  - [ ] Counting rule, register rules, progress note contents
  - [ ] Exports rule and capture conventions
  - [ ] Append script invocation and by-hand fallback
  - [ ] Inputs and Outputs, Resources, description
  - [ ] just sync
  - [ ] Verify: pytest, sync check, claude plugin validate, just check
  - [ ] Document: CLAUDE.md note
- [ ] Step 7: Design Checks Artifacts and Plans Register Coverage (task)
  - [ ] Category map: Registers column, untargeted register rule, floors count probes
  - [ ] Seeds and forced-choice bank: concrete scenarios, battery-suited seeds
  - [ ] Artifact plan: availability check
  - [ ] Closure pass: register and artifact checks
  - [ ] Verify: just check, claude plugin validate
- [ ] Step 8: Compile and Skillify Read the New Archive (task)
  - [ ] Compile: battery verdicts, evidence rule, exports rule, meta-rule routing, picker reading rule
  - [ ] Skillify: exports in the finish message, section map ignores later tags
  - [ ] Sync and docs/formats/profile.md if profile-format.md changed
  - [ ] Verify: just check, claude plugin validate

## Section 6: Evals and Docs

- [ ] Step 9: Update the Design and Interview Evals (task)
  - [ ] Interview evals: battery eval, deferral eval, revised turn expectations
  - [ ] Design evals: unavailable artifact, register coverage
  - [ ] Compile eval: exports in the compile log
  - [ ] evals/README.md
  - [ ] Verify: test_evals, just check
- [ ] Step 10: Update the Stage Pages and the Front Door (task)
  - [ ] docs/stages/interview.md
  - [ ] docs/stages/design.md, compile.md, skillify.md
  - [ ] docs/index.md, docs/stages/index.md, README.md wording
  - [ ] Verify: grep for the old wording, just check

## Section 7: Version and Release Readiness

- [ ] Step 11: Set Version 0.2.0 and Refresh the Release Record (task)
  - [ ] 0.2.0 in five SKILL.md files, both manifests, pyproject.toml, README beta section
  - [ ] uv lock
  - [ ] docs/surface-check.md version and automated-checks record
  - [ ] Verify: just check, release-dry, claude plugin validate, sync check
  - [ ] Document: CLAUDE.md note
