# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## State of the Repo

The repo holds planning documents, the Python toolchain, the plugin and marketplace manifests, the directory skeleton, and a placeholder docs site.
`tests/fixtures/` holds the ported woodworking extractions and the woodshop plugin fixture; they are verbatim data, so do not edit them or lint their prose.
Skills, scripts, and tools are still to come; their directories hold only `.gitkeep` placeholders.
`spec.md` is the authority for what gets built, `plan.md` is the 22-step build order, and `todo.md` tracks progress.
Read the spec's Invariants, Non-goals, and Deferred list before changing anything: they are hard constraints, and a step that crosses one needs a spec change first.

## What Is Being Built

Metacognition is a Claude plugin that captures how one person judges work in a field and packages that judgment as a skill.
It is five stages, each its own skill, run in order: design, interview, compile, calibrate, skillify.
No stage starts the next one.
The plugin must work on three surfaces: Claude Code, Cowork, and claude.ai chat.

## Architecture

The repo is a plugin marketplace with the installable plugin in `metacognition/`.

`src/references/` and `src/scripts/` are the single source of truth for files the skills share.
`tools/sync_skills.py` copies each skill its slice of `src/` into `metacognition/skills/<stage>/references/` and `scripts/`, using a manifest declared by hand in the tool.
Never edit a synced copy; change `src/` and run `just sync`.
A pytest drift guard fails when a copy differs from its source, and a manifest guard fails when a SKILL.md and its slice disagree.

Each skill must run alone in the claude.ai per-skill sandbox, which drives three rules.
A skill reaches its files by relative path only, so `${CLAUDE_PLUGIN_ROOT}` and `../` never appear in a skill.
Scripts under `src/scripts/` import only the Python standard library and run on Python 3.11 or newer.
When a script cannot run, the skill applies the same rules by hand from its references.

`yaml_subset.py` is a strict parser for the YAML subset the artifact formats use; `resolve_config.py` and `validate_artifacts.py` build on it.
`tests/test_doctrine_invariants.py` greps the shipped trees for private tokens, model pins, and `../` paths.

## Porting From the Private Source

Most skills, references, fixtures, and evals are ported from the `claude-code-plugin-private` repo at commit `2806854`.
Read it only with `git -C <private> show 2806854:<path>`; never read its working tree and never modify it.
Every ported file goes through the Component F port rules in `spec.md`.
Never commit the private repo's filesystem path.

## Commands

These recipes exist in the `justfile`.
`just docs-build` works now.
`sync` and `release-dry` depend on files that later plan steps add, so they fail until those steps land.

- `just check`: the full gate (ruff format check, ruff check, mypy strict, pytest, `mkdocs build --strict`).
- `just test`: pytest only.
- `uv run pytest tests/test_yaml_subset.py::test_name`: a single test.
- `just fmt`: format and autofix.
- `just sync`: regenerate the synced skill copies from `src/`.
- `just docs-build` and `just docs-serve`: the mkdocs site.
- `just release-dry`: build the plugin zip into `dist/`.

## Conventions

- Versions are uniform across every SKILL.md, `plugin.json`, and `marketplace.json`: SemVer `0.x` during beta, CalVer at 1.0, and they move only on the maintainer's ruling.
- SKILL.md frontmatter carries exactly `name`, `version`, `description`, and `compatibility`; no `model:` line anywhere.
- The profile token ceiling is 5,000 in this phase.
- Prose follows `.claude/rules/vendored/writing.md`: no em-dash or en-dash, straight quotes, Title Case headings, one sentence per line in committed Markdown.
- Test-first for anything under `src/scripts/` and `tools/`; tests assert behavior, not the presence of a mechanism.
- GitHub Actions are pinned to commit SHAs.
