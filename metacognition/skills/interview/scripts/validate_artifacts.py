# ABOUTME: Structural validator for one metacognition extraction directory.
# ABOUTME: Parses frontmatter and checks archive, profile, and calibration shape; never touches prose.
"""Validate the structure of a metacognition extraction directory. Standard library only.

Given an extraction directory (``extractions/<domain-slug>/``), this script runs the checks below
and exits 1 with a findings list when any fail (exit 0 when clean):

- **frontmatter-parse**: every ``interview-spec.md``, ``archive.md``, ``profile.md``, and
  ``calibration/round-NN.md`` frontmatter block parses (via the sibling ``yaml_subset`` module)
  into a mapping. A missing closing delimiter, a syntax error, or a non-mapping result all fail here.
- **archive-question-numbering**: the archive's ``### Qnn`` headings are globally contiguous,
  starting at 1, with no gap and no repeat.
- **archive-category-count**: each category's frontmatter ``asked`` count matches the probes the body
  holds for that category. Each ``### Qnn [<category>]`` heading counts one probe, except a battery,
  which counts the number in its ``[items: n]`` tag. A ``[closing]`` entry touches no category.
- **archive-battery-items**: a ``[probe: battery]`` heading carries ``[items: n]`` with n from 3 to 6,
  and its body holds exactly n numbered items under ``**Q:**`` and n numbered answers under
  ``**A:**``. An ``[items: n]`` tag on any other probe type also fails here.
- **archive-section-ids**: when the optional ``## Open research`` or ``## Exports`` section is
  present, its line IDs (``R01``, ``E01``) run contiguously from 1 with no gap and no repeat; the
  message names the section. Neither section is ever required.
- **profile-token-ceiling**: the profile body (everything after the closing frontmatter delimiter
  through end of file), recomputed as characters divided by four, does not exceed the token ceiling.
  The ceiling is 10,000 at any register count.
- **profile-token-estimate-mismatch**: the frontmatter's stored ``token_estimate`` matches that same
  recompute, flagged even when the profile is comfortably under the ceiling.
- **profile-missing-section**: every required top-level XML section from the profile format
  reference is present.
- **profile-section-order**: the sections that are present appear in the format's fixed order.
- **golden-example-incomplete**: every ``<example>`` in ``golden_examples`` carries all three of
  ``<bad>``, ``<good>``, and ``<why>``.
- **calibration-round-contiguity**: ``calibration/round-NN.md`` files are globally contiguous,
  starting at 1, with no gap and no repeat.

Two checks guard the extraction directory itself, before any artifact is parsed:

- **extraction-dir-missing**: the given path does not exist at all.
- **extraction-dir-empty**: the path exists but holds none of the four artifact files
  (``interview-spec.md``, ``archive.md``, ``profile.md``, a ``calibration/`` directory).
  A directory failing either check returns immediately with that one finding.

Boundary: this script owns structure only. It never checks codepoints (dashes, curly quotes) or
vocabulary; prose checks live in a separate script. A profile or archive can pass every check here
and still fail the prose gate, and the reverse.

Usage, from a skill directory:

    python3 scripts/validate_artifacts.py <extraction-dir>

Findings print to stdout as ``<path>: <check>: <message>``. Exit 0 when clean, 1 on any finding.
"""

import argparse
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

try:
    # Imported as scripts.validate_artifacts (tests, from src/ on the path).
    from scripts.yaml_subset import YamlSubsetError, parse
except ModuleNotFoundError:
    # Run as scripts/validate_artifacts.py inside a skill: the script directory is sys.path[0].
    from yaml_subset import (  # type: ignore[import-not-found,no-redef,unused-ignore]
        YamlSubsetError,
        parse,
    )

TOKEN_CEILING = 10000
FRONTMATTER_DELIMITER = "---\n"

# The profile.md section order, sourced from the profile format's "Section
# Reference": the single constant every section-presence and section-order
# check reads from, so the two files can never drift apart silently.
REQUIRED_PROFILE_SECTIONS: tuple[str, ...] = (
    "usage",
    "priority",
    "identity_context",
    "judgment_fingerprint",
    "domain_laws",
    "communication_laws",
    "hard_refusals",
    "taste_loves",
    "taste_disgusts",
    "phrase_bank",
    "signature_tells",
    "decision_rules",
    "productive_contradictions",
    "golden_examples",
    "do_not_infer",
    "calibration_state",
    "final_instruction",
)

REQUIRED_EXAMPLE_CHILDREN: tuple[str, ...] = ("bad", "good", "why")

QUESTION_HEADING_PATTERN = re.compile(
    r"^### Q(?P<number>\d+) \[(?P<category>[^\]]+)\]"
    r"(?: \[(?P<register>(?!probe: |items: )[^\]]+)\])?"
    r"(?: \[probe: (?P<probe>[^\]]+)\])?"
    r"(?: \[items: (?P<items>\d+)\])?[^\n]*$",
    re.MULTILINE,
)
NEXT_BLOCK_PATTERN = re.compile(r"^#{2,3} ", re.MULTILINE)
NUMBERED_LINE_PATTERN = re.compile(r"^(\d+)\. ", re.MULTILINE)
OPTIONAL_SECTIONS: tuple[tuple[str, str], ...] = (("Open research", "R"), ("Exports", "E"))
BATTERY_ITEMS_RANGE = range(3, 7)
CLOSING_CATEGORY = "closing"
SECTION_TAG_PATTERN = re.compile(r"<([a-z_]+)>", re.MULTILINE)
EXAMPLE_BLOCK_PATTERN = re.compile(r"<example>(.*?)</example>", re.DOTALL)
ROUND_FILENAME_PATTERN = re.compile(r"round-(\d+)\.md$")


class Finding(NamedTuple):
    """One structural violation: which check failed, which file, and why."""

    check: str
    path: str
    message: str


def parse_frontmatter(path: Path) -> tuple[dict[str, object] | None, str, list[Finding]]:
    """Split a Markdown artifact into its YAML frontmatter and body.

    Args:
        path: The artifact file to parse.

    Returns:
        A tuple of (frontmatter, body, findings). frontmatter is None and one
        "frontmatter-parse" finding is returned when the closing delimiter is
        missing, the YAML fails to parse, or the parsed value is not a
        mapping. body is the text after the closing delimiter through end of
        file whenever the delimiters were found (even if the YAML itself was
        invalid), because the profile token-estimate recompute needs that
        exact slice regardless of frontmatter validity; it is empty only when
        the closing delimiter itself could not be found.
    """
    text = path.read_text(encoding="utf-8")
    parts = text.split(FRONTMATTER_DELIMITER, 2)
    if len(parts) < 3:
        return (
            None,
            "",
            [Finding("frontmatter-parse", str(path), "no closing frontmatter delimiter found")],
        )
    _, frontmatter_text, body = parts
    try:
        frontmatter: dict[str, object] | None = dict(parse(frontmatter_text)) if frontmatter_text.strip() else None
    except YamlSubsetError as error:
        return None, body, [Finding("frontmatter-parse", str(path), f"YAML failed to parse: {error}")]
    if not isinstance(frontmatter, dict):
        return (
            None,
            body,
            [Finding("frontmatter-parse", str(path), "frontmatter did not parse to a mapping")],
        )
    return frontmatter, body, []


class QuestionEntry(NamedTuple):
    """One parsed ``### Qnn`` heading and the body text that follows it."""

    number: int
    category: str
    register: str | None
    probe: str | None
    items: int | None
    body: str


def parse_question_entries(body: str) -> list[QuestionEntry]:
    """Turn every ``### Qnn ...`` heading in the archive body into a QuestionEntry, in order.

    The entry text runs from the end of its heading to the next ``##`` or ``###`` heading.
    """
    entries: list[QuestionEntry] = []
    for match in QUESTION_HEADING_PATTERN.finditer(body):
        next_block = NEXT_BLOCK_PATTERN.search(body, match.end())
        entry_text = body[match.end() : next_block.start() if next_block else len(body)]
        items = match.group("items")
        entries.append(
            QuestionEntry(
                int(match.group("number")),
                match.group("category"),
                match.group("register"),
                match.group("probe"),
                int(items) if items is not None else None,
                entry_text,
            )
        )
    return entries


def probe_count(entry: QuestionEntry) -> int:
    """Return how many probes an entry counts toward its category: a battery's items, else one."""
    if entry.probe == "battery":
        return entry.items or 0
    return 1


def check_archive_question_numbering(path: Path, body: str) -> list[Finding]:
    """Flag a gap or repeat in the archive's global ``Qnn`` numbering."""
    numbers = [entry.number for entry in parse_question_entries(body)]
    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        return [
            Finding(
                "archive-question-numbering",
                str(path),
                f"question numbers {numbers} are not contiguous from 1 (expected {expected})",
            )
        ]
    return []


def check_archive_category_counts(path: Path, frontmatter: dict[str, object], body: str) -> list[Finding]:
    """Flag a frontmatter ``categories.asked`` count that disagrees with the probes in the archive body."""
    categories = frontmatter.get("categories")
    if not isinstance(categories, dict):
        return []
    actual_counts: dict[str, int] = {}
    for entry in parse_question_entries(body):
        if entry.category == CLOSING_CATEGORY:
            continue
        actual_counts[entry.category] = actual_counts.get(entry.category, 0) + probe_count(entry)
    findings: list[Finding] = []
    for category, tally in categories.items():
        if not isinstance(tally, dict):
            continue
        stated = tally.get("asked")
        actual = actual_counts.get(category, 0)
        if stated != actual:
            findings.append(
                Finding(
                    "archive-category-count",
                    str(path),
                    f"category {category!r} states asked={stated!r} but the body has {actual}",
                )
            )
    return findings


def _numbered_lines(text: str) -> list[int]:
    """Return the leading number of every ``n. `` line in text, in order."""
    return [int(number) for number in NUMBERED_LINE_PATTERN.findall(text)]


def check_archive_battery_items(path: Path, body: str) -> list[Finding]:
    """Flag a battery whose tag or body breaks the 3-to-6 numbered-items shape, or a stray ``[items: n]``."""
    findings: list[Finding] = []
    for entry in parse_question_entries(body):
        label = f"Q{entry.number:02d}"
        if entry.probe != "battery":
            if entry.items is not None:
                findings.append(
                    Finding(
                        "archive-battery-items",
                        str(path),
                        f"{label} carries [items: {entry.items}] but its probe is {entry.probe!r}, not battery",
                    )
                )
            continue
        if entry.items is None:
            findings.append(Finding("archive-battery-items", str(path), f"{label} is a battery with no [items: n] tag"))
            continue
        problems: list[str] = []
        if entry.items not in BATTERY_ITEMS_RANGE:
            problems.append("a battery holds 3 to 6 items")
        question_part, _, answer_part = entry.body.partition("**A:**")
        expected = list(range(1, entry.items + 1))
        for kind, numbers in (("items", _numbered_lines(question_part)), ("answers", _numbered_lines(answer_part))):
            if numbers != expected:
                problems.append(f"its numbered {kind} are {numbers}")
        if problems:
            findings.append(
                Finding(
                    "archive-battery-items",
                    str(path),
                    f"{label} states [items: {entry.items}] but " + " and ".join(problems),
                )
            )
    return findings


def check_archive_optional_section_ids(path: Path, body: str) -> list[Finding]:
    """Flag a gap or repeat in the line IDs of the optional Open research and Exports sections."""
    findings: list[Finding] = []
    for title, prefix in OPTIONAL_SECTIONS:
        heading = re.search(rf"^## {re.escape(title)}[ \t]*$", body, re.MULTILINE)
        if heading is None:
            continue
        next_section = re.compile(r"^## ", re.MULTILINE).search(body, heading.end())
        section_text = body[heading.end() : next_section.start() if next_section else len(body)]
        numbers = [int(number) for number in re.findall(rf"^- {prefix}(\d+)\b", section_text, re.MULTILINE)]
        expected = list(range(1, len(numbers) + 1))
        if numbers != expected:
            findings.append(
                Finding(
                    "archive-section-ids",
                    str(path),
                    f"the '## {title}' section's IDs {numbers} are not contiguous from {prefix}01 "
                    f"(expected {expected})",
                )
            )
    return findings


def check_profile_token_estimate(path: Path, frontmatter: dict[str, object], body: str) -> list[Finding]:
    """Recompute the profile token estimate; flag a ceiling breach or a stale stored value."""
    estimate = len(body) // 4
    findings: list[Finding] = []
    if estimate > TOKEN_CEILING:
        findings.append(
            Finding(
                "profile-token-ceiling",
                str(path),
                f"recomputed token estimate {estimate} exceeds the {TOKEN_CEILING} ceiling",
            )
        )
    stored = frontmatter.get("token_estimate")
    if stored != estimate:
        findings.append(
            Finding(
                "profile-token-estimate-mismatch",
                str(path),
                f"frontmatter token_estimate {stored!r} disagrees with the recomputed {estimate}",
            )
        )
    return findings


def check_profile_required_sections(path: Path, body: str) -> list[Finding]:
    """Flag a missing required XML section, or one out of the profile format's fixed order."""
    present_sections = [tag for tag in SECTION_TAG_PATTERN.findall(body) if tag in REQUIRED_PROFILE_SECTIONS]
    findings: list[Finding] = []
    missing = [section for section in REQUIRED_PROFILE_SECTIONS if section not in present_sections]
    for section in missing:
        findings.append(Finding("profile-missing-section", str(path), f"required section <{section}> is absent"))
    expected_order = [section for section in REQUIRED_PROFILE_SECTIONS if section not in missing]
    if present_sections != expected_order:
        findings.append(
            Finding(
                "profile-section-order",
                str(path),
                f"sections appear as {present_sections} but the required order is {expected_order}",
            )
        )
    return findings


def check_golden_examples(path: Path, body: str) -> list[Finding]:
    """Flag a golden example missing its ``<bad>``, ``<good>``, or ``<why>`` child."""
    findings: list[Finding] = []
    for example_index, example_match in enumerate(EXAMPLE_BLOCK_PATTERN.finditer(body), start=1):
        example_body = example_match.group(1)
        for child in REQUIRED_EXAMPLE_CHILDREN:
            if f"<{child}>" not in example_body:
                findings.append(
                    Finding(
                        "golden-example-incomplete",
                        str(path),
                        f"example {example_index} is missing its <{child}> child",
                    )
                )
    return findings


def check_calibration_round_contiguity(calibration_dir: Path) -> list[Finding]:
    """Flag a gap or repeat in the calibration round numbering."""
    if not calibration_dir.is_dir():
        return []
    round_numbers = sorted(
        int(round_match.group(1))
        for round_path in calibration_dir.glob("round-*.md")
        if (round_match := ROUND_FILENAME_PATTERN.search(round_path.name)) is not None
    )
    expected = list(range(1, len(round_numbers) + 1))
    if round_numbers != expected:
        return [
            Finding(
                "calibration-round-contiguity",
                str(calibration_dir),
                f"round numbers {round_numbers} are not contiguous from 1 (expected {expected})",
            )
        ]
    return []


def check_extraction_dir_populated(extraction_dir: Path) -> list[Finding]:
    """Flag a missing extraction directory, or one with none of the four artifact files.

    Returns a single finding and nothing else when either condition holds, so
    the caller can skip every per-artifact check against a directory that was
    never there or never populated.
    """
    if not extraction_dir.is_dir():
        return [
            Finding(
                "extraction-dir-missing",
                str(extraction_dir),
                "extraction directory does not exist",
            )
        ]
    artifact_paths = (
        extraction_dir / "interview-spec.md",
        extraction_dir / "archive.md",
        extraction_dir / "profile.md",
        extraction_dir / "calibration",
    )
    if not any(path.exists() for path in artifact_paths):
        return [
            Finding(
                "extraction-dir-empty",
                str(extraction_dir),
                "extraction directory holds none of interview-spec.md, archive.md, "
                "profile.md, or a calibration/ directory",
            )
        ]
    return []


def validate_extraction(extraction_dir: Path) -> list[Finding]:
    """Run every structural check against one extraction directory.

    Args:
        extraction_dir: Path to an extraction directory (e.g.
            ``extractions/woodworking`` or a fixture directory of the same
            shape). Missing artifact files are skipped rather than flagged,
            once the directory itself is confirmed to exist and hold at
            least one artifact; This validator checks shape, not presence of
            every individual file.

    Returns:
        Every finding from every check, in file-then-check order. An empty
        list means the extraction is structurally clean. A missing or
        artifactless directory returns immediately with a single
        ``extraction-dir-missing`` or ``extraction-dir-empty`` finding.
    """
    dir_findings = check_extraction_dir_populated(extraction_dir)
    if dir_findings:
        return dir_findings

    findings: list[Finding] = []

    interview_spec_path = extraction_dir / "interview-spec.md"
    if interview_spec_path.is_file():
        _, _, interview_spec_findings = parse_frontmatter(interview_spec_path)
        findings.extend(interview_spec_findings)

    archive_path = extraction_dir / "archive.md"
    if archive_path.is_file():
        archive_frontmatter, archive_body, archive_findings = parse_frontmatter(archive_path)
        findings.extend(archive_findings)
        findings.extend(check_archive_question_numbering(archive_path, archive_body))
        findings.extend(check_archive_battery_items(archive_path, archive_body))
        findings.extend(check_archive_optional_section_ids(archive_path, archive_body))
        if archive_frontmatter is not None:
            findings.extend(check_archive_category_counts(archive_path, archive_frontmatter, archive_body))

    profile_path = extraction_dir / "profile.md"
    if profile_path.is_file():
        profile_frontmatter, profile_body, profile_findings = parse_frontmatter(profile_path)
        findings.extend(profile_findings)
        findings.extend(check_profile_required_sections(profile_path, profile_body))
        findings.extend(check_golden_examples(profile_path, profile_body))
        if profile_frontmatter is not None:
            findings.extend(check_profile_token_estimate(profile_path, profile_frontmatter, profile_body))

    calibration_dir = extraction_dir / "calibration"
    findings.extend(check_calibration_round_contiguity(calibration_dir))
    if calibration_dir.is_dir():
        for round_path in sorted(calibration_dir.glob("round-*.md")):
            _, _, round_findings = parse_frontmatter(round_path)
            findings.extend(round_findings)

    return findings


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point: validate the given extraction directory and print any findings."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "extraction_dir",
        type=Path,
        help="path to an extraction directory (e.g. extractions/woodworking)",
    )
    arguments = parser.parse_args(argv)

    findings = validate_extraction(arguments.extraction_dir)
    for finding in findings:
        print(f"{finding.path}: {finding.check}: {finding.message}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
