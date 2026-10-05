# ABOUTME: Behavior tests for scripts.archive_append, the single-entry archive writer.
# ABOUTME: Each test works on a tmp_path copy of the woodworking-battery fixture, never the fixture itself.
"""Tests for scripts.archive_append."""

import shutil
import subprocess
import sys
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
    category: str = "failure-modes",
    register: str = "shop",
    probe: str = "contrast",
    question: str = QUESTION,
    answer: str = ANSWER,
) -> list[str]:
    """Build an argv for one inline append."""
    return [
        str(directory),
        "--category",
        category,
        "--register",
        register,
        "--probe",
        probe,
        "--question",
        question,
        "--answer",
        answer,
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


def test_battery_is_out_of_scope_and_refused(extraction: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _assert_error_writes_nothing(extraction, _append(extraction, probe="battery"), capsys, "battery")


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
