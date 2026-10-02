# Lessons Learned

## Recent
<!-- 10 most recent lessons, newest first -->
- When a guard over a docs tree forbids a string the docs must display, keep the string in a file the guard exempts by design and include it at build time with a checked snippet, so the guard stays whole and the build fails if the source section goes missing (2026-10-01)
- Look up a GitHub Action's commit SHA from the tag ref through the API, dereference annotated tags, and confirm the result against the commits endpoint; never write a SHA from memory (2026-10-01)
- Once a prose gate scans the repo's own files, every session summary, lesson, and CLAUDE.md edit written afterward is checked by it, so run the gate before committing and never quote the banned list or a dirty fixture's lines in prose; say the rule name instead (2026-10-01)
- A packaging tool should collect and report every refusal in one run, write to a temporary name and rename it, and be tested for leaving an existing artifact untouched when it refuses (2026-10-01)
- A guard test over an existing tree cannot show RED on the tree itself, so write its detection logic test-first against planted input under tmp_path, then point it at the real tree, and never plant anything in the repo (2026-10-01)
- When adapting an eval to changed behavior, check each expectation against the exact text of the skill it tests; an expectation the skill does not state can fail a correct run, so the eval follows the skill and a gap in the skill is reported, not papered over in the eval (2026-10-01)
- A tool that deletes or overwrites files in a directory must check for symlinks at every level it touches, the directory and each entry, and its drift check must not read through a link, or a link passes as a valid copy (2026-10-01)
- When fixing one case of a class (a symlinked directory), list the sibling cases (symlinked file, dangling link, link to a directory, link at a non-slice name) and test them in the same pass; the first sync_skills fix covered only the directory and the file case slipped through to validation (2026-10-01)
- To hold a block inside one file equal to another file, delimit it with a marker pair that appears exactly once, and have the test fail on a missing, repeated, or empty block, not only on a mismatch (2026-10-01)
- When a skill writes files into another skill, give every path in the produced skill one consistent target prefix (`<target-skill>/references/archive.md`) so tooling can tell them from the skill's own references (2026-10-01)

## Security
- A tool that deletes or overwrites files in a directory must check for symlinks at every level it touches, the directory and each entry, and its drift check must not read through a link, or a link passes as a valid copy (2026-10-01)

## Workflow
- Once a prose gate scans the repo's own files, every session summary, lesson, and CLAUDE.md edit written afterward is checked by it, so run the gate before committing and never quote the banned list or a dirty fixture's lines in prose; say the rule name instead (2026-10-01)
- When adapting an eval to changed behavior, check each expectation against the exact text of the skill it tests; an expectation the skill does not state can fail a correct run, so the eval follows the skill and a gap in the skill is reported, not papered over in the eval (2026-10-01)
- When fixing one case of a class (a symlinked directory), list the sibling cases (symlinked file, dangling link, link to a directory, link at a non-slice name) and test them in the same pass; the first sync_skills fix covered only the directory and the file case slipped through to validation (2026-10-01)
- When a ported skill tells the reader to reproduce a script's computation by hand, check the instruction against the script itself, not only the source text; compile said byte length (`wc -c`) while validate_artifacts.py counts decoded characters, so it now says `wc -m` (2026-10-01)
- A number in a spec overview or plan step (such as "60 to 120 questions") is not a rule to port unless the source text states it; grep the source before adding it to a ported skill (2026-10-01)
- When a port replaces "he" with "they", every verb in a list after the pronoun needs the plural form, not only the first one; re-read each changed sentence in full (2026-10-01)
- When a port rule edits a fixture's body, update every frontmatter value derived from that body (such as token_estimate) in the same step; Steps 3 and 4 reworded profile line 25 and left token_estimate stale, and the Step 8 validator test then fired on eight fixtures (2026-10-01)
- In a Feature step, run the new tests and see them fail before writing the implementation, and log any deviation to .ai-sessions/implementation-notes.md at the time it happens (2026-10-01)
- When a port rule targets a kind of file (such as each extraction's own README status table), check every file of that kind, not only the one top-level file; in a plan section with Tools: none nothing downstream catches a missed rule, so grep for the rule's target across the whole ported tree before finalizing (2026-10-01)
- `/bpe:goal` pre-flight needs four things in place: a feature branch, a clean tree with the planning files committed, `goal.md` in `.gitignore`, and a verification command (2026-10-01)
- Before the repo has a `pyproject.toml`, `/bpe:goal` cannot autodetect a test runner; put a `**Verification command:**` line in spec.md's `## Available tooling` section (2026-10-01)
- A review ruling that contradicts a spec invariant needs a spec edit in the same pass, then `/bpe:plan --regen`, or plan and spec drift (2026-10-01)

## Testing
- A guard test over an existing tree cannot show RED on the tree itself, so write its detection logic test-first against planted input under tmp_path, then point it at the real tree, and never plant anything in the repo (2026-10-01)
- To hold a block inside one file equal to another file, delimit it with a marker pair that appears exactly once, and have the test fail on a missing, repeated, or empty block, not only on a mismatch (2026-10-01)
- Before treating a ported fixture that fails validation as broken, check the source history for whether the failure is intentional (woodworking-truncated fails archive-category-count on purpose), then pin the expected finding with a test (2026-10-01)
- pytest exits 5 when it collects no tests; a goal run whose early steps have no tests needs a verification command that accepts exit 5 (2026-10-01)

## Tooling
- A packaging tool should collect and report every refusal in one run, write to a temporary name and rename it, and be tested for leaving an existing artifact untouched when it refuses (2026-10-01)
- mypy exits 2 when a directory listed in its configured `files` holds no .py files, so an empty tools/ broke `just check`; the recipe was narrowed until Step 14 added tools/sync_skills.py and is plain `uv run mypy` again (2026-10-01)
- Start the `/bpe:review` server with the 2-hour background limit (`timeout: 7200000`); the 30-minute default kills it mid-review (2026-10-01)
- The review server picks a random port on every start and bakes it into the page's Save button; if a tab is stranded on a dead port, relay that port to the new server so Save still works (2026-10-01)
- `pkill -f <pattern>` kills the shell that runs it when the pattern appears in that shell's own command line; kill by PID (2026-10-01)

## Plugin Development
- When a skill writes files into another skill, give every path in the produced skill one consistent target prefix (`<target-skill>/references/archive.md`) so tooling can tell them from the skill's own references (2026-10-01)
- Marketplace install works on Claude Code, Cowork, and claude.ai; the release zip is an alternate upload path and the Release asset, not a requirement (2026-10-01)

## DevOps
- Look up a GitHub Action's commit SHA from the tag ref through the API, dereference annotated tags, and confirm the result against the commits endpoint; never write a SHA from memory (2026-10-01)

## Python
- A shipped script that imports a sibling module must work both as a package import under pytest and as a direct `python3 scripts/<name>.py` run: import the package path first, fall back to the sibling name on ModuleNotFoundError, and prove the direct case with a subprocess test from another working directory (2026-10-01)
- When stripping a comment from a line, quote tracking must apply the same escape rules as the string reader: '' doubling in single quotes and backslash escapes in double quotes; otherwise a # after an escaped quote is read as a comment start (2026-10-01)
- PyYAML's safe_load returns datetime.date for a bare YYYY-MM-DD scalar, so a parser that must match it has to return a date object, and JSON output then needs a default hook to print dates as ISO strings (2026-10-01)

## Documentation
- When a guard over a docs tree forbids a string the docs must display, keep the string in a file the guard exempts by design and include it at build time with a checked snippet, so the guard stays whole and the build fails if the source section goes missing (2026-10-01)
