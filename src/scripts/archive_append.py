# ABOUTME: Appends one single-probe entry to a metacognition extraction's archive.md and updates every counter.
# ABOUTME: Rewrites only the questions_asked and category lines and the README interview cell, by temp file and rename.
"""Append one entry to an extraction's ``archive.md``. Standard library only, Python 3.12 or newer.

Usage, from a skill directory:

    python3 scripts/archive_append.py <extraction-dir> --category <name> --register <name> --probe <type> \\
        (--question <text> | --question-file <path>) (--answer <text> | --answer-file <path>)

In one run the script:

- assigns the next ``Qnn`` (one more than the last ``### Qnn`` heading, zero-padded like it);
- appends ``### Qnn [<category>] [<register>] [probe: <type>]`` and the two-line ``**Q:**`` / ``**A:**`` body
  as the last thing under ``## Questions``;
- raises ``questions_asked`` by one and the category's ``asked`` by one, rewriting only those two
  frontmatter lines and leaving every other byte of the frontmatter alone;
- rewrites the README status table's ``interview n/floor`` cell to the new probe total over the floor
  sum, changing no other cell;
- applies the one capture normalization, mapping en-dash, em-dash, and the curly single and double
  quote codepoints to their plain ASCII forms in the question and the answer, and changing nothing else
  (leading and trailing spaces and non-ASCII letters survive). A file given with ``--question-file`` or
  ``--answer-file`` is read as UTF-8 and loses one trailing line terminator, so a file that ends in a
  newline gives the same entry as the inline text.

This version handles single entries only. ``--probe battery`` is refused.

The assigned ``Qnn`` prints to stdout and the exit code is 0. On any problem (a missing or unreadable
``archive.md`` or ``README.md``, an archive with no parseable frontmatter or no ``## Questions`` section,
a category not in the frontmatter, a missing answer or question, a bad request) the script prints one line
naming the problem to stderr and exits 2, including an embedded line break in the question or answer of a
single entry and an OSError while writing. Everything is validated and both new file contents are built in
memory before anything is written. Both are then written to temporary names in their own directory; if
either temporary write fails, both originals are untouched and no temporary file remains. Only then are the
two renames made, archive first. A failure between the renames (not expected on a normal filesystem) would
leave the archive one entry ahead of the README cell; the next successful append corrects the cell, because
it is recomputed from the archive's per-category counts, not incremented.
"""

import argparse
import dataclasses
import os
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

try:
    # Imported as scripts.archive_append (tests, from src/ on the path).
    from scripts.yaml_subset import YamlSubsetError, extract_frontmatter, parse
except ModuleNotFoundError:
    # Run as scripts/archive_append.py inside a skill: the script directory is sys.path[0].
    from yaml_subset import (  # type: ignore[import-not-found,no-redef,unused-ignore]
        YamlSubsetError,
        extract_frontmatter,
        parse,
    )

EXIT_ERROR = 2
MIN_NUMBER_WIDTH = 2
README_CELL_INDEX = 2
README_MIN_PARTS = 7

NORMALIZATION = str.maketrans(
    {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
)
HEADING_NUMBER_PATTERN = re.compile(r"^### Q(\d+)", re.MULTILINE)
SECTION_PATTERN = re.compile(r"^## ", re.MULTILINE)
QUESTIONS_HEADING_PATTERN = re.compile(r"^## Questions[ \t]*$", re.MULTILINE)
ASKED_PATTERN = re.compile(r"asked: *\d+")
INTERVIEW_CELL_PATTERN = re.compile(r"\d+/\d+")


class ArchiveAppendError(Exception):
    """A request or an input the script refuses; the message is the one line printed."""


@dataclasses.dataclass(frozen=True)
class Request:
    """One parsed append request. The question and answer are text, or None when a file supplies them."""

    directory: Path
    category: str
    register: str
    probe: str
    question: str | None
    question_file: Path | None
    answer: str | None
    answer_file: Path | None


@dataclasses.dataclass(frozen=True)
class NewArchive:
    """The rewritten archive text, the assigned question label, and the totals the README cell needs."""

    text: str
    label: str
    probe_total: int
    floor_total: int


class _RequestParser(argparse.ArgumentParser):
    """An argument parser whose usage errors become ArchiveAppendError, so main owns exit code 2."""

    def error(self, message: str) -> NoReturn:
        raise ArchiveAppendError(f"bad request: {message}")


def normalize(text: str) -> str:
    """Map dash and curly-quote codepoints to plain ASCII and change nothing else."""
    return text.translate(NORMALIZATION)


def parse_request(argv: Sequence[str]) -> Request:
    """Turn command-line arguments into a Request, refusing a malformed one. Touches no file."""
    parser = _RequestParser(prog="archive_append.py", description="Append one single-probe archive entry.")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--category", required=True)
    parser.add_argument("--register", required=True)
    parser.add_argument("--probe", required=True)
    parser.add_argument("--question")
    parser.add_argument("--question-file", type=Path)
    parser.add_argument("--answer")
    parser.add_argument("--answer-file", type=Path)
    namespace = parser.parse_args(list(argv))
    if namespace.question is None and namespace.question_file is None:
        raise ArchiveAppendError("missing question: give --question or --question-file")
    if namespace.answer is None and namespace.answer_file is None:
        raise ArchiveAppendError("missing answer: give --answer or --answer-file")
    for field, value in (
        ("category", namespace.category),
        ("register", namespace.register),
        ("probe", namespace.probe),
    ):
        if not value or "]" in value or "[" in value or "\n" in value:
            raise ArchiveAppendError(f"bad {field}: {value!r} cannot appear in an entry heading")
    if namespace.probe == "battery":
        raise ArchiveAppendError("battery entries are not supported yet: only single probes can be appended")
    return Request(
        directory=namespace.directory,
        category=namespace.category,
        register=namespace.register,
        probe=namespace.probe,
        question=namespace.question,
        question_file=namespace.question_file,
        answer=namespace.answer,
        answer_file=namespace.answer_file,
    )


def _with_line_ending(original: str, replacement: str) -> str:
    """Return replacement carrying original's line terminator, so the rewrite keeps the file's endings."""
    stripped = original.rstrip("\r\n")
    return replacement + original[len(stripped) :]


def _rewrite_frontmatter_lines(lines: list[str], request: Request, new_total: int, new_asked: int) -> None:
    """Rewrite the questions_asked line and the request category's line in place, in a frontmatter line list."""
    asked_index = next((index for index, line in enumerate(lines) if line.startswith("questions_asked:")), None)
    categories_index = next((index for index, line in enumerate(lines) if line.startswith("categories:")), None)
    if asked_index is None or categories_index is None:
        raise ArchiveAppendError("archive.md frontmatter has no questions_asked or categories line")
    lines[asked_index] = _with_line_ending(lines[asked_index], f"questions_asked: {new_total}")
    prefix = f"{request.category}:"
    for index in range(categories_index + 1, len(lines)):
        if lines[index].strip().startswith(prefix) and lines[index][:1].isspace():
            lines[index] = ASKED_PATTERN.sub(f"asked: {new_asked}", lines[index], count=1)
            return
    raise ArchiveAppendError(f"category {request.category!r} has no line under categories in archive.md")


def compute_new_archive(archive_text: str, request: Request, question: str, answer: str) -> NewArchive:
    """Return the archive text with the entry appended and the counters raised. Touches no file.

    Raises:
        ArchiveAppendError: On unparseable frontmatter, an unknown category, or no ``## Questions`` section.
    """
    frontmatter = extract_frontmatter(archive_text)
    if frontmatter is None:
        raise ArchiveAppendError("archive.md has no complete frontmatter block")
    try:
        data = parse(frontmatter)
    except YamlSubsetError as error:
        raise ArchiveAppendError(f"archive.md frontmatter does not parse: {error}") from error
    categories = data.get("categories")
    total = data.get("questions_asked")
    if not isinstance(categories, dict) or not isinstance(total, int) or isinstance(total, bool):
        raise ArchiveAppendError("archive.md frontmatter needs a categories map and an integer questions_asked")
    if request.category not in categories:
        raise ArchiveAppendError(f"category {request.category!r} is not in the archive.md frontmatter")
    counts: dict[str, tuple[int, int]] = {}
    for name, entry in categories.items():
        asked = entry.get("asked") if isinstance(entry, dict) else None
        floor = entry.get("floor") if isinstance(entry, dict) else None
        if not isinstance(asked, int) or not isinstance(floor, int):
            raise ArchiveAppendError("archive.md frontmatter categories need integer asked and floor counts")
        counts[name] = (asked, floor)
    asked_total = sum(asked for asked, _ in counts.values()) + 1
    floor_total = sum(floor for _, floor in counts.values())
    category_asked = counts[request.category][0]

    lines = archive_text.splitlines(keepends=True)
    closing_index = next(index for index in range(1, len(lines)) if lines[index].rstrip() == "---")
    frontmatter_lines = lines[1:closing_index]
    _rewrite_frontmatter_lines(frontmatter_lines, request, total + 1, category_asked + 1)
    head = "".join([lines[0], *frontmatter_lines, lines[closing_index]])
    body = "".join(lines[closing_index + 1 :])

    questions = QUESTIONS_HEADING_PATTERN.search(body)
    if questions is None:
        raise ArchiveAppendError("archive.md has no '## Questions' section")
    following = SECTION_PATTERN.search(body, questions.end())
    section_end = following.start() if following else len(body)
    numbers = HEADING_NUMBER_PATTERN.findall(body[questions.end() : section_end])
    width = max(MIN_NUMBER_WIDTH, len(numbers[-1])) if numbers else MIN_NUMBER_WIDTH
    label = f"Q{(int(numbers[-1]) if numbers else 0) + 1:0{width}d}"
    entry = (
        f"### {label} [{request.category}] [{request.register}] [probe: {request.probe}]\n"
        f"**Q:** {normalize(question)}\n**A:** {normalize(answer)}\n"
    )
    before = body[:section_end].rstrip("\n")
    after = body[section_end:]
    new_body = f"{before}\n\n{entry}" + (f"\n{after}" if after else "")
    return NewArchive(head + new_body, label, asked_total, floor_total)


def compute_new_readme(readme_text: str, probe_total: int, floor_total: int) -> str:
    """Return the README text with the status table's interview cell set to probe_total/floor_total.

    Raises:
        ArchiveAppendError: When the README has no status table data row.
    """
    lines = readme_text.splitlines(keepends=True)
    separator_index = next(
        (index for index, line in enumerate(lines) if line.startswith("|---") or line.startswith("| ---")), None
    )
    if separator_index is None or separator_index + 1 >= len(lines):
        raise ArchiveAppendError("README.md has no status table row")
    row = lines[separator_index + 1]
    parts = row.rstrip("\r\n").split("|")
    if len(parts) < README_MIN_PARTS:
        raise ArchiveAppendError("README.md status table row has too few cells")
    value = f"{probe_total}/{floor_total}"
    cell = parts[README_CELL_INDEX]
    parts[README_CELL_INDEX] = (
        INTERVIEW_CELL_PATTERN.sub(value, cell, count=1) if INTERVIEW_CELL_PATTERN.search(cell) else f" {value} "
    )
    lines[separator_index + 1] = _with_line_ending(row, "|".join(parts))
    return "".join(lines)


def _read_text(path: Path, description: str) -> str:
    """Read a UTF-8 file with its bytes intact, or raise ArchiveAppendError naming it."""
    try:
        return path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ArchiveAppendError(f"cannot read {description} {path.name}: {error.__class__.__name__}") from error


def _text_from(inline: str | None, path: Path | None, description: str) -> str:
    """Return inline text, or the named file's text without one trailing line terminator."""
    if inline is not None:
        text = inline
    else:
        assert path is not None
        text = _read_text(path, description)
        text = text.removesuffix("\n").removesuffix("\r")
    if text == "":
        raise ArchiveAppendError(f"empty {description}")
    return text


def _require_one_line(text: str, description: str) -> None:
    """Refuse text with an embedded line break, which would break a two-line entry body."""
    if "\n" in text or "\r" in text:
        raise ArchiveAppendError(f"{description} has a line break: a single entry needs a one-line {description}")


def _write_temporary(path: Path, text: str) -> Path:
    """Write text completely to a temporary name beside path and return that name."""
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(text.encode("utf-8"))
    return temporary


def apply_request(request: Request) -> str:
    """Read the inputs, build both new files in memory, then write archive.md and README.md.

    This is the only function that touches the disk. It returns the assigned question label.
    """
    archive_path = request.directory / "archive.md"
    readme_path = request.directory / "README.md"
    archive_text = _read_text(archive_path, "archive")
    readme_text = _read_text(readme_path, "README")
    question = _text_from(request.question, request.question_file, "question")
    answer = _text_from(request.answer, request.answer_file, "answer")
    if request.probe != "battery":
        _require_one_line(question, "question")
        _require_one_line(answer, "answer")
    new_archive = compute_new_archive(archive_text, request, question, answer)
    new_readme = compute_new_readme(readme_text, new_archive.probe_total, new_archive.floor_total)
    temporaries: list[Path] = []
    failing = archive_path
    try:
        for path, text in ((archive_path, new_archive.text), (readme_path, new_readme)):
            failing = path
            temporaries.append(path.with_name(f".{path.name}.tmp"))
            _write_temporary(path, text)
        failing = archive_path
        os.replace(temporaries[0], archive_path)
        failing = readme_path
        os.replace(temporaries[1], readme_path)
    except OSError as error:
        raise ArchiveAppendError(f"cannot write {failing.name}: {error.__class__.__name__}") from error
    finally:
        for temporary in temporaries:
            temporary.unlink(missing_ok=True)
    return new_archive.label


def main(argv: Sequence[str]) -> int:
    """Run the append and return the exit code: 0 on success, 2 on any refused request."""
    try:
        label = apply_request(parse_request(argv))
    except ArchiveAppendError as error:
        print(f"archive_append: {error}", file=sys.stderr)
        return EXIT_ERROR
    print(label)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
