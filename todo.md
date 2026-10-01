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
- [ ] Step 6: YAML Parity Test Over Fixtures
  - [ ] RED: parity test vs pyyaml over all fixture frontmatter
  - [ ] GREEN: grow parser if a construct is uncovered, update docstring
  - [ ] REFACTOR: frontmatter locator helper
  - [ ] Verify parity passes and just check

## Section 4: Config and Artifact Validation Scripts

- [ ] Step 7: Implement resolve_config.py
  - [ ] RED: resolver tests (all tiers, merge, loud errors, defaults, exists, stderr echo)
  - [ ] Document: agreement with settings.md noted
  - [ ] GREEN: resolver with five tiers, JSON stdout, "Loaded config from" on stderr
  - [ ] RED: integration tests
  - [ ] GREEN: wire tiers
  - [ ] REFACTOR: tier structure
  - [ ] Verify coverage and just check
- [ ] Step 8: Port validate_artifacts.py
  - [ ] RED: ported suite (woodworking pass, five bad cases, remaining checks)
  - [ ] Document: 5,000 ceiling and prose-elsewhere note
  - [ ] GREEN: port onto yaml_subset, preserve checks and exit codes
  - [ ] RED: multi-finding ordering test if applicable
  - [ ] GREEN: minimal
  - [ ] REFACTOR: named check functions
  - [ ] Verify woodworking pass and each finding, just check

## Section 5: Source References

- [ ] Step 9: Port and Author the References (task)
  - [ ] Port six references (extraction-theory, interview-spec-format, archive-format, profile-format, calibration-protocol, skill-scaffold)
  - [ ] profile-format: 5,000 ceiling and fixed priority text
  - [ ] Write settings.md (matches resolve_config, documents the "Loaded config from" line)
  - [ ] Write research-contract.md (four-block shape plus no-results line)
  - [ ] Verify: no private tokens, no ../

## Section 6: The Five Skills

- [ ] Step 10: Port design and interview (task)
  - [ ] design/SKILL.md ported (four-field frontmatter at 0.1.0, settings-first, research dispatch, ends and stops)
  - [ ] interview/SKILL.md ported (one question per turn, verbatim, generic dictation note)
  - [ ] Verify: grep checks pass, inputs and outputs by path
- [ ] Step 11: Port compile and calibrate (task)
  - [ ] compile/SKILL.md ported (never resolves a tension, logs every cut)
  - [ ] calibrate/SKILL.md ported (reads profile not archive, probes never ship)
  - [ ] Verify: grep checks pass
- [ ] Step 12: Port skillify (task)
  - [ ] skillify/SKILL.md ported (exemplar, --into and default package, verbatim-archive warning, target_skill, augment, version stamping, loader)
  - [ ] Verify: grep checks pass, warning text present

## Section 7: The Research Agent

- [ ] Step 13: Port the Agent and Bind Its Contract
  - [ ] RED: contract-parity test (agent block equals research-contract.md, no model lines)
  - [ ] Document: stable contract-block markers
  - [ ] GREEN: port agent, make block byte-equal
  - [ ] RED: four-block shape and no-results line present
  - [ ] GREEN: align both
  - [ ] REFACTOR: single marker pair
  - [ ] Verify parity and just check

## Section 8: Sync Tool and Drift Guards

- [ ] Step 14: Implement sync_skills.py and Populate the Skills
  - [ ] RED: test_sync_drift and test_sync_manifest (G2 table)
  - [ ] Document: manifest-source comment
  - [ ] GREEN: sync_skills.py with manifest, copy, remove, --check
  - [ ] Run sync and commit populated skill dirs
  - [ ] RED: extra-file detection test
  - [ ] GREEN: minimal
  - [ ] REFACTOR: typed copy and diff helpers
  - [ ] Verify: --check clean, drift test fails on a byte edit, plugin validate passes, just check

## Section 9: Evals

- [ ] Step 15: Port Evals and Add the Parse-and-Path Test
  - [ ] RED: test_evals (JSON parses, fixture paths exist, README present)
  - [ ] Document: evals/README.md scratch-copy procedure
  - [ ] GREEN: port five stage evals.json, drop sync, repoint fixtures
  - [ ] RED: no evals path inside metacognition/
  - [ ] GREEN: keep evals top-level
  - [ ] Verify parse and paths, just check

## Section 10: Doctrine and Version Guards

- [ ] Step 16: Doctrine Invariants and Skill-Version Tests
  - [ ] RED: test_doctrine_invariants (tokens, model lines, ../, self-check)
  - [ ] RED: test_skill_versions (presence, SemVer 0.x shape during beta, uniformity)
  - [ ] GREEN: scoped walker and version reader; fix any violation at source
  - [ ] RED: planted-token detection test
  - [ ] GREEN: matcher catches it
  - [ ] REFACTOR: shared walker
  - [ ] Verify both guards and just check

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
