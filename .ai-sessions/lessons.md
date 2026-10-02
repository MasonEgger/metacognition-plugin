# Lessons Learned

## Recent
<!-- 10 most recent lessons, newest first -->
- When a port rule edits a fixture's body, update every frontmatter value derived from that body (such as token_estimate) in the same step; Steps 3 and 4 reworded profile line 25 and left token_estimate stale, and the Step 8 validator test then fired on eight fixtures (2026-10-01)
- Before treating a ported fixture that fails validation as broken, check the source history for whether the failure is intentional (woodworking-truncated fails archive-category-count on purpose), then pin the expected finding with a test (2026-10-01)
- A shipped script that imports a sibling module must work both as a package import under pytest and as a direct `python3 scripts/<name>.py` run: import the package path first, fall back to the sibling name on ModuleNotFoundError, and prove the direct case with a subprocess test from another working directory (2026-10-01)
- PyYAML's safe_load returns datetime.date for a bare YYYY-MM-DD scalar, so a parser that must match it has to return a date object, and JSON output then needs a default hook to print dates as ISO strings (2026-10-01)
- mypy exits 2 when a directory listed in its configured `files` holds no .py files, so an empty tools/ breaks `just check`; the recipe is narrowed to `src/scripts tests` until Step 14 adds tools/*.py, and must be restored then (2026-10-01)
- In a Feature step, run the new tests and see them fail before writing the implementation, and log any deviation to .ai-sessions/implementation-notes.md at the time it happens (2026-10-01)
- When stripping a comment from a line, quote tracking must apply the same escape rules as the string reader: '' doubling in single quotes and backslash escapes in double quotes; otherwise a # after an escaped quote is read as a comment start (2026-10-01)
- When a port rule targets a kind of file (such as each extraction's own README status table), check every file of that kind, not only the one top-level file; in a plan section with Tools: none nothing downstream catches a missed rule, so grep for the rule's target across the whole ported tree before finalizing (2026-10-01)
- `/bpe:goal` pre-flight needs four things in place: a feature branch, a clean tree with the planning files committed, `goal.md` in `.gitignore`, and a verification command (2026-10-01)
- pytest exits 5 when it collects no tests; a goal run whose early steps have no tests needs a verification command that accepts exit 5 (2026-10-01)

## Workflow
- When a port rule edits a fixture's body, update every frontmatter value derived from that body (such as token_estimate) in the same step; Steps 3 and 4 reworded profile line 25 and left token_estimate stale, and the Step 8 validator test then fired on eight fixtures (2026-10-01)
- In a Feature step, run the new tests and see them fail before writing the implementation, and log any deviation to .ai-sessions/implementation-notes.md at the time it happens (2026-10-01)
- When a port rule targets a kind of file (such as each extraction's own README status table), check every file of that kind, not only the one top-level file; in a plan section with Tools: none nothing downstream catches a missed rule, so grep for the rule's target across the whole ported tree before finalizing (2026-10-01)
- `/bpe:goal` pre-flight needs four things in place: a feature branch, a clean tree with the planning files committed, `goal.md` in `.gitignore`, and a verification command (2026-10-01)
- Before the repo has a `pyproject.toml`, `/bpe:goal` cannot autodetect a test runner; put a `**Verification command:**` line in spec.md's `## Available tooling` section (2026-10-01)
- A review ruling that contradicts a spec invariant needs a spec edit in the same pass, then `/bpe:plan --regen`, or plan and spec drift (2026-10-01)

## Testing
- Before treating a ported fixture that fails validation as broken, check the source history for whether the failure is intentional (woodworking-truncated fails archive-category-count on purpose), then pin the expected finding with a test (2026-10-01)
- pytest exits 5 when it collects no tests; a goal run whose early steps have no tests needs a verification command that accepts exit 5 (2026-10-01)

## Tooling
- mypy exits 2 when a directory listed in its configured `files` holds no .py files, so an empty tools/ breaks `just check`; the recipe is narrowed to `src/scripts tests` until Step 14 adds tools/*.py, and must be restored then (2026-10-01)
- Start the `/bpe:review` server with the 2-hour background limit (`timeout: 7200000`); the 30-minute default kills it mid-review (2026-10-01)
- The review server picks a random port on every start and bakes it into the page's Save button; if a tab is stranded on a dead port, relay that port to the new server so Save still works (2026-10-01)
- `pkill -f <pattern>` kills the shell that runs it when the pattern appears in that shell's own command line; kill by PID (2026-10-01)

## Plugin Development
- Marketplace install works on Claude Code, Cowork, and claude.ai; the release zip is an alternate upload path and the Release asset, not a requirement (2026-10-01)

## Python
- A shipped script that imports a sibling module must work both as a package import under pytest and as a direct `python3 scripts/<name>.py` run: import the package path first, fall back to the sibling name on ModuleNotFoundError, and prove the direct case with a subprocess test from another working directory (2026-10-01)
- When stripping a comment from a line, quote tracking must apply the same escape rules as the string reader: '' doubling in single quotes and backslash escapes in double quotes; otherwise a # after an escaped quote is read as a comment start (2026-10-01)
- PyYAML's safe_load returns datetime.date for a bare YYYY-MM-DD scalar, so a parser that must match it has to return a date object, and JSON output then needs a default hook to print dates as ISO strings (2026-10-01)
