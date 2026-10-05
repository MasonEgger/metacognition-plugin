# ABOUTME: Behavior tests for scripts.archive_append, the single-entry archive writer.
# ABOUTME: Each test works on a tmp_path copy of the woodworking-battery fixture, never the fixture itself.
"""Tests for scripts.archive_append."""

import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

import pytest

import scripts.archive_append as archive_append
from scripts.archive_append import main
from scripts.validate_artifacts import main as validate_main

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "src" / "scripts" / "archive_append.py"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "extractions" / "woodworking-battery"

QUESTION = "Which clamp do you reach for first on a glue-up?"
ANSWER = "The long bar clamps. Cauls go on before anything else."


@pytest.fixture
def extraction(tmp_path: Path) -> Path:
    """Return a writable copy of the battery fixture."""
    target = tmp_path / "woodworking-battery"
    shutil.copytree(FIXTURE, target)
    return target


def _append(
    directory: Path,
    *,
    category: str | None = "failure-modes",
    register: str = "shop",
    probe: str = "contrast",
    question: str = QUESTION,
    answer: str = ANSWER,
    extra: Sequence[str] = (),
) -> list[str]:
    """Build an argv for one inline append; extra flags go on the end."""
    category_flags = [] if category is None else ["--category", category]
    return [
        str(directory),
        *category_flags,
        "--register",
        register,
        "--probe",
        probe,
        "--question",
        question,
        "--answer",
        answer,
        *extra,
    ]


def _frontmatter_lines(directory: Path) -> list[str]:
    """Return the archive's frontmatter lines, delimiters excluded."""
    text = (directory / "archive.md").read_text(encoding="utf-8")
    return text.split("---\n", 2)[1].splitlines()


def _snapshot(directory: Path) -> dict[str, bytes]:
    """Return every file's bytes by name, so a test can prove nothing changed."""
    return {path.name: path.read_bytes() for path in sorted(directory.iterdir())}


def test_prints_next_question_number_and_exits_zero(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(_append(extraction))

    assert code == 0
    assert capsys.readouterr().out == "Q07\n"


def test_entry_is_last_thing_under_questions(extraction: Path) -> None:
    main(_append(extraction, probe="critical-incident"))

    text = (extraction / "archive.md").read_text(encoding="utf-8")
    assert text.endswith(
        f"\n\n### Q07 [failure-modes] [shop] [probe: critical-incident]\n**Q:** {QUESTION}\n**A:** {ANSWER}\n"
    )
    assert text.count("### Q07") == 1


def test_counters_rise_and_everything_else_is_unchanged(extraction: Path) -> None:
    before = _frontmatter_lines(extraction)

    main(_append(extraction))

    after = _frontmatter_lines(extraction)
    expected = [
        "questions_asked: 7"
        if line == "questions_asked: 6"
        else line.replace("failure-modes: {asked: 0", "failure-modes: {asked: 1")
        for line in before
    ]
    assert after == expected
    assert "  failure-modes: {asked: 1, floor: 1, saturated: false}" in after


def test_body_before_the_new_entry_is_unchanged(extraction: Path) -> None:
    original = (extraction / "archive.md").read_text(encoding="utf-8")
    original_body = original.split("---\n", 2)[2]

    main(_append(extraction))

    new_body = (extraction / "archive.md").read_text(encoding="utf-8").split("---\n", 2)[2]
    assert new_body.startswith(original_body.rstrip("\n"))


def test_readme_cell_shows_new_probe_total_over_floor_sum(extraction: Path) -> None:
    before = (extraction / "README.md").read_text(encoding="utf-8")

    main(_append(extraction))

    after = (extraction / "README.md").read_text(encoding="utf-8")
    assert after == before.replace("| 8/9 |", "| 9/9 |")


def test_validator_accepts_the_result(extraction: Path) -> None:
    main(_append(extraction))

    assert validate_main([str(extraction)]) == 0


def test_file_flags_match_inline_flags(extraction: Path, tmp_path: Path) -> None:
    inline = tmp_path / "inline"
    shutil.copytree(FIXTURE, inline)
    question_file = tmp_path / "question.txt"
    answer_file = tmp_path / "answer.txt"
    question_file.write_text(QUESTION, encoding="utf-8")
    answer_file.write_text(ANSWER, encoding="utf-8")

    main(_append(inline))
    code = main(
        [
            str(extraction),
            "--category",
            "failure-modes",
            "--register",
            "shop",
            "--probe",
            "contrast",
            "--question-file",
            str(question_file),
            "--answer-file",
            str(answer_file),
        ]
    )

    assert code == 0
    assert _snapshot(extraction) == _snapshot(inline)


def test_dashes_and_curly_quotes_are_normalized_and_nothing_else(extraction: Path) -> None:
    question = "It\u2019s a \u201cclamp\u201d \u2013 right? \u2014 café"
    answer = "  \u2018Yes\u2019 \u2014 naïve and sure.  "

    main(_append(extraction, question=question, answer=answer))

    text = (extraction / "archive.md").read_text(encoding="utf-8")
    assert '**Q:** It\'s a "clamp" - right? - café\n' in text
    assert "**A:**   'Yes' - naïve and sure.  \n" in text


@pytest.mark.parametrize("flag_value", ["\u2013", "\u2014", "\u2018", "\u2019", "\u201c", "\u201d"])
def test_every_normalized_codepoint_leaves_no_trace(extraction: Path, flag_value: str) -> None:
    main(_append(extraction, question=f"a{flag_value}b", answer=f"c{flag_value}d"))

    text = (extraction / "archive.md").read_text(encoding="utf-8")
    assert flag_value not in text


def _assert_error_writes_nothing(
    directory: Path, argv: list[str], capsys: pytest.CaptureFixture[str], mention: str
) -> None:
    before = _snapshot(directory)

    code = main(argv)

    captured = capsys.readouterr()
    assert code == 2
    assert captured.out == ""
    assert len(captured.err.strip().splitlines()) == 1
    assert mention in captured.err
    assert _snapshot(directory) == before


def test_missing_archive_exits_two(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (extraction / "archive.md").unlink()

    _assert_error_writes_nothing(extraction, _append(extraction), capsys, "archive.md")


def test_unparseable_frontmatter_exits_two(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    archive = extraction / "archive.md"
    archive.write_text(
        archive.read_text(encoding="utf-8").replace("---\n\n# Archive", "\n# Archive", 1), encoding="utf-8"
    )

    _assert_error_writes_nothing(extraction, _append(extraction), capsys, "frontmatter")


def test_unknown_category_exits_two(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _assert_error_writes_nothing(extraction, _append(extraction, category="nope"), capsys, "nope")


def test_missing_answer_exits_two(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    argv = _append(extraction)[:-2]

    _assert_error_writes_nothing(extraction, argv, capsys, "answer")


def test_missing_answer_file_exits_two(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    argv = _append(extraction)[:-2] + ["--answer-file", str(extraction / "absent.txt")]

    _assert_error_writes_nothing(extraction, argv, capsys, "absent.txt")


@pytest.mark.parametrize("field", ["question", "answer"])
@pytest.mark.parametrize("separator", ["\n", "\r"])
def test_inline_line_break_exits_two(
    extraction: Path, capsys: pytest.CaptureFixture[str], field: str, separator: str
) -> None:
    argv = _append(extraction, **{field: f"first{separator}second"})

    _assert_error_writes_nothing(extraction, argv, capsys, field)


@pytest.mark.parametrize("field", ["question", "answer"])
def test_multi_line_file_exits_two(
    extraction: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], field: str
) -> None:
    source = tmp_path / f"{field}.txt"
    source.write_text("first\nsecond\n", encoding="utf-8")
    argv = _append(extraction)
    argv[argv.index(f"--{field}")] = f"--{field}-file"
    argv[argv.index(f"--{field}-file") + 1] = str(source)

    _assert_error_writes_nothing(extraction, argv, capsys, field)


def test_one_line_files_with_trailing_newlines_succeed(extraction: Path, tmp_path: Path) -> None:
    question_file = tmp_path / "question.txt"
    answer_file = tmp_path / "answer.txt"
    question_file.write_text(QUESTION + "\n", encoding="utf-8")
    answer_file.write_text(ANSWER + "\r\n", encoding="utf-8")

    code = main(
        [
            str(extraction),
            "--category",
            "failure-modes",
            "--register",
            "shop",
            "--probe",
            "contrast",
            "--question-file",
            str(question_file),
            "--answer-file",
            str(answer_file),
        ]
    )

    assert code == 0
    assert f"**Q:** {QUESTION}\n**A:** {ANSWER}\n" in (extraction / "archive.md").read_text(encoding="utf-8")


def test_write_failure_exits_two_and_leaves_both_files_and_no_temporary(
    extraction: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    real_write = archive_append._write_temporary

    def failing_write(path: Path, text: str) -> Path:
        if path.name == "README.md":
            raise OSError("disk full")
        return real_write(path, text)

    monkeypatch.setattr(archive_append, "_write_temporary", failing_write)
    names = {path.name for path in extraction.iterdir()}

    _assert_error_writes_nothing(extraction, _append(extraction), capsys, "README.md")

    assert {path.name for path in extraction.iterdir()} == names


def test_missing_readme_exits_two(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (extraction / "README.md").unlink()

    _assert_error_writes_nothing(extraction, _append(extraction), capsys, "README.md")


def test_battery_without_items_is_refused(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _assert_error_writes_nothing(extraction, _append(extraction, probe="battery"), capsys, "--items")


def test_bracket_in_a_heading_field_exits_two(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _assert_error_writes_nothing(extraction, _append(extraction, register="sh]op"), capsys, "register")


def test_no_temporary_file_remains_after_success_or_error(extraction: Path) -> None:
    names = {path.name for path in extraction.iterdir()}

    main(_append(extraction))
    main(_append(extraction, category="nope"))

    assert {path.name for path in extraction.iterdir()} == names


def test_three_appends_across_two_categories(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    main(_append(extraction, category="failure-modes"))
    main(_append(extraction, category="joinery", probe="forced-choice"))
    main(_append(extraction, category="failure-modes", probe="ladder"))

    assert capsys.readouterr().out.split() == ["Q07", "Q08", "Q09"]
    frontmatter = _frontmatter_lines(extraction)
    assert "questions_asked: 9" in frontmatter
    assert "  failure-modes: {asked: 2, floor: 1, saturated: false}" in frontmatter
    assert "  joinery: {asked: 6, floor: 2, saturated: true}" in frontmatter
    assert "| 11/9 |" in (extraction / "README.md").read_text(encoding="utf-8")
    assert validate_main([str(extraction)]) == 0


def test_subprocess_runs_from_another_directory(extraction: Path, tmp_path: Path) -> None:
    other = tmp_path / "elsewhere"
    other.mkdir()

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *_append(extraction)],
        capture_output=True,
        text=True,
        cwd=other,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == "Q07\n"
    assert validate_main([str(extraction)]) == 0


STEM = "For each of these finishing steps, would you do it before assembly?"
ITEMS = ["Sand the inside faces.", "Pre-finish the tenons.", "Wax the dovetail pins."]
ANSWERS = ["Yes. Always.", "No. Glue needs bare wood.", "Yes, a little."]


def _numbered(lines: Sequence[str]) -> str:
    """Return lines as a numbered block, one per line."""
    return "\n".join(f"{number}. {line}" for number, line in enumerate(lines, start=1))


def _battery(
    directory: Path,
    *,
    items: int | str = 3,
    question: str | None = None,
    answer: str | None = None,
    category: str | None = "failure-modes",
    extra: Sequence[str] = (),
) -> list[str]:
    """Build an argv for a battery append; the default question and answer carry three numbered lines."""
    return _append(
        directory,
        category=category,
        probe="battery",
        question=f"{STEM}\n{_numbered(ITEMS)}" if question is None else question,
        answer=_numbered(ANSWERS) if answer is None else answer,
        extra=["--items", str(items), *extra],
    )


def _archive_text(directory: Path) -> str:
    """Return archive.md's text."""
    return (directory / "archive.md").read_text(encoding="utf-8")


def test_battery_writes_heading_and_body_and_counts_items(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(_battery(extraction))

    assert code == 0
    assert capsys.readouterr().out == "Q07\n"
    assert _archive_text(extraction).endswith(
        "\n\n### Q07 [failure-modes] [shop] [probe: battery] [items: 3]\n"
        f"**Q:** {STEM}\n1. {ITEMS[0]}\n2. {ITEMS[1]}\n3. {ITEMS[2]}\n"
        f"**A:**\n1. {ANSWERS[0]}\n2. {ANSWERS[1]}\n3. {ANSWERS[2]}\n"
    )
    frontmatter = _frontmatter_lines(extraction)
    assert "questions_asked: 7" in frontmatter
    assert "  failure-modes: {asked: 3, floor: 1, saturated: false}" in frontmatter
    assert "| 11/9 |" in (extraction / "README.md").read_text(encoding="utf-8")
    assert validate_main([str(extraction)]) == 0


def test_battery_from_files_with_trailing_newlines(extraction: Path, tmp_path: Path) -> None:
    question_file = tmp_path / "question.txt"
    answer_file = tmp_path / "answer.txt"
    question_file.write_text(f"{STEM}\n{_numbered(ITEMS)}\n", encoding="utf-8")
    answer_file.write_text(_numbered(ANSWERS) + "\n", encoding="utf-8")

    code = main(
        [
            str(extraction),
            "--category",
            "failure-modes",
            "--register",
            "shop",
            "--probe",
            "battery",
            "--items",
            "3",
            "--question-file",
            str(question_file),
            "--answer-file",
            str(answer_file),
        ]
    )

    assert code == 0
    assert validate_main([str(extraction)]) == 0


def test_battery_of_six_items_counts_six(extraction: Path) -> None:
    items = [f"item {number}" for number in range(1, 7)]
    argv = _battery(
        extraction, items=6, question=f"{STEM}\n{_numbered(items)}", answer=_numbered([f"a{n}" for n in range(6)])
    )

    assert main(argv) == 0
    assert "  failure-modes: {asked: 6, floor: 1, saturated: false}" in _frontmatter_lines(extraction)
    assert validate_main([str(extraction)]) == 0


@pytest.mark.parametrize("items", ["2", "7", "0"])
def test_items_outside_three_to_six_is_refused(
    extraction: Path, capsys: pytest.CaptureFixture[str], items: str
) -> None:
    _assert_error_writes_nothing(extraction, _battery(extraction, items=items), capsys, "--items")


def test_items_disagreeing_with_question_lines_is_refused(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _assert_error_writes_nothing(extraction, _battery(extraction, items=4), capsys, "question")


def test_items_disagreeing_with_answer_lines_is_refused(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    argv = _battery(extraction, answer=_numbered(ANSWERS[:2]))

    _assert_error_writes_nothing(extraction, argv, capsys, "answer")


@pytest.mark.parametrize(
    ("question", "answer"),
    [
        (f"{STEM}\nplain line\n{_numbered(ITEMS)}", None),
        (f"{STEM}\n1. a\n3. b\n4. c", None),
        (f"{STEM}\n{_numbered(ITEMS)}\n\n", None),
        (None, f"{_numbered(ANSWERS)}\nand a trailing remark"),
        (None, "1. one\n3. two\n2. three"),
        (_numbered(ITEMS), None),
    ],
)
def test_malformed_battery_structure_is_refused(
    extraction: Path, capsys: pytest.CaptureFixture[str], question: str | None, answer: str | None
) -> None:
    _assert_error_writes_nothing(extraction, _battery(extraction, question=question, answer=answer), capsys, "battery")


def test_items_with_another_probe_type_is_refused(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _assert_error_writes_nothing(extraction, _append(extraction, extra=["--items", "3"]), capsys, "--items")


def test_battery_normalizes_dashes_per_line(extraction: Path) -> None:
    items = ["Sand \u2014 all faces.", "b", "c"]
    argv = _battery(extraction, question=f"{STEM}\n{_numbered(items)}")

    assert main(argv) == 0
    assert "1. Sand - all faces.\n" in _archive_text(extraction)


def test_evidence_entry_counts_one_probe(extraction: Path) -> None:
    assert main(_append(extraction, probe="evidence")) == 0

    assert "  failure-modes: {asked: 1, floor: 1, saturated: false}" in _frontmatter_lines(extraction)
    assert "| 9/9 |" in (extraction / "README.md").read_text(encoding="utf-8")
    assert validate_main([str(extraction)]) == 0


def test_closing_uses_pseudo_category_and_touches_no_tally(extraction: Path) -> None:
    before = _frontmatter_lines(extraction)
    readme = (extraction / "README.md").read_text(encoding="utf-8")

    code = main(_append(extraction, category=None, probe="open", extra=["--closing"]))

    assert code == 0
    assert _archive_text(extraction).endswith(
        f"\n\n### Q07 [closing] [shop] [probe: open]\n**Q:** {QUESTION}\n**A:** {ANSWER}\n"
    )
    expected = ["questions_asked: 7" if line == "questions_asked: 6" else line for line in before]
    assert _frontmatter_lines(extraction) == expected
    assert (extraction / "README.md").read_text(encoding="utf-8") == readme
    assert validate_main([str(extraction)]) == 0


@pytest.mark.parametrize(
    ("argv_extra", "mention"),
    [
        (["--category", "failure-modes"], "--category"),
        (["--saturated"], "--saturated"),
    ],
)
def test_closing_with_a_contradictory_flag_is_refused(
    extraction: Path, capsys: pytest.CaptureFixture[str], argv_extra: list[str], mention: str
) -> None:
    argv = [*_append(extraction, category=None), "--closing", *argv_extra]

    _assert_error_writes_nothing(extraction, argv, capsys, mention)


def test_closing_battery_is_refused(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    argv = _battery(extraction, category=None, extra=["--closing"])

    _assert_error_writes_nothing(extraction, argv, capsys, "--closing")


def test_category_is_required_without_closing(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _assert_error_writes_nothing(extraction, _append(extraction, category=None), capsys, "--category")


def test_saturated_flips_only_that_category(extraction: Path) -> None:
    before = _frontmatter_lines(extraction)

    assert main(_append(extraction, extra=["--saturated"])) == 0

    after = _frontmatter_lines(extraction)
    changed = [line for line in after if line not in before]
    assert changed == ["questions_asked: 7", "  failure-modes: {asked: 1, floor: 1, saturated: true}"]
    assert validate_main([str(extraction)]) == 0


def test_ledger_line_is_appended_with_next_id(extraction: Path) -> None:
    line = '(Q07 vs Q03): "oil first" vs "wax first." Resolution: unresolved'

    assert main(_append(extraction, extra=["--ledger", line])) == 0

    text = _archive_text(extraction)
    assert "- L01 (Q01 vs Q03): " in text and f"\n- L02 {line}\n\n## Open research" in text, (
        "L02 follows L01 inside the ledger section"
    )
    assert validate_main([str(extraction)]) == 0


def test_research_and_export_lines_get_next_ids(extraction: Path) -> None:
    research = "(Q07): Whether glue-up open time changes in cold shops. Status: unresolved"
    export = "(Q07): Which sandpaper brand to buy -> unassigned"

    assert main(_append(extraction, extra=["--research", research, "--export", export])) == 0

    text = _archive_text(extraction)
    assert f"Status: resolved in Q05\n- R02 {research}\n\n## Exports" in text
    assert f"-> unassigned\n- E02 {export}\n\n## Questions" in text
    assert validate_main([str(extraction)]) == 0


def _without_optional_sections(directory: Path) -> None:
    """Strip the ledger, Open research, and Exports sections from a copy's archive."""
    text = _archive_text(directory)
    start = text.index("## Contradiction ledger")
    end = text.index("## Questions")
    (directory / "archive.md").write_text(text[:start] + text[end:], encoding="utf-8")


def test_missing_sections_are_created_in_spec_order(extraction: Path) -> None:
    _without_optional_sections(extraction)

    code = main(
        _append(
            extraction,
            extra=["--export", "(Q07): finish -> unassigned", "--research", "(Q07): a thing. Status: unresolved"]
            + ["--ledger", '(Q01 vs Q07): "a" vs "b". Resolution: unresolved'],
        )
    )

    assert code == 0
    text = _archive_text(extraction)
    positions = [
        text.index(heading) for heading in ("## Contradiction ledger", "## Open research", "## Exports", "## Questions")
    ]
    assert positions == sorted(positions)
    assert "## Contradiction ledger\n\n- L01 (Q01 vs Q07)" in text
    assert "## Open research\n\n- R01 (Q07)" in text
    assert "## Exports\n\n- E01 (Q07)" in text
    assert validate_main([str(extraction)]) == 0


def test_only_exports_created_lands_before_questions(extraction: Path) -> None:
    _without_optional_sections(extraction)

    assert main(_append(extraction, extra=["--export", "(Q07): finish -> unassigned"])) == 0

    text = _archive_text(extraction)
    assert "\n\n## Exports\n\n- E01 (Q07): finish -> unassigned\n\n## Questions\n" in text
    assert "## Open research" not in text


@pytest.mark.parametrize("flag", ["--ledger", "--export", "--research"])
@pytest.mark.parametrize("bad_line", ["", "first\nsecond", "no parenthesis"])
def test_bad_section_line_is_refused(
    extraction: Path, capsys: pytest.CaptureFixture[str], flag: str, bad_line: str
) -> None:
    _assert_error_writes_nothing(extraction, _append(extraction, extra=[flag, bad_line]), capsys, flag)


def test_battery_saturated_and_export_apply_in_one_write(extraction: Path) -> None:
    argv = _battery(extraction, extra=["--saturated", "--export", "(Q07): finish -> unassigned"])

    assert main(argv) == 0

    frontmatter = _frontmatter_lines(extraction)
    assert "  failure-modes: {asked: 3, floor: 1, saturated: true}" in frontmatter
    assert "- E02 (Q07): finish -> unassigned" in _archive_text(extraction)
    assert "| 11/9 |" in (extraction / "README.md").read_text(encoding="utf-8")
    assert validate_main([str(extraction)]) == 0


def test_a_failed_combined_run_writes_nothing(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    argv = _battery(extraction, extra=["--saturated", "--export", "no parenthesis"])

    _assert_error_writes_nothing(extraction, argv, capsys, "--export")


def test_scripted_interview_round_trip(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    codes = [
        main(_append(extraction, category="failure-modes", probe="open")),
        main(_battery(extraction, category="decision-heuristics")),
        main(
            _append(
                extraction,
                category="failure-modes",
                probe="evidence",
                extra=["--research", "(Q07): Glue open time. Status: resolved in Q09", "--saturated"],
            )
        ),
        main(_append(extraction, category="signature-habits", extra=["--export", "(Q10): sanding -> unassigned"])),
        main(_append(extraction, category=None, probe="open", extra=["--closing"])),
    ]

    assert codes == [0] * 5
    assert capsys.readouterr().out.split() == ["Q07", "Q08", "Q09", "Q10", "Q11"]
    frontmatter = _frontmatter_lines(extraction)
    assert "questions_asked: 11" in frontmatter
    assert "  failure-modes: {asked: 2, floor: 1, saturated: true}" in frontmatter
    assert "  decision-heuristics: {asked: 3, floor: 1, saturated: false}" in frontmatter
    assert "| 14/9 |" in (extraction / "README.md").read_text(encoding="utf-8")
    assert validate_main([str(extraction)]) == 0
