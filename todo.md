# Metacognition Plugin: Todo

Mirrors plan.md.
Check a step only when every sub-step under it is done.

## Section 1: Repo Scaffold and Toolchain

- [x] Step 1: Python Toolchain and Justfile (task)
  - [x] Scope: pyproject.toml and justfile
  - [x] Write pyproject.toml (requires-python >=3.11, dev group, ruff, mypy, pytest config)
  - [x] Write justfile (check, fmt, test, sync, docs-build, docs-serve, release-dry)
  - [x] Verify: uv sync exits 0
- [x] Step 2: Manifests, Directory Skeleton, and Minimal Docs (task)
  - [x] marketplace.json (version 0.1.0)
  - [x] plugin.json (version 0.1.0)
  - [x] Directory skeleton plus src/scripts/__init__.py
  - [x] .gitignore additions
  - [x] Minimal mkdocs.yml and docs/index.md
  - [x] Verify: just docs-build and claude plugin validate pass

## Section 2: Fixtures and Bad-Extraction Cases

- [x] Step 3: Port the Good Fixtures (task)
  - [x] woodworking, woodworking-augment, woodworking-truncated
  - [x] woodshop plugin fixture
  - [x] extractions README (port rules applied)
  - [x] Verify: every listed fixture file exists
- [x] Step 4: Port the Bad-Extraction Cases (task)
  - [x] bad-yaml, missing-section, noncontiguous-rounds, numbering-gap, oversize-profile
  - [x] Verify: all five case directories complete

## Section 3: YAML Subset Parser

- [x] Step 5: Implement yaml_subset.py
  - [x] RED: parser unit tests (inline strings)
  - [x] Document: module docstring construct list
  - [x] GREEN: parse() and CLI, stdlib only
  - [x] RED: edge-case tests
  - [x] GREEN: extend parser
  - [x] REFACTOR: tokenizer and coercion helpers
  - [x] Update docstring
  - [x] Verify coverage and just check
- [x] Step 6: YAML Parity Test Over Fixtures
  - [x] RED: parity test vs pyyaml over all fixture frontmatter
  - [x] GREEN: grow parser if a construct is uncovered, update docstring
  - [x] REFACTOR: frontmatter locator helper
  - [x] Verify parity passes and just check

## Section 4: Config and Artifact Validation Scripts

- [x] Step 7: Implement resolve_config.py
  - [x] RED: resolver tests (all tiers, merge, loud errors, defaults, exists, stderr echo)
  - [x] Document: agreement with settings.md noted
  - [x] GREEN: resolver with five tiers, JSON stdout, "Loaded config from" on stderr
  - [x] RED: integration tests
  - [x] GREEN: wire tiers
  - [x] REFACTOR: tier structure
  - [x] Verify coverage and just check
- [x] Step 8: Port validate_artifacts.py
  - [x] RED: ported suite (woodworking pass, five bad cases, remaining checks)
  - [x] Document: 5,000 ceiling and prose-elsewhere note
  - [x] GREEN: port onto yaml_subset, preserve checks and exit codes
  - [x] RED: multi-finding ordering test if applicable
  - [x] GREEN: minimal
  - [x] REFACTOR: named check functions
  - [x] Verify woodworking pass and each finding, just check

## Section 5: Source References

- [x] Step 9: Port and Author the References (task)
  - [x] Port six references (extraction-theory, interview-spec-format, archive-format, profile-format, calibration-protocol, skill-scaffold)
  - [x] profile-format: 5,000 ceiling and fixed priority text
  - [x] Write settings.md (matches resolve_config, documents the "Loaded config from" line)
  - [x] Write research-contract.md (four-block shape plus no-results line)
  - [x] Verify: no private tokens, no ../

## Section 6: The Five Skills

- [x] Step 10: Port design and interview (task)
  - [x] design/SKILL.md ported (four-field frontmatter at 0.1.0, settings-first, research dispatch, ends and stops)
  - [x] interview/SKILL.md ported (one question per turn, verbatim, generic dictation note)
  - [x] Verify: grep checks pass, inputs and outputs by path
- [x] Step 11: Port compile and calibrate (task)
  - [x] compile/SKILL.md ported (never resolves a tension, logs every cut)
  - [x] calibrate/SKILL.md ported (reads profile not archive, probes never ship)
  - [x] Verify: grep checks pass
- [x] Step 12: Port skillify (task)
  - [x] skillify/SKILL.md ported (exemplar, --into and default package, verbatim-archive warning, target_skill, augment, version stamping, loader)
  - [x] Verify: grep checks pass, warning text present

## Section 7: The Research Agent

- [x] Step 13: Port the Agent and Bind Its Contract
  - [x] RED: contract-parity test (agent block equals research-contract.md, no model lines)
  - [x] Document: stable contract-block markers
  - [x] GREEN: port agent, make block byte-equal
  - [x] RED: four-block shape and no-results line present
  - [x] GREEN: align both
  - [x] REFACTOR: single marker pair
  - [x] Verify parity and just check

## Section 8: Sync Tool and Drift Guards

- [x] Step 14: Implement sync_skills.py and Populate the Skills
  - [x] RED: test_sync_drift and test_sync_manifest (G2 table)
  - [x] Document: manifest-source comment
  - [x] GREEN: sync_skills.py with manifest, copy, remove, --check
  - [x] Run sync and commit populated skill dirs
  - [x] RED: extra-file detection test
  - [x] GREEN: minimal
  - [x] REFACTOR: typed copy and diff helpers
  - [x] Verify: --check clean, drift test fails on a byte edit, plugin validate passes, just check

## Section 9: Evals

- [x] Step 15: Port Evals and Add the Parse-and-Path Test
  - [x] RED: test_evals (JSON parses, fixture paths exist, README present)
  - [x] Document: evals/README.md scratch-copy procedure
  - [x] GREEN: port five stage evals.json, drop sync, repoint fixtures
  - [x] RED: no evals path inside metacognition/
  - [x] GREEN: keep evals top-level
  - [x] Verify parse and paths, just check

## Section 10: Doctrine and Version Guards

- [x] Step 16: Doctrine Invariants and Skill-Version Tests
  - [x] RED: test_doctrine_invariants (tokens, model lines, ../, self-check)
  - [x] RED: test_skill_versions (presence, SemVer 0.x shape during beta, uniformity)
  - [x] GREEN: scoped walker and version reader; fix any violation at source
  - [x] RED: planted-token detection test
  - [x] GREEN: matcher catches it
  - [x] REFACTOR: shared walker
  - [x] Verify both guards and just check

## Section 11: Packaging, Prose Gate, and Release

- [ ] Step 17: Implement build_zips.py and Its Refusals
  - [ ] RED: test_build_zips (happy path plus every refusal, exclusions)
  - [ ] Document: refusal-list docstring
  - [ ] GREEN: build_zips.py (version read, refusals, zip from metacognition/ only)
  - [ ] RED: clean-tree archive opens with sole root
  - [ ] GREEN: minimal
  - [ ] REFACTOR: named refusal predicates
  - [ ] Verify happy path and refusals, just check
- [ ] Step 18: Port prose_scrub.py and Run It Over the Repo
  - [ ] RED: test_prose_scrub (clean passes, dirty fails, allowlist, reporting)
  - [ ] Document: allowlist docstring
  - [ ] GREEN: port prose_scrub with cut-down allowlist
  - [ ] RED: test_repo_prose over own prose
  - [ ] GREEN: fix any real violation
  - [ ] REFACTOR: share file walker
  - [ ] Verify fixtures, allowlist, clean repo prose, just check
- [ ] Step 19: CI and Release Workflows (task)
  - [ ] ci.yml (matrix 3.11 and 3.13, just check, docs deploy on main, SHA-pinned)
  - [ ] release.yml (version read, tag guard, gate, zip, tag, pre-release during 0.x, SHA-pinned)
  - [ ] Verify: every uses: pinned to a 40-char SHA, valid YAML

## Section 12: Docs Site and README

- [ ] Step 20: Build the Docs Site (task)
  - [ ] Home, Getting Started, The Five Stages
  - [ ] Configuration (from settings.md), The Method (from extraction-theory.md)
  - [ ] Privacy, File Formats
  - [ ] Update mkdocs.yml nav
  - [ ] Verify: just docs-build clean
- [ ] Step 21: Write the README (task)
  - [ ] Port from private README, strip private tokens
  - [ ] What it is, install (marketplace first, zip alternate), docs link, beta note, model recommendation, single credit line
  - [ ] Verify: exactly one credit line, docs link resolves

## Section 13: Live Surface Check

- [ ] Step 22: Prepare and Record the Surface Check (task)
  - [ ] Build the upload zip (just release-dry)
  - [ ] Write the three-surface checklist with result slots
  - [ ] Verify: zip exists, checklist lists all three surfaces
