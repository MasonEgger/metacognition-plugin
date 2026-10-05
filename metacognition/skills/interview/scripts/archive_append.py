# ABOUTME: Appends one entry (a probe or a battery) to a metacognition archive.md and updates every counter.
# ABOUTME: Rewrites only the questions_asked and category lines and the README interview cell, by temp file and rename.
"""Append one entry to an extraction's ``archive.md``. Standard library only, Python 3.12 or newer.

Usage, from a skill directory:

    python3 scripts/archive_append.py <extraction-dir> (--category <name> | --closing) --register <name> \\
        --probe <type> (--question <text> | --question-file <path>) (--answer <text> | --answer-file <path>) \\
        [--items <n>] [--saturated] [--ledger <line>] [--research <line>] [--export <line>]

In one run the script:

- assigns the next ``Qnn`` (one more than the last ``### Qnn`` heading, zero-padded like it);
- appends ``### Qnn [<category>] [<register>] [probe: <type>]`` and the two-line ``**Q:**`` / ``**A:**`` body
  as the last thing under ``## Questions``;
- raises ``questions_asked`` by one and the category's ``asked`` by the entry's probe count (one, or ``n``
  for a battery), rewriting only those two frontmatter lines and leaving every other byte of the
  frontmatter alone;
- rewrites the README status table's ``interview n/floor`` cell to the new probe total over the floor
  sum, changing no other cell;
- applies the one capture normalization, mapping en-dash, em-dash, and the curly single and double
  quote codepoints to their plain ASCII forms in the question and the answer, and changing nothing else
  (leading and trailing spaces and non-ASCII letters survive). A file given with ``--question-file`` or
  ``--answer-file`` is read as UTF-8 and loses one trailing line terminator, so a file that ends in a
  newline gives the same entry as the inline text.

Battery: ``--probe battery --items <n>`` (n from 3 to 6). The question is the stem on its own line followed
by n lines ``1. ...`` through ``n. ...``; the answer is n lines numbered the same way. The script counts the
numbered lines itself and refuses a mismatch with ``--items``, a stem that is itself numbered, and any other
line. The heading gains ``[items: n]`` and the body is the stem on the ``**Q:**`` line, the numbered items, a
bare ``**A:**`` line, then the numbered answers. ``--items`` with any other probe type is refused.

Closing question: ``--closing`` (instead of ``--category``) logs the entry under the ``[closing]``
pseudo-category. It raises ``questions_asked`` by one, changes no category count, and leaves the README
probe total unchanged. Giving ``--category`` or ``--saturated`` with it, or a battery, is refused.

Saturation: ``--saturated`` sets the entry's category ``saturated`` flag to true and touches no other category.

Section lines: ``--ledger``, ``--research``, and ``--export`` each append one line to ``## Contradiction
ledger``, ``## Open research``, or ``## Exports`` with the next ID (``L01``, ``R01``, ``E01``, contiguous).
The caller passes everything after the ID, starting with the parenthesized question reference, for
example ``--research "(Q73): <what was deferred>. Status: unresolved"``, ``--export "(Q92): <topic> ->
<destination skill or unassigned>"``, or ``--ledger '(Q07 vs Q23): "<claim A>" vs "<claim B>". Resolution:
<text>'``. A line must be one line and start with ``(``. A section the archive lacks is created the first
time a line is added, in the order ledger, Open research, Exports, Questions.

The assigned ``Qnn`` prints to stdout and the exit code is 0. On any problem (a missing or unreadable
``archive.md`` or ``README.md``, an archive with no parseable frontmatter or no ``## Questions`` section,
a category not in the frontmatter, a missing answer or question, a bad request) the script prints one line
naming the problem to stderr and exits 2, including an embedded line break in the question or answer of a
non-battery entry and an OSError while writing. Everything is validated and both new file contents are built
in memory before anything is written. Both are then written to temporary names in their own directory; if
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
BATTERY_PROBE = "battery"
CLOSING_CATEGORY = "closing"
BATTERY_ITEMS_RANGE = range(3, 7)

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
SATURATED_PATTERN = re.compile(r"saturated: *(?:true|false)")
INTERVIEW_CELL_PATTERN = re.compile(r"\d+/\d+")
NUMBERED_LINE_PATTERN = re.compile(r"^(\d+)\. \S")


@dataclasses.dataclass(frozen=True)
class SectionSpec:
    """One optional line-list section of the archive: its request key, heading, and line-ID prefix."""

    key: str
    heading: str
    id_prefix: str


# In archive order: each section sits before every later one and before ``## Questions``.
SECTIONS = (
    SectionSpec("ledger", "Contradiction ledger", "L"),
    SectionSpec("research", "Open research", "R"),
    SectionSpec("export", "Exports", "E"),
)


class ArchiveAppendError(Exception):
    """A request or an input the script refuses; the message is the one line printed."""


@dataclasses.dataclass(frozen=True)
class Request:
    """One parsed append request. The question and answer are text, or None when a file supplies them.

    category is None exactly when closing is true. section_lines maps a SectionSpec key to the caller's
    line (everything after the ID); items is set exactly when the probe is a battery.
    """

    directory: Path
    category: str | None
    register: str
    probe: str
    question: str | None
    question_file: Path | None
    answer: str | None
    answer_file: Path | None
    items: int | None
    closing: bool
    saturated: bool
    section_lines: dict[str, str]


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
    parser = _RequestParser(prog="archive_append.py", description="Append one archive entry.")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--category")
    parser.add_argument("--register", required=True)
    parser.add_argument("--probe", required=True)
    parser.add_argument("--question")
    parser.add_argument("--question-file", type=Path)
    parser.add_argument("--answer")
    parser.add_argument("--answer-file", type=Path)
    parser.add_argument("--items", type=int)
    parser.add_argument("--closing", action="store_true")
    parser.add_argument("--saturated", action="store_true")
    for section in SECTIONS:
        parser.add_argument(f"--{section.key}", dest=section.key)
    namespace = parser.parse_args(list(argv))
    if namespace.closing:
        if namespace.category is not None:
            raise ArchiveAppendError("--closing logs under [closing]: do not give --category with it")
        if namespace.saturated:
            raise ArchiveAppendError("--saturated names a category's flag: it cannot go with --closing")
        if namespace.probe == BATTERY_PROBE:
            raise ArchiveAppendError("--closing cannot log a battery: a closing question is a single probe")
    elif namespace.category is None:
        raise ArchiveAppendError("missing --category: give one, or --closing")
    if namespace.question is None and namespace.question_file is None:
        raise ArchiveAppendError("missing question: give --question or --question-file")
    if namespace.answer is None and namespace.answer_file is None:
        raise ArchiveAppendError("missing answer: give --answer or --answer-file")
    for field, value in (
        ("category", namespace.category),
        ("register", namespace.register),
        ("probe", namespace.probe),
    ):
        if value is not None and (not value or "]" in value or "[" in value or "\n" in value):
            raise ArchiveAppendError(f"bad {field}: {value!r} cannot appear in an entry heading")
    if namespace.probe == BATTERY_PROBE:
        if namespace.items is None:
            raise ArchiveAppendError("a battery needs --items n (3 to 6)")
        if namespace.items not in BATTERY_ITEMS_RANGE:
            raise ArchiveAppendError(f"--items {namespace.items} is outside 3 to 6")
    elif namespace.items is not None:
        raise ArchiveAppendError(f"--items goes only with --probe battery, not --probe {namespace.probe}")
    section_lines: dict[str, str] = {}
    for section in SECTIONS:
        line: str | None = getattr(namespace, section.key)
        if line is None:
            continue
        if "\n" in line or "\r" in line or not line.startswith("("):
            raise ArchiveAppendError(
                f"bad --{section.key} line: give one line starting with the parenthesized question reference"
            )
        section_lines[section.key] = line
    return Request(
        directory=namespace.directory,
        category=namespace.category,
        register=namespace.register,
        probe=namespace.probe,
        question=namespace.question,
        question_file=namespace.question_file,
        answer=namespace.answer,
        answer_file=namespace.answer_file,
        items=namespace.items,
        closing=namespace.closing,
        saturated=namespace.saturated,
        section_lines=section_lines,
    )


def _with_line_ending(original: str, replacement: str) -> str:
    """Return replacement carrying original's line terminator, so the rewrite keeps the file's endings."""
    stripped = original.rstrip("\r\n")
    return replacement + original[len(stripped) :]


def _rewrite_frontmatter_lines(lines: list[str], request: Request, new_total: int, new_asked: int | None) -> None:
    """Rewrite the questions_asked line and, unless new_asked is None, the request category's line in place."""
    asked_index = next((index for index, line in enumerate(lines) if line.startswith("questions_asked:")), None)
    categories_index = next((index for index, line in enumerate(lines) if line.startswith("categories:")), None)
    if asked_index is None or categories_index is None:
        raise ArchiveAppendError("archive.md frontmatter has no questions_asked or categories line")
    lines[asked_index] = _with_line_ending(lines[asked_index], f"questions_asked: {new_total}")
    if new_asked is None:
        return
    prefix = f"{request.category}:"
    for index in range(categories_index + 1, len(lines)):
        if lines[index].strip().startswith(prefix) and lines[index][:1].isspace():
            rewritten = ASKED_PATTERN.sub(f"asked: {new_asked}", lines[index], count=1)
            if request.saturated:
                rewritten = SATURATED_PATTERN.sub("saturated: true", rewritten, count=1)
            lines[index] = rewritten
            return
    raise ArchiveAppendError(f"category {request.category!r} has no line under categories in archive.md")


def _battery_lines(text: str, description: str, items: int, *, skip_stem: bool) -> tuple[str, list[str]]:
    """Split a battery's text into its stem (empty for an answer) and its numbered lines without the numbers.

    Raises:
        ArchiveAppendError: When a line is not numbered, the numbers are not 1 to items, or the count differs.
    """
    lines = text.splitlines()
    stem = ""
    if skip_stem:
        stem, lines = lines[0], lines[1:]
        if NUMBERED_LINE_PATTERN.match(stem):
            raise ArchiveAppendError("battery question needs a stem line before its numbered items")
    numbers: list[int] = []
    contents: list[str] = []
    for line in lines:
        match = NUMBERED_LINE_PATTERN.match(line)
        if match is None:
            raise ArchiveAppendError(f"battery {description} has a line that is not a numbered item: {line[:30]!r}")
        numbers.append(int(match.group(1)))
        contents.append(line)
    if numbers != list(range(1, items + 1)):
        raise ArchiveAppendError(f"battery {description} has numbered lines {numbers}, not 1 to {items} for --items")
    return stem, contents


def _entry_text(request: Request, label: str, question: str, answer: str) -> str:
    """Return the heading and body of the new entry, normalized, with the shape its probe type needs."""
    category = CLOSING_CATEGORY if request.category is None else request.category
    heading = f"### {label} [{category}] [{request.register}] [probe: {request.probe}]"
    if request.items is None:
        _require_one_line(question, "question")
        _require_one_line(answer, "answer")
        return f"{heading}\n**Q:** {normalize(question)}\n**A:** {normalize(answer)}\n"
    stem, items = _battery_lines(normalize(question), "question", request.items, skip_stem=True)
    _, answers = _battery_lines(normalize(answer), "answer", request.items, skip_stem=False)
    return (
        f"{heading} [items: {request.items}]\n**Q:** {stem}\n"
        + "\n".join(items)
        + "\n**A:**\n"
        + "\n".join(answers)
        + "\n"
    )


def _add_section_line(body: str, section: SectionSpec, line: str, later_headings: Sequence[str]) -> str:
    """Return body with one line, carrying the next ID, added to section; create the section if it is absent.

    A new section goes just before the first of later_headings that exists in body.
    """
    heading = re.search(rf"^## {re.escape(section.heading)}[ \t]*$", body, re.MULTILINE)
    if heading is None:
        for later in later_headings:
            match = re.search(rf"^## {re.escape(later)}[ \t]*$", body, re.MULTILINE)
            if match is not None:
                new_section = f"## {section.heading}\n\n- {section.id_prefix}01 {line}\n\n"
                return body[: match.start()] + new_section + body[match.start() :]
        raise ArchiveAppendError("archive.md has no '## Questions' section")
    following = SECTION_PATTERN.search(body, heading.end())
    section_end = following.start() if following else len(body)
    numbers = [
        int(number)
        for number in re.findall(rf"^- {section.id_prefix}(\d+)\b", body[heading.end() : section_end], re.MULTILINE)
    ]
    identifier = f"{section.id_prefix}{(max(numbers) if numbers else 0) + 1:02d}"
    before = body[:section_end].rstrip("\n")
    after = body[section_end:]
    return f"{before}\n- {identifier} {line}\n" + (f"\n{after}" if after else "")


def compute_new_archive(archive_text: str, request: Request, question: str, answer: str) -> NewArchive:
    """Return the archive text with the entry appended, the counters raised, and section lines added.

    Touches no file.

    Raises:
        ArchiveAppendError: On unparseable frontmatter, an unknown category, a malformed battery, or no
            ``## Questions`` section.
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
    if request.category is not None and request.category not in categories:
        raise ArchiveAppendError(f"category {request.category!r} is not in the archive.md frontmatter")
    counts: dict[str, tuple[int, int]] = {}
    for name, entry in categories.items():
        asked = entry.get("asked") if isinstance(entry, dict) else None
        floor = entry.get("floor") if isinstance(entry, dict) else None
        if not isinstance(asked, int) or not isinstance(floor, int):
            raise ArchiveAppendError("archive.md frontmatter categories need integer asked and floor counts")
        counts[name] = (asked, floor)
    probe_count = 0 if request.category is None else (request.items or 1)
    asked_total = sum(asked for asked, _ in counts.values()) + probe_count
    floor_total = sum(floor for _, floor in counts.values())
    new_category_asked = None if request.category is None else counts[request.category][0] + probe_count

    lines = archive_text.splitlines(keepends=True)
    closing_index = next(index for index in range(1, len(lines)) if lines[index].rstrip() == "---")
    frontmatter_lines = lines[1:closing_index]
    _rewrite_frontmatter_lines(frontmatter_lines, request, total + 1, new_category_asked)
    head = "".join([lines[0], *frontmatter_lines, lines[closing_index]])
    body = "".join(lines[closing_index + 1 :])

    for position, section in enumerate(SECTIONS):
        if section.key in request.section_lines:
            later = [later_section.heading for later_section in SECTIONS[position + 1 :]] + ["Questions"]
            body = _add_section_line(body, section, request.section_lines[section.key], later)

    questions = QUESTIONS_HEADING_PATTERN.search(body)
    if questions is None:
        raise ArchiveAppendError("archive.md has no '## Questions' section")
    following = SECTION_PATTERN.search(body, questions.end())
    section_end = following.start() if following else len(body)
    numbers = HEADING_NUMBER_PATTERN.findall(body[questions.end() : section_end])
    width = max(MIN_NUMBER_WIDTH, len(numbers[-1])) if numbers else MIN_NUMBER_WIDTH
    label = f"Q{(int(numbers[-1]) if numbers else 0) + 1:0{width}d}"
    entry = _entry_text(request, label, question, answer)
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
        raise ArchiveAppendError(f"{description} has a line break: a non-battery entry needs a one-line {description}")


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
