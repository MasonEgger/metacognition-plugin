# Accomplishment: Port From Private Main

**Archived**: 2026-10-03
**Convergence**: converged (22 of 22 steps checked)

## Spec Slice

The first phase of `spec.md`: port the private metacognition plugin, read at commit `2806854`, into a public marketplace repo.
Done meant that a person with no access to the private repo can install the plugin on Claude Code, Cowork, and claude.ai chat and run all five stages, with nothing changed in the private repo.

The slice covered goals G1 to G8 and components A to I:

- The marketplace and plugin manifests, with the installable plugin under `metacognition/`.
- `src/references/` and `src/scripts/` as the single source of truth, copied into each skill by a sync tool, with drift and manifest guards.
- Three shipped scripts that use only the standard library: a strict YAML subset parser, a tiered settings resolver, and the artifact validator.
- The five stage skills, the research agent, the evals, and the woodworking fixtures.
- Doctrine and version guards, a packager with refusals, a prose gate, CI and release workflows, a docs site, and a README.

The profile token ceiling stayed at 5,000 in this phase by design.

## What Got Done

- Step 1: Python toolchain and justfile.
- Step 2: plugin and marketplace manifests, directory skeleton, and minimal docs.
- Step 3: the good fixtures ported from the private source.
- Step 4: the five bad-extraction cases ported.
- Step 5: `yaml_subset.py`, the parser for artifact frontmatter.
- Step 6: a PyYAML parity test over every fixture frontmatter, with bare-date support.
- Step 7: `resolve_config.py`, the tiered settings resolver.
- Step 8: `validate_artifacts.py` ported onto the subset parser.
- Step 9: the eight shared references under `src/references/`.
- Steps 10 to 12: the design, interview, compile, calibrate, and skillify skills.
- Step 13: the domain-research agent, with its output contract held equal to the reference by a test.
- Step 14: `sync_skills.py`, the populated skill directories, and the drift and manifest guards.
- Step 15: the five stage evals and a parse-and-path test.
- Step 16: the doctrine invariant and skill-version guards.
- Step 17: `build_zips.py` and its refusals.
- Step 18: the prose gate, run over the repo's own prose inside the test suite.
- Step 19: the CI and release workflows, with every action pinned to a commit SHA.
- Step 20: the docs site.
- Step 21: the README.
- Step 22: the surface checklist, prepared with every result slot empty.

After the plan finished:

- Pull request 1 merged the phase to `main`.
- Pull request 2 fixed the release workflow's tag guard, which read an exit code on the line after the command and so never ran under the runner's `bash -e`.
- `v0.1.0` was published as a pre-release on 2026-10-02, and the docs site went live.

## Deferred or Dropped

- The live surface check on Claude Code, claude.ai chat, and Cowork was prepared but not run. The maintainer accepted that for a 0.1 pre-release.
- The profile ceiling raise to 10,000 was out of scope by design and is tracked as issue 3.
- The interview retro's recommendations were out of scope and are tracked as issue 4.
- The interview skill carries no question-count range, because the private text never states one.
- The packager does not refuse a `hooks/` directory or an MCP config file. Neither exists in the plugin today.
- The CI workflow pins its task runner by version, not by hash.
- The prose gate enforces less than the vendored writing rules describe.

## Notable Decisions

- Versions are SemVer `0.x` during beta and flip to CalVer at 1.0, ruled by the maintainer during plan review.
- Marketplace install is the primary path on all three surfaces. The release zip is the alternate path and the release asset.
- The settings resolver prints the path of any config file it loads, so a person can see which file took effect.
- Evals live at the top level, never inside the plugin, and are not run as a gate.
- The `woodworking-truncated` fixture fails the validator on purpose. A test pins that one finding, and the fixture is not to be fixed.
- Compile's by-hand token count uses characters, not bytes, so it matches what the validator counts.
- The repo slug and the credit line cannot appear under `docs/`, which the doctrine guard scans. They live in `README.md` between snippet markers and are included at build time.
- Step 5 skipped its RED phase, and the validator pass caught a quote and comment parsing bug that was then fixed test-first.
- The sync tool's first symlink fix covered only a linked directory. Validation caught the linked-file case, and the second fix closed the class.
- Fixture edits made under the port rules left stored token estimates stale. They were corrected in eight fixtures when the validator arrived.
