# Settings

Every stage starts by resolving two settings and stating the extraction root it will use in one line.
`python3 scripts/resolve_config.py` does the resolving.
This reference holds the same rules so a skill can apply them by hand when the script cannot run: no code execution on the surface, or an interpreter older than Python 3.12.
When a skill falls back to the by-hand rules, it says so in one line.
The script and this reference must agree exactly; a change to one is a change to both.

## The Two Keys

| Key | Meaning | Default |
|---|---|---|
| `extractions_root` | Where extraction directories live. Each extraction is `<root>/<slug>/`. | `extractions` |
| `exemplar` | Path to a skill, either its directory or its `SKILL.md`, whose shape skillify should match. | none |

No other key exists.
Every setting has a default, so no config file is ever required.

## The Five Tiers

The tiers are listed highest first.
A higher tier wins, key by key.

1. `run-time`: a value the person passed for this run.
   That is a `--set key=value` argument, a `--extractions-root` flag, or a setting the person stated in the conversation or in Project instructions.
2. `project`: `./.claude/metacognition.local.md` in the working directory.
   The file is looked up in the working directory only; there is no upward search through parent directories.
3. `user-claude`: `~/.claude/metacognition.local.md`.
4. `user-xdg`: `$XDG_CONFIG_HOME/metacognition/config.yaml`.
   When `XDG_CONFIG_HOME` is unset or empty, the file is `~/.config/metacognition/config.yaml`.
5. `default`: `extractions_root` is `extractions`; `exemplar` is unset.

The names in backticks are the tier names the script prints as `source`.

Tiers 2 and 3 are Markdown files whose YAML frontmatter holds the settings; the body below the frontmatter is ignored.
A file with no frontmatter sets nothing.
Tier 4 is a plain YAML file, read whole.

When both user files (tiers 3 and 4) set the same key, `~/.claude/` wins over the XDG file.

### Per-Key Merging

Each key resolves on its own.
A project file that sets only `exemplar` leaves `extractions_root` to come from the next tier down that sets it, and from the default if none does.
Settings from different tiers combine; a file never replaces the whole set.

### Every Tier Is Read

Every tier is read even when a higher tier already won a key.
A bad file at a lower tier is therefore an error even when a higher tier would have supplied the value.

### On claude.ai

Only tier 1 and the defaults apply on claude.ai chat.
The config files are not consulted there.
The person states a setting in the first message or in Project instructions, and the skill treats it as a run-time value.

## Path Resolution

The winning value becomes an absolute path:

- A leading `~` expands to the home directory.
- A relative value resolves against the working directory.
- An absolute value is kept as given.

`extractions_root` resolves the same way as `exemplar`.
The default `extractions` therefore means `./extractions` under the working directory.

## Errors

Three conditions are loud errors.
Each one stops the stage with one line that names the file (or `--set`) and the key.

- **Unknown key.** Any key other than `extractions_root` and `exemplar`.
- **Wrong type.** A value that is not a non-empty string.
  An empty string, a list, a map, a number, or a boolean is a wrong-type error.
- **Unparseable file.** A config file whose YAML does not parse.

These are not errors:

- **A missing file**, at any tier. A missing file is skipped silently.
- **A null value.** `exemplar:` with nothing after the colon counts as unset, so the next tier down supplies the value.
- **An exemplar that does not exist.** The setting resolves normally and is reported as not existing.
  Skillify tells the person the exemplar was not found and continues on `references/skill-scaffold.md` alone.

### Run-Time Values

A `--set` value is checked the same way as a file value.
A bad `--set` is a loud error: an unknown key, an argument with no `=`, or an empty value.
When the same key is set twice, the last one wins.
`--extractions-root VALUE` is an alias for `--set extractions_root=VALUE` and wins over any `--set extractions_root=...` given in the same call.

## Announcing the Config

Each config file that was actually read is announced with one line: `Loaded config from: <path>`.
The script prints these lines on stderr, so its stdout stays pure JSON.
A file that exists but sets nothing is still announced.
A missing file is not.
In the by-hand fallback, the skill states the same line for each file it read.

## Using the Script

A skill runs the resolver from its own directory:

```bash
python3 scripts/resolve_config.py
python3 scripts/resolve_config.py --extractions-root work/interviews
python3 scripts/resolve_config.py --set extractions_root=work/interviews --set exemplar=~/skills/jig-design
```

The script prints one JSON object on stdout and exits 0:

```json
{
  "extractions_root": {
    "value": "/home/sam/projects/shop/extractions",
    "source": "default"
  },
  "exemplar": {
    "value": "/home/sam/skills/jig-design",
    "source": "user-claude",
    "exists": true
  }
}
```

- `value` is an absolute path, or `null` when the key is unset.
- `source` is the tier name that supplied the value, one of `run-time`, `project`, `user-claude`, `user-xdg`, `default`.
- `exists` appears on `exemplar` only. It is `true` when the path exists and `false` when it does not or when `value` is `null`.

On a loud error the script exits 2 and prints one line on stderr naming the file and the key, for example `/home/sam/projects/shop/.claude/metacognition.local.md: unknown key 'extraction_root' (allowed: extractions_root, exemplar)`.

## Config File Forms

The project file and the `~/.claude` file share one form: YAML frontmatter between `---` lines, then any Markdown the person wants.
The body is ignored.

```markdown
---
extractions_root: work/interviews
exemplar: ~/skills/jig-design
---

Notes for myself about these settings.
```

The XDG file is plain YAML with the same keys and no `---` lines:

```yaml
extractions_root: ~/metacognition
exemplar: ~/skills/jig-design
```

Either form may set one key or both.

## Applying the Rules by Hand

When the script cannot run, resolve each key on its own, in this order:

1. If the person stated a value in this conversation, in Project instructions, or as a `--extractions-root` flag, use it. Tier 1.
2. Otherwise read `./.claude/metacognition.local.md` if the surface can read files. Use the key from its frontmatter if present and not null.
3. Otherwise read `~/.claude/metacognition.local.md` the same way.
4. Otherwise read `$XDG_CONFIG_HOME/metacognition/config.yaml`, or `~/.config/metacognition/config.yaml` when the variable is unset.
5. Otherwise use the default.

Then check every file that was read for an unknown key or a wrong type, even if a higher tier won, and stop with one line naming the file and key when one is found.
Make each winning path absolute as described under Path Resolution.
State `Loaded config from: <path>` for each file read, then state the extraction root in one line.
