# ABOUTME: Scans the repo's prose surfaces for writing-rule violations (dashes, curly quotes, banned vocabulary).
# Pure scan functions plus an argparse CLI wrapper so tests import the functions directly.

"""Scan prose surfaces for writing-rule violations.

Scans files for the writing rules in .claude/rules/vendored/writing.md:
em-dashes, en-dashes, curly quotes, and banned vocabulary. Three surfaces:

- ``.md``: every line. Content inside fenced code blocks is exempt from the
  banned-vocabulary check only; the codepoint checks apply everywhere.
- ``.py``: comment lines only (lstripped line starts with ``#``). String
  literals are exempt because some scripts legitimately carry em-dash
  characters as data (normalization tables, keyboard-chars fixers).
- ``.json``: the string values of ``description`` keys only, at any nesting
  depth. This covers plugin manifests and marketplace.json; other values are
  data, not prose.

Allowlisted verbatim surfaces. Some files preserve other people's words or
deliberately broken text, so the banned-vocabulary rule misfires on them. They
are exempt from that one rule; the codepoint rules (dashes, curly quotes) still
apply to them. The surfaces are the extraction data under
``tests/fixtures/extractions/``, the deliberately broken extractions under
``tests/fixtures/extractions-bad/``, the calibration round under
``tests/fixtures/calibration/``, the skillify copy (the fixture plugin) under
``tests/fixtures/plugins/``, and the vendored writing rules at
``.claude/rules/vendored/writing.md``, which list the banned words they ban.
The list is VOCABULARY_EXEMPT_GLOBS. One more file is skipped outright when a
directory scan starts at the repo root: ``tests/fixtures/prose/dirty.md``, which
is dirty on purpose (SKIPPED_PATH_GLOBS). Naming it as an argument, or scanning
its own directory, still reports it. Nothing else is allowlisted: the specs,
plans, docs, references, SKILL.md files, evals, and session notes are the
repo's own prose and are scanned.

A directory scan skips ``.git``, ``tmp``, environments, build output, caches,
and the gitignored scratch files ``goal.md`` and ``commit-msg.md`` at the root.

Exit codes: 0 when clean, 1 when findings exist.
Findings print one per line as ``path:line: rule: excerpt``.
"""

import argparse
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

from sync_skills import is_litter

REPO_ROOT = Path(__file__).resolve().parent.parent

# Source of truth: the banned-vocabulary short list in
# .claude/rules/vendored/writing.md.
# Context-dependent entries from that list (boasts as "has", landscape as an
# abstract noun, underscore as a verb) are omitted because they need human
# judgment and would fire on legitimate technical prose.
BANNED_VOCABULARY: tuple[str, ...] = (
    "delve",
    "delving",
    "dive into",
    "tapestry",
    "vibrant",
    "seamless",
    "seamlessly",
    "comprehensive",
    "robust",
    "leverage",
    "leveraged",
    "leverages",
    "leveraging",
    "unlock",
    "unleash",
    "realm",
    "holistic",
    "transformative",
    "showcase",
    "showcasing",
    "fostering",
    "bolstered",
    "crucial",
    "pivotal",
    "meticulous",
    "meticulously",
    "testament",
    "intricate",
    "interplay",
    "enduring",
)

# Directory names skipped at any depth: version control, scratch, environments, tool caches.
# Interpreter caches (__pycache__) are skipped through sync_skills.is_litter, the repo's one litter rule.
SKIPPED_DIRECTORIES: frozenset[str] = frozenset({".git", "tmp", ".venv", ".pytest_cache", ".mypy_cache", ".ruff_cache"})
# Build output, skipped only as a top-level directory of the scan root (a nested docs/site is repo prose).
SKIPPED_TOP_LEVEL_DIRECTORIES: frozenset[str] = frozenset({"site", "dist"})
# Gitignored scratch files at the scan root; they are never committed, so they are not repo prose.
SKIPPED_ROOT_FILES: frozenset[str] = frozenset({"goal.md", "commit-msg.md"})
EXCERPT_LENGTH = 80

# The vocabulary-exemption allowlist: the repo's verbatim surfaces. They are exempt from the
# banned-vocabulary rule only; codepoint rules (dashes, curly quotes) keep applying to them. Each glob
# is matched against the resolved absolute path, so a leading "**/" anchors the entry to any prefix
# (a checkout, a home directory, a test tmp dir). Add nothing else: the rest is the repo's own prose.
VOCABULARY_EXEMPT_GLOBS: tuple[str, ...] = (
    # Extraction data: verbatim interview answers, archives, compiled profiles, and calibration rounds.
    "**/tests/fixtures/extractions/**",
    # Deliberately broken extractions, kept verbatim so the validator's refusals are tested on real shapes.
    "**/tests/fixtures/extractions-bad/**",
    # The calibration round fixture, a verbatim record of a person's corrections.
    "**/tests/fixtures/calibration/**",
    # The skillify copy: the fixture plugin carries extraction content verbatim into a produced skill.
    "**/tests/fixtures/plugins/**",
    # The vendored writing rules list the banned words they ban, so the vocabulary rule misfires on them.
    "**/.claude/rules/vendored/writing.md",
)

# Files skipped outright by a directory scan, matched against the path relative to the scan root, so
# the skip only applies when the scan starts at the repo root.
SKIPPED_PATH_GLOBS: tuple[str, ...] = (
    # Dirty on purpose: the prose fixture that the gate's own tests expect to fail.
    "tests/fixtures/prose/dirty.md",
)

# Matches, in priority order: a leading "**/" (zero or more segments before a
# fixed path), a trailing "/**" (an optional "/anything" after a fixed path),
# a bare "**" (matches anything), then single-segment "*" and "?".
_GLOB_TOKEN_PATTERN = re.compile(r"\*\*/|/\*\*|\*\*|\*|\?")


def _glob_to_regex(glob: str) -> re.Pattern[str]:
    """Compile one glob pattern to an anchored regex.

    ``**`` matches zero or more full path segments, crossing ``/`` the way
    ``pathlib.PurePath.match`` cannot. ``*`` and ``?`` stay scoped to a
    single path segment, matching classic glob semantics.

    Args:
        glob: The glob pattern to compile.

    Returns:
        A compiled regex that fully matches (``^...$``) an equivalent path.
    """
    pieces: list[str] = []
    position = 0
    for token_match in _GLOB_TOKEN_PATTERN.finditer(glob):
        pieces.append(re.escape(glob[position : token_match.start()]))
        token = token_match.group()
        if token == "**/":
            pieces.append("(?:.*/)?")
        elif token == "/**":
            pieces.append("(?:/.*)?")
        elif token == "**":
            pieces.append(".*")
        elif token == "*":
            pieces.append("[^/]*")
        else:  # "?"
            pieces.append("[^/]")
        position = token_match.end()
    pieces.append(re.escape(glob[position:]))
    return re.compile(f"^{''.join(pieces)}$")


def path_matches_any_glob(path: str, globs: Sequence[str]) -> bool:
    """Report whether path matches any glob in globs.

    Args:
        path: A path string (relative or absolute) to test.
        globs: Glob patterns; see :func:`_glob_to_regex` for supported syntax.

    Returns:
        True if path matches at least one glob.
    """
    return any(_glob_to_regex(glob).match(path) for glob in globs)


class Finding(NamedTuple):
    """One writing-rule violation at a specific line."""

    path: str
    line: int
    rule: str
    excerpt: str


class Rule(NamedTuple):
    """One scan rule: name, pattern, and whether it applies inside code fences."""

    name: str
    pattern: re.Pattern[str]
    applies_in_code_fences: bool


# The findings table: adding a rule is one row here.
RULES: tuple[Rule, ...] = (
    Rule("em-dash", re.compile("—"), applies_in_code_fences=True),
    Rule("en-dash", re.compile("–"), applies_in_code_fences=True),
    Rule(
        "curly-quote",
        re.compile("[‘’“”]"),
        applies_in_code_fences=True,
    ),
    Rule(
        "banned-vocabulary",
        re.compile(r"\b(?:" + "|".join(BANNED_VOCABULARY) + r")\b", re.IGNORECASE),
        applies_in_code_fences=False,
    ),
)


def is_vocabulary_exempt(path: Path) -> bool:
    """Report whether the path is allowlisted out of the banned-vocabulary rule.

    The single source of truth is VOCABULARY_EXEMPT_GLOBS, matched against
    the resolved absolute path; codepoint rules are never exempted here.
    """
    return path_matches_any_glob(path.resolve().as_posix(), VOCABULARY_EXEMPT_GLOBS)


def scan_text(text: str, path: str = "<text>", *, skip_vocabulary: bool = False) -> list[Finding]:
    """Scan a document, returning one finding per rule per offending line."""
    findings: list[Finding] = []
    inside_code_fence = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        is_fence_marker = line.lstrip().startswith("```")
        fence_exempt = inside_code_fence or is_fence_marker
        excerpt = line.strip()[:EXCERPT_LENGTH]
        for rule in RULES:
            if fence_exempt and not rule.applies_in_code_fences:
                continue
            if skip_vocabulary and rule.name == "banned-vocabulary":
                continue
            if rule.pattern.search(line):
                findings.append(Finding(path, line_number, rule.name, excerpt))
        if is_fence_marker:
            inside_code_fence = not inside_code_fence
    return findings


def scan_python_text(text: str, path: str = "<text>") -> list[Finding]:
    """Scan only the comment lines of Python source.

    A comment line is one whose lstripped content starts with ``#``. String
    literals (including trailing-comment lines) are exempt: scripts such as
    keyboard-character fixers carry em-dash characters as data.
    """
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.lstrip().startswith("#"):
            continue
        excerpt = line.strip()[:EXCERPT_LENGTH]
        for rule in RULES:
            if rule.pattern.search(line):
                findings.append(Finding(path, line_number, rule.name, excerpt))
    return findings


# A one-line ``"description": "..."`` pair; JSON strings cannot span lines,
# so a per-line match sees every description value at any nesting depth.
DESCRIPTION_VALUE_PATTERN = re.compile(r'"description"\s*:\s*"((?:[^"\\]|\\.)*)"')


def scan_json_text(text: str, path: str = "<text>") -> list[Finding]:
    """Scan only the string values of ``description`` keys in a JSON document.

    Other keys hold data, not prose, so they are exempt.
    """
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for value_match in DESCRIPTION_VALUE_PATTERN.finditer(line):
            value = value_match.group(1)
            excerpt = value.strip()[:EXCERPT_LENGTH]
            for rule in RULES:
                if rule.pattern.search(value):
                    findings.append(Finding(path, line_number, rule.name, excerpt))
    return findings


def scan_file(path: Path) -> list[Finding]:
    """Scan one file with the scanner for its suffix, tagging findings with its path."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".py":
        return scan_python_text(text, path=str(path))
    if path.suffix == ".json":
        return scan_json_text(text, path=str(path))
    return scan_text(
        text,
        path=str(path),
        skip_vocabulary=is_vocabulary_exempt(path),
    )


SCANNED_PATTERNS: tuple[str, ...] = ("*.md", "*.py", "*.json")


def is_skipped(relative: Path) -> bool:
    """Report whether a directory scan leaves out this path, given relative to the scan root."""
    parent_parts = relative.parts[:-1]
    if any(part in SKIPPED_DIRECTORIES for part in parent_parts) or is_litter(relative):
        return True
    if parent_parts and parent_parts[0] in SKIPPED_TOP_LEVEL_DIRECTORIES:
        return True
    if not parent_parts and relative.name in SKIPPED_ROOT_FILES:
        return True
    return path_matches_any_glob(relative.as_posix(), SKIPPED_PATH_GLOBS)


def collect_files(root: Path) -> list[Path]:
    """Collect .md, .py, and .json files under root, leaving out what is_skipped names."""
    candidates = {candidate for pattern in SCANNED_PATTERNS for candidate in root.rglob(pattern)}
    return [candidate for candidate in sorted(candidates) if not is_skipped(candidate.relative_to(root))]


def scan_paths(paths: Sequence[Path]) -> list[Finding]:
    """Scan each path: a directory through collect_files, a file directly."""
    findings: list[Finding] = []
    for target_path in paths:
        if target_path.is_dir():
            for markdown_file in collect_files(target_path):
                findings.extend(scan_file(markdown_file))
        else:
            findings.extend(scan_file(target_path))
    return findings


def format_finding(finding: Finding) -> str:
    """Render a finding as ``path:line: rule: excerpt``."""
    return f"{finding.path}:{finding.line}: {finding.rule}: {finding.excerpt}"


def main(argv: Sequence[str] | None = None, repo_root: Path = REPO_ROOT) -> int:
    """Entry point: scan the given paths (default: repo_root) and report findings."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="files or directories to scan (default: the repo root)",
    )
    arguments = parser.parse_args(argv)
    target_paths: list[Path] = arguments.paths or [repo_root]

    findings = scan_paths(target_paths)
    for finding in findings:
        print(format_finding(finding))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
