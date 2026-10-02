# Configuration

Nothing needs configuring.
Every setting has a default, and a missing config file is never an error.
This page lists the two settings, the five tiers they can come from, and the options on claude.ai.

Every stage begins by resolving these settings and stating the extraction root it will use in one line.
`python3 scripts/resolve_config.py` does the resolving.
When the script cannot run, because the surface has no code execution or the interpreter is older than Python 3.11, the stage applies the same rules by hand and says so in one line.

## The Two Keys

| Key | Meaning | Default |
|---|---|---|
| `extractions_root` | Where extraction directories live. Each extraction is `<root>/<slug>/`. | `extractions` |
| `exemplar` | Path to a skill, either its directory or its `SKILL.md`, whose shape skillify should match. | none |

No other key exists.

## The Five Tiers

The tiers are listed highest first.
A higher tier wins, key by key.

| Tier | Name | Source |
|---|---|---|
| 1 | `run-time` | A value you passed for this run: a `--set key=value` argument, a `--extractions-root` flag, or a setting you stated in the conversation or in Project instructions. |
| 2 | `project` | `./.claude/metacognition.local.md` in the working directory. The file is looked up in the working directory only, with no search through parent directories. |
| 3 | `user-claude` | `~/.claude/metacognition.local.md` |
| 4 | `user-xdg` | `$XDG_CONFIG_HOME/metacognition/config.yaml`, or `~/.config/metacognition/config.yaml` when `XDG_CONFIG_HOME` is unset or empty. |
| 5 | `default` | `extractions_root` is `extractions`. `exemplar` is unset. |

When both user files (tiers 3 and 4) set the same key, `~/.claude/` wins over the XDG file.

Each key resolves on its own.
A project file that sets only `exemplar` leaves `extractions_root` to come from the next tier down that sets it, and from the default if none does.

### Config File Forms

The project file and the `~/.claude` file are Markdown files with YAML frontmatter.
Only the frontmatter is read.
The body is ignored, so you can leave notes to yourself there.

```markdown
---
extractions_root: work/interviews
exemplar: ~/skills/jig-design
---

Notes for myself about these settings.
```

The XDG file is plain YAML with the same keys and no `---` lines.

```yaml
extractions_root: ~/metacognition
exemplar: ~/skills/jig-design
```

Either form can set one key or both.
A file with no frontmatter sets nothing.

### Paths

A leading `~` expands to your home directory.
A relative value resolves against the working directory.
An absolute value is kept as given.
The default `extractions` therefore means `./extractions` under the working directory.

## On claude.ai

Only tier 1 and the defaults apply on claude.ai chat.
The config files are not consulted there.
You have two options:

- State the setting in your first message.
- Put the setting in the Project instructions.

Either way, the skill treats it as a run-time value.

## Errors

Three conditions are loud errors.
Each stops the stage with one line that names the file (or `--set`) and the key.

- An unknown key. Anything other than `extractions_root` and `exemplar`.
- A wrong type. A value that is not a non-empty string. An empty string, a list, a map, a number, or a boolean is a wrong-type error.
- An unparseable file. A config file whose YAML does not parse.

These are not errors:

- A missing file, at any tier. It is skipped silently.
- A null value. `exemplar:` with nothing after the colon counts as unset, so the next tier down supplies the value.
- An exemplar that does not exist. Skillify tells you the exemplar was not found and continues on its built-in scaffold alone.

Every tier is read even when a higher tier already won a key.
A bad file at a lower tier is therefore an error even when a higher tier would have supplied the value.

A bad `--set` is an error too: an unknown key, an argument with no `=`, or an empty value.
When the same key is set twice, the last one wins.
`--extractions-root VALUE` is an alias for `--set extractions_root=VALUE`, and it wins over any `--set extractions_root=...` in the same call.

## Which Config Was Read

Each config file that was actually read is announced with one line: `Loaded config from: <path>`.
A file that exists but sets nothing is still announced.
A missing file is not.
