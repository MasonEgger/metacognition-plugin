# Lessons Learned

## Recent
<!-- 10 most recent lessons, newest first -->
- `/bpe:goal` pre-flight needs four things in place: a feature branch, a clean tree with the planning files committed, `goal.md` in `.gitignore`, and a verification command (2026-10-01)
- pytest exits 5 when it collects no tests; a goal run whose early steps have no tests needs a verification command that accepts exit 5 (2026-10-01)
- Before the repo has a `pyproject.toml`, `/bpe:goal` cannot autodetect a test runner; put a `**Verification command:**` line in spec.md's `## Available tooling` section (2026-10-01)
- Start the `/bpe:review` server with the 2-hour background limit (`timeout: 7200000`); the 30-minute default kills it mid-review (2026-10-01)
- The review server picks a random port on every start and bakes it into the page's Save button; if a tab is stranded on a dead port, relay that port to the new server so Save still works (2026-10-01)
- `pkill -f <pattern>` kills the shell that runs it when the pattern appears in that shell's own command line; kill by PID (2026-10-01)
- Marketplace install works on Claude Code, Cowork, and claude.ai; the release zip is an alternate upload path and the Release asset, not a requirement (2026-10-01)
- A review ruling that contradicts a spec invariant needs a spec edit in the same pass, then `/bpe:plan --regen`, or plan and spec drift (2026-10-01)

## Workflow
- `/bpe:goal` pre-flight needs four things in place: a feature branch, a clean tree with the planning files committed, `goal.md` in `.gitignore`, and a verification command (2026-10-01)
- Before the repo has a `pyproject.toml`, `/bpe:goal` cannot autodetect a test runner; put a `**Verification command:**` line in spec.md's `## Available tooling` section (2026-10-01)
- A review ruling that contradicts a spec invariant needs a spec edit in the same pass, then `/bpe:plan --regen`, or plan and spec drift (2026-10-01)

## Testing
- pytest exits 5 when it collects no tests; a goal run whose early steps have no tests needs a verification command that accepts exit 5 (2026-10-01)

## Tooling
- Start the `/bpe:review` server with the 2-hour background limit (`timeout: 7200000`); the 30-minute default kills it mid-review (2026-10-01)
- The review server picks a random port on every start and bakes it into the page's Save button; if a tab is stranded on a dead port, relay that port to the new server so Save still works (2026-10-01)
- `pkill -f <pattern>` kills the shell that runs it when the pattern appears in that shell's own command line; kill by PID (2026-10-01)

## Plugin Development
- Marketplace install works on Claude Code, Cowork, and claude.ai; the release zip is an alternate upload path and the Release asset, not a requirement (2026-10-01)
