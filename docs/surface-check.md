# Surface Check

Status: not yet run.

Before the first release, the maintainer runs a manual check on each of the three surfaces: Claude Code, claude.ai chat, and Cowork.
The maintainer runs it by hand, because no automated test can load a plugin into a live surface.
This page is the record.
Each surface has a checklist and a result block.
Every result block is empty until the maintainer fills it in.

## Before You Start

Build the zip you will upload.

```bash
just release-dry
```

That writes `dist/metacognition-<version>.zip`.
The version comes from `.claude-plugin/marketplace.json`, which currently reads `0.1.1`, so the file is `dist/metacognition-0.1.1.zip`.
The `dist/` directory is gitignored.

Run this check from the locally built zip before merging this phase's pull request.
The release workflow publishes a release when a push to `main` carries a version that has no tag, so merging that pull request publishes the first pre-release.

Two one-time repository settings are needed for the workflows.
Both are things to do, not things already done.

- [ ] Enable GitHub Pages, with the `gh-pages` branch as the source.
  The branch exists only after the first docs deploy creates it.
- [ ] If the repository's Actions setting gives the workflow token read-only access, allow "Read and write permissions".

## Claude Code

Steps:

- [ ] Add the marketplace and install the plugin with the commands below.
  Look for: both commands finish without an error.

  --8<-- "README.md:install"

- [ ] List the plugin's skills.
  Look for: five skills, each invocable as `/metacognition:<stage>`: `design`, `interview`, `compile`, `calibrate`, `skillify`.
- [ ] List the plugin's agents.
  Look for: `domain-research` is listed.
  The agent ships with no model line by project rule, and this step is where its loading is confirmed.
- [ ] Open Claude Code in an empty directory and run `/metacognition:design` with a domain of your choice.
  Look for: a line reading "Extraction root:" followed by a path, before anything else.
- [ ] Continue until design asks a question.
  Look for: the domain slug printed back to you, then the first scoping question, asked alone.

Result:

- Date: `<YYYY-MM-DD>`
- Surface version or build, if visible: `<version>`
- Result: Not yet run
- Five skills invocable: Not yet run
- Notes: `<anything unexpected>`

## claude.ai Chat

Steps:

- [ ] Upload `dist/metacognition-0.1.1.zip` through Customize, Plugins.
  Look for: the plugin appears in the list with no error.
- [ ] Type "/" and invoke each of the five skills in turn: `design`, `interview`, `compile`, `calibrate`, `skillify`.
  Look for: each one is offered by the "/" menu and starts when picked.
  Record any that is missing or fails to start.
- [ ] Upload a copy of the woodworking fixture, `tests/fixtures/extractions/woodworking/`, to a conversation.
- [ ] Ask a stage to check the uploaded files, so that it runs `scripts/validate_artifacts.py` against them.
  Look for one of two outcomes:
  the script runs and reports the fixture clean, or the skill says in one line that it is applying the rules by hand.
  Record which of the two happened.
  If the script ran, record the Python version the sandbox reported.
- [ ] Type "/", pick the `design` skill, and note how the research step goes.
  Look for: the research runs inside the conversation.
  Plugin agents are ignored on this surface, so there is no separate research agent.

Result:

- Date: `<YYYY-MM-DD>`
- Surface version or build, if visible: `<version>`
- Result: Not yet run
- Five skills invocable: Not yet run
- Script ran or by-hand fallback: `<script ran | by-hand fallback>`
- Sandbox Python version, if the script ran: `<version>`
- Notes: `<anything unexpected>`

## Cowork

Steps:

- [ ] Upload `dist/metacognition-0.1.1.zip`.
  Look for: the plugin loads with no error.
- [ ] Check that the five skills load.
  Look for: `design`, `interview`, `compile`, `calibrate`, and `skillify` are all present and invocable as `/metacognition:<stage>`.
- [ ] Check that the research agent loads.
  Look for: `domain-research` is listed among the plugin's agents.
  Plugin agents load on this surface.

Result:

- Date: `<YYYY-MM-DD>`
- Surface version or build, if visible: `<version>`
- Result: Not yet run
- Five skills invocable: Not yet run
- Notes: `<anything unexpected>`

## If Something Fails

The claude.ai check rests on one assumption: the sandbox runs the shipped scripts on Python 3.11 or newer.
If the check shows an older Python, the fix is to lower the floor in `pyproject.toml` and the scripts.
It is not to add a dependency.

Record any failure in the Notes slot of the surface where it happened, and open an issue on the repository.

## Automated Checks Already Passing

Run on 2026-10-03.
These are not a substitute for the surface results above.
They cover the files in the repository, not a live surface.

| Check | Output |
|---|---|
| `claude plugin validate ./metacognition` | Validation passed |
| `just release-dry` | Wrote `dist/metacognition-0.1.1.zip`, 44 entries, with `metacognition/` as the single top-level entry |
| `python3 tools/sync_skills.py --check` | Exit 0, no output |
| `uv run pytest -q` | 383 passed |
