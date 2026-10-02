# ABOUTME: Resolves the two metacognition settings across five tiers and prints them as JSON.
# ABOUTME: Standard library plus the sibling yaml_subset module; runs from a skill's scripts/ directory.
"""Resolve the metacognition settings across five tiers. Standard library only.

Two keys exist and no others: "extractions_root" (default "extractions") and "exemplar" (default none).
Tiers, highest first, merged key by key:

1. run-time     --set key=value (repeatable; the last one for a key wins), or --extractions-root VALUE
               (an alias for --set extractions_root=VALUE, applied after every --set)
2. project      ./.claude/metacognition.local.md   YAML frontmatter, body ignored, working directory only
3. user-claude  ~/.claude/metacognition.local.md   YAML frontmatter, body ignored
4. user-xdg     $XDG_CONFIG_HOME/metacognition/config.yaml (default ~/.config/...), a whole YAML file
5. default

~/.claude wins over XDG when both set a key. Relative values resolve against the working directory
and "~" expands. A null value in a file ("key:") counts as unset.

Usage, from a skill directory:

    python3 scripts/resolve_config.py [--set key=value ...] [--extractions-root VALUE]

stdout is one JSON object: {"extractions_root": {"value", "source"}, "exemplar": {"value", "source",
"exists"}}. "value" is an absolute path or null. stderr gets one "Loaded config from: <path>" line per
config file actually read. A missing file is skipped silently. A configured exemplar that does not exist
is reported as "exists": false, never as an error.

Exit 0 on success. Exit 2 with one line on stderr for an unknown key, a wrong type (anything but a
non-empty string), an unparseable file, or a bad --set (unknown key, no "=", empty value).

src/references/settings.md documents the same tiers, keys, defaults, and tie-break for applying by hand
when this script cannot run. The two must agree; change them together.
"""

import argparse
import json
import os
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

try:
    # Imported as scripts.resolve_config (tests, from src/ on the path).
    from scripts.yaml_subset import YamlSubsetError, extract_frontmatter, parse
except ModuleNotFoundError:
    # Run as scripts/resolve_config.py inside a skill: the script directory is sys.path[0].
    from yaml_subset import (  # type: ignore[import-not-found,no-redef,unused-ignore]
        YamlSubsetError,
        extract_frontmatter,
        parse,
    )

KEYS = ("extractions_root", "exemplar")
DEFAULT_EXTRACTIONS_ROOT = "extractions"
LOCAL_MD = Path(".claude") / "metacognition.local.md"
XDG_FILE = Path("metacognition") / "config.yaml"


class ConfigError(Exception):
    """A loud configuration error; the message is the single line printed on stderr."""


@dataclass(frozen=True)
class Tier:
    """One config tier: its name and a loader returning the settings it sets."""

    name: str
    load: Callable[[], dict[str, str]]


def _validate(settings: Mapping[str, object], origin: str) -> dict[str, str]:
    """Check keys and types of parsed settings; origin names the file in any error."""
    checked: dict[str, str] = {}
    for key, value in settings.items():
        if key not in KEYS:
            raise ConfigError(f"{origin}: unknown key '{key}' (allowed: {', '.join(KEYS)})")
        if value is None:
            continue
        if not isinstance(value, str) or not value:
            raise ConfigError(f"{origin}: key '{key}' must be a non-empty string")
        checked[key] = value
    return checked


def _read_file(path: Path, frontmatter_only: bool) -> dict[str, str]:
    """Read one config file if it exists, echoing its path on stderr; {} when it is missing."""
    if not path.is_file():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
        if frontmatter_only:
            block = extract_frontmatter(text)
            parsed = parse(block) if block is not None else {}
        else:
            parsed = parse(text)
    except (OSError, ValueError, YamlSubsetError) as error:
        raise ConfigError(f"{path}: {error}") from error
    settings = _validate(parsed, str(path))
    print(f"Loaded config from: {path}", file=sys.stderr)
    return settings


def _xdg_path() -> Path:
    """Return $XDG_CONFIG_HOME/metacognition/config.yaml, or the ~/.config default."""
    xdg_home = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_home) if xdg_home else Path.home() / ".config"
    return base / XDG_FILE


def _parse_set(items: list[str]) -> dict[str, str]:
    """Turn --set key=value strings into settings; later entries override earlier ones."""
    settings: dict[str, str] = {}
    for item in items:
        key, separator, value = item.partition("=")
        if not separator:
            raise ConfigError(f"--set: expected key=value, got '{item}' (key '{key}' has no value)")
        if key not in KEYS:
            raise ConfigError(f"--set: unknown key '{key}' (allowed: {', '.join(KEYS)})")
        if not value:
            raise ConfigError(f"--set: key '{key}' must be a non-empty string")
        settings[key] = value
    return settings


def _absolute(value: str) -> str:
    """Expand "~" and resolve a relative value against the working directory."""
    return os.path.normpath(Path.cwd() / Path(value).expanduser())


def resolve(set_items: list[str]) -> dict[str, dict[str, object]]:
    """Resolve both keys across the five tiers.

    Args:
        set_items: The run-time "key=value" strings, in order.

    Returns:
        One entry per key with "value", "source", and (exemplar only) "exists".

    Raises:
        ConfigError: On any loud error, with the one-line message to print.
    """
    tiers = [
        Tier("run-time", lambda: _parse_set(set_items)),
        Tier("project", lambda: _read_file(Path.cwd() / LOCAL_MD, frontmatter_only=True)),
        Tier("user-claude", lambda: _read_file(Path.home() / LOCAL_MD, frontmatter_only=True)),
        Tier("user-xdg", lambda: _read_file(_xdg_path(), frontmatter_only=False)),
        Tier("default", lambda: {"extractions_root": DEFAULT_EXTRACTIONS_ROOT}),
    ]
    # Every tier is read, so a bad lower-tier file is an error even when a higher tier wins.
    loaded = [(tier.name, tier.load()) for tier in tiers]
    result: dict[str, dict[str, object]] = {}
    for key in KEYS:
        winner = next(((name, settings[key]) for name, settings in loaded if key in settings), None)
        entry: dict[str, object] = {"value": None, "source": "default"}
        if winner is not None:
            entry = {"value": _absolute(winner[1]), "source": winner[0]}
        if key == "exemplar":
            entry["exists"] = entry["value"] is not None and Path(str(entry["value"])).exists()
        result[key] = entry
    return result


def main(argv: list[str]) -> int:
    """Run the resolver; argv excludes the program name."""
    parser = argparse.ArgumentParser(prog="resolve_config.py", description="Resolve metacognition settings.")
    parser.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", dest="set_items")
    parser.add_argument("--extractions-root", metavar="PATH", default=None)
    namespace = parser.parse_args(argv)
    set_items: list[str] = list(namespace.set_items)
    if namespace.extractions_root is not None:
        # The alias is applied after every --set, so it wins over a --set of the same key.
        set_items.append(f"extractions_root={namespace.extractions_root}")
    try:
        result = resolve(set_items)
    except ConfigError as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
