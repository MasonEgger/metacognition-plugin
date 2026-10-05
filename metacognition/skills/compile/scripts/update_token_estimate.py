# ABOUTME: Recomputes a profile's token_estimate and rewrites that one frontmatter line when stale.
# ABOUTME: Shares the validator's estimate function, so a rewritten profile never trips the mismatch check.
"""Keep a profile's ``token_estimate`` frontmatter line equal to the validator's recount. Standard library only.

Usage, from a skill directory:

    python3 scripts/update_token_estimate.py [-c | --check] <profile.md> [<profile.md> ...]

The estimate is the validator's own number (``validate_artifacts.estimate_tokens``): everything after
the closing frontmatter delimiter, counted in characters and divided by four.

Default mode rewrites a stale ``token_estimate`` line in place and reports the old and new values; a
current profile is reported as current and left byte-identical. With ``--check`` (or ``-c``) a stale
profile is reported and nothing is written. Each path is handled independently.

Exit codes:

- 0: every profile is current or was updated.
- 1: ``--check`` found a stale profile.
- 2: a path is missing or malformed (no closing delimiter, or no ``token_estimate``
  line); one line on stderr names the file and the problem. Exit 2 outranks exit 1.

Only the ``token_estimate`` line inside the frontmatter is ever changed. The frontmatter is found by
the validator's own split (after universal newlines) and a line prefix, with no YAML round trip, so
every other byte of the file is kept, CRLF endings and a byte-order mark included.
A body line that begins with ``token_estimate:`` is never touched.
"""

import argparse
import io
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

try:
    # Imported as scripts.update_token_estimate (tests, from src/ on the path).
    from scripts.validate_artifacts import FRONTMATTER_DELIMITER, estimate_tokens, split_frontmatter
except ModuleNotFoundError:
    # Run as scripts/update_token_estimate.py inside a skill: the script directory is sys.path[0].
    from validate_artifacts import (  # type: ignore[import-not-found,no-redef,unused-ignore]
        FRONTMATTER_DELIMITER,
        estimate_tokens,
        split_frontmatter,
    )

EXIT_STALE = 1
EXIT_ERROR = 2
ESTIMATE_PREFIX = "token_estimate:"


class ProfileError(Exception):
    """A profile that cannot be read, is malformed, or cannot be written."""


class Recount(NamedTuple):
    """The result of recounting one profile's text."""

    text: str
    old: str
    new: int


def recount(raw: str) -> Recount:
    """Return the profile text with its token_estimate line corrected, plus the old and new values.

    Pure: nothing is read or written. The count and the frontmatter split are the validator's: the
    text is put through universal newlines (CRLF and lone CR become LF, exactly as ``Path.read_text``
    does) and split by ``split_frontmatter``. The edit is made on ``raw`` itself, so every other byte,
    including line endings and a byte-order mark, is kept. ``raw`` is returned unchanged when the
    stored value already equals the new one.

    Args:
        raw: The full profile file contents, decoded but with newlines untouched.

    Returns:
        The new text, the stored value as written, and the recomputed estimate.

    Raises:
        ProfileError: When there is no closing delimiter or no token_estimate line.
    """
    raw_lines = list(io.StringIO(raw, newline=""))
    text = "".join(line.rstrip("\r\n") + ("\n" if line.endswith(("\r", "\n")) else "") for line in raw_lines)
    parts = split_frontmatter(text)
    if parts is None:
        raise ProfileError("no closing frontmatter delimiter")
    preamble, frontmatter, body = parts
    new = estimate_tokens(body)
    # The frontmatter begins on the line after the opening delimiter; its last piece is the partial
    # line that holds the closing delimiter, so only the complete lines before it are candidates.
    first_line = text.count("\n", 0, len(preamble) + len(FRONTMATTER_DELIMITER))
    for line_index in range(first_line, first_line + frontmatter.count("\n")):
        raw_line = raw_lines[line_index]
        content = raw_line.rstrip("\r\n")
        if not content.startswith(ESTIMATE_PREFIX):
            continue
        old = content.removeprefix(ESTIMATE_PREFIX).strip()
        if old == str(new):
            return Recount(raw, old, new)
        raw_lines[line_index] = f"{ESTIMATE_PREFIX} {new}{raw_line[len(content) :]}"
        return Recount("".join(raw_lines), old, new)
    raise ProfileError("no token_estimate line in the frontmatter")


def process(path: Path, *, check: bool) -> tuple[str, bool]:
    """Recount one profile, writing the fix unless ``check``. This is the only function that touches the disk.

    Args:
        path: The profile.md to handle.
        check: When true, write nothing.

    Returns:
        A report line and whether the profile was stale.

    Raises:
        ProfileError: On a missing, unreadable, malformed, or unwritable profile.
    """
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ProfileError(f"cannot read: {error.__class__.__name__}") from error
    result = recount(text)
    if result.text == text:
        return f"{path}: current ({result.new})", False
    if check:
        return f"{path}: stale (stored {result.old}, recount {result.new})", True
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_bytes(result.text.encode("utf-8"))
        os.replace(temporary, path)
    except OSError as error:
        raise ProfileError(f"cannot write: {error.__class__.__name__}") from error
    finally:
        temporary.unlink(missing_ok=True)
    return f"{path}: updated {result.old} -> {result.new}", True


def main(argv: Sequence[str]) -> int:
    """Run the script and return the exit code: 0 clean, 1 stale under --check, 2 on any bad path."""
    parser = argparse.ArgumentParser(description="Recompute a profile's token_estimate frontmatter line.")
    parser.add_argument("-c", "--check", action="store_true", help="report stale profiles and write nothing")
    parser.add_argument("paths", nargs="+", type=Path, help="profile.md files")
    arguments = parser.parse_args(argv)
    exit_code = 0
    for path in arguments.paths:
        try:
            report, stale = process(path, check=arguments.check)
        except ProfileError as error:
            print(f"{path}: {error}", file=sys.stderr)
            exit_code = EXIT_ERROR
            continue
        print(report)
        if stale and arguments.check and exit_code == 0:
            exit_code = EXIT_STALE
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
