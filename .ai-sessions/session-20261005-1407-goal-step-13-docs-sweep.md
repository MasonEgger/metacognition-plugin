# Session: Step 13, Update the Stage Pages and the Front Door

## Summary

The maintainer's one review note on the plan was to make sure the docs were updated.
The stage pages, Configuration, Privacy, and the README still described the old interview and the old skillify, and no page mentioned the two writing scripts or the companion plugin.
Step 13 brings the docs in line with the reworked skills, references, and scripts from Steps 8 to 12, then sweeps every page.

## What Changed

- Pages changed: README, docs/index.md, docs/getting-started.md, docs/configuration.md, docs/privacy.md, the five stage pages (interview, design, compile, calibrate, skillify), and the formats index, archive, and profile pages.
- The plugin-dev recommendation sits inside the README's install snippet section, so it also renders on Getting Started and inside the surface checklist's Claude Code step.
  It gives no install command because no source states one.
- The three snippet marker pairs in the README are intact, and the beta section still reads 0.1.1.
- `todo.md` has Step 13 and its sub-items checked.

## Docs Sweep

Pages checked against the five SKILL.md files, src/references/, the script docstrings, and the research agent.

- README.md: interview wording and stage-table row changed from "one question at a time"; plugin-dev companion paragraph added inside the install snippet (markers intact, beta section still names 0.1.1).
- docs/index.md: "one at a time" sentence and the Interview table row reworded for batteries.
- docs/getting-started.md: the research-agent paragraph now says interview dispatches it too and records an unresolved deferral with no web access; the scripts paragraph now lists writing interview entries and keeping the token estimate current. Python 3.12 line already correct. Install section shows the plugin-dev paragraph through the snippet.
- docs/configuration.md: exemplar row now an advanced option "whose shape skillify may use" (was "should match"); line 94 now says a missing exemplar is skipped silently (was "Skillify tells you"); added the by-hand "Loaded config from" sentence from settings.md; added that exemplar can stay unset.
- docs/privacy.md: research findings with source links and exports travel with the archive, including into a skillify package.
- docs/method.md: no change needed. Still says sixteen rules; rule 16 table has the verdict battery and evidence probe rows and matches the reference.
- docs/stages/index.md: no change needed. No one-at-a-time line, no stage summaries that changed.
- docs/stages/interview.md: turns, batteries, picker and lettered fallback, same-turn research and ratification, no-web behavior, progress note contents, exports, probe counting for floors, entries saved as answered.
- docs/stages/design.md: artifact check and register coverage rule added; scoping "one at a time" left as is.
- docs/stages/compile.md: ratified practice with citation, exports to the compile log, unresolved research listed as not yet settled, token estimate script.
- docs/stages/calibrate.md: token estimate refreshed by the same script after a fold-back.
- docs/stages/skillify.md: plugin-dev baseline and its fallback, augment structural assessment and the person's choice, dry-run behavior, exemplar as advanced and silent, exports as follow-up work. Role questions "one at a time" left as is.
- docs/formats/index.md: structure-check list gained battery items and the Open research and Exports id checks; added the two writing scripts.
- docs/formats/archive.md: added that interview appends each entry with archive_append.py, or by hand when it cannot run.
- docs/formats/profile.md: token_estimate wording (frontmatter entry and Token Contract) now names update_token_estimate.py. The source reference src/references/profile-format.md does not mention the script (it is not wrong, only silent); the page's added sentence traces to the compile and calibrate SKILL.md files.
- docs/formats/interview-spec.md: no change needed (Step 2 already covers probe counting, register coverage, artifact availability).
- docs/formats/calibration-round.md: no change needed.
- docs/surface-check.md: no change needed (Python 3.12 assumption already stated; version record is Step 14).
- mkdocs.yml: no change needed (no new pages).
- CLAUDE.md: no change needed (sixteen pages and the three include markers still true).

## Verification

- `uv run pytest -q`: 506 passed.
- `just check` exits 0, including the strict docs build.
- The prose gate exits 0.
- The validator was clean at iteration 1. It independently verified every claim against the sources and found no stale sentence on any page.

## Deviations from Plan

- Plan said: implementation-notes.md is gitignored.
- Deviated: .gitignore has no entry for it, so the file shows as untracked. It was written anyway and then absorbed into this summary and deleted.
- Impact: it was never staged. Suggestion for the maintainer: add an ignore line for `.ai-sessions/implementation-notes.md`; none was added here.

## Observations

- One open item: the profile format reference does not yet name the estimate script, so docs/formats/profile.md says more than its source (spec.component-j-reference-parity, info).
- For Step 14: add one sentence naming `scripts/update_token_estimate.py` to src/references/profile-format.md (the token_estimate field entry and the Token Contract), run `just sync`, and confirm docs/formats/profile.md agrees.
