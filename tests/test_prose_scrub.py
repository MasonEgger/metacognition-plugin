# ABOUTME: Tests for tools/prose_scrub.py, the prose writing-rules scanner.
# Covers dash and quote codepoints, banned vocabulary, code fences, file collection, the allowlist,
# Python comment-only scanning, JSON description-value scanning, and the CLI.
"""Tests for tools/prose_scrub.py."""

import subprocess
import sys
from pathlib import Path

import prose_scrub
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "tools" / "prose_scrub.py"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "prose"
WRITING_RULES = REPO_ROOT / ".claude" / "rules" / "vendored" / "writing.md"


def test_em_dash_reported_with_path_and_line() -> None:
    """A line containing an em-dash (U+2014) is reported with file path and line number."""
    # Arrange
    text = "clean first line\nbroken — second line\n"

    # Act
    findings = prose_scrub.scan_text(text, path="doc.md")

    # Assert
    assert len(findings) == 1
    finding = findings[0]
    assert finding.path == "doc.md"
    assert finding.line == 2
    assert finding.rule == "em-dash"


def test_en_dash_reported_hyphen_minus_not() -> None:
    """An en-dash (U+2013) is reported; a plain hyphen-minus is not."""
    # Arrange
    text = "a well-formed hyphen-minus line\nrange 1 – 10\n"

    # Act
    findings = prose_scrub.scan_text(text, path="doc.md")

    # Assert
    assert [(finding.line, finding.rule) for finding in findings] == [(2, "en-dash")]


def test_each_curly_quote_reported() -> None:
    """Each curly quote codepoint (U+2018, U+2019, U+201C, U+201D) is reported."""
    # Arrange
    curly_quotes = ("‘", "’", "“", "”")
    text = "".join(f"quote {quote} here\n" for quote in curly_quotes)

    # Act
    findings = prose_scrub.scan_text(text, path="doc.md")

    # Assert
    assert [finding.rule for finding in findings] == ["curly-quote"] * 4
    assert [finding.line for finding in findings] == [1, 2, 3, 4]


def test_banned_vocabulary_case_insensitive() -> None:
    """Banned vocabulary from the writing rules' short list is reported case-insensitively."""
    # Arrange
    sample_words = (
        "Delve",
        "TAPESTRY",
        "seamless",
        "Comprehensive",
        "ROBUST",
        "Leverage",
        "crucial",
        "Pivotal",
    )

    for sample_word in sample_words:
        # Act
        findings = prose_scrub.scan_text(f"we {sample_word} daily\n", path="doc.md")

        # Assert
        assert [finding.rule for finding in findings] == ["banned-vocabulary"], sample_word


def test_banned_word_inside_longer_word_not_reported() -> None:
    """A banned word embedded in a longer word (cantilevered) is not reported."""
    # Arrange
    text = "The cantilevered beam held firm.\n"

    # Act
    findings = prose_scrub.scan_text(text, path="doc.md")

    # Assert
    assert findings == []


def test_code_fence_exempts_vocabulary_but_not_em_dash() -> None:
    """Fenced code blocks are exempt from vocabulary checks but not em-dash checks."""
    # Arrange
    text = 'prose before\n```python\nleverage = compute()\nlabel = "a — b"\n```\nprose after\n'

    # Act
    findings = prose_scrub.scan_text(text, path="doc.md")

    # Assert
    assert [(finding.line, finding.rule) for finding in findings] == [(4, "em-dash")]


def test_clean_document_returns_empty_list() -> None:
    """A clean document produces zero findings and an empty list."""
    # Arrange
    text = "A plain paragraph.\n\nAnother one with a hyphen-minus compound-word.\n"

    # Act
    findings = prose_scrub.scan_text(text, path="doc.md")

    # Assert
    assert findings == []


def test_collect_files_scanned_suffixes_skipping_git_and_tmp(tmp_path: Path) -> None:
    """Directory collection returns .md, .py, and .json files and skips .git/ and tmp/."""
    # Arrange
    (tmp_path / "a.md").write_text("hello\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("hello\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "c.md").write_text("hello\n", encoding="utf-8")
    (tmp_path / "tmp").mkdir()
    (tmp_path / "tmp" / "d.md").write_text("hello\n", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "e.md").write_text("hello\n", encoding="utf-8")
    (tmp_path / "f.py").write_text("# hello\n", encoding="utf-8")
    (tmp_path / "g.json").write_text("{}\n", encoding="utf-8")

    # Act
    collected = prose_scrub.collect_files(tmp_path)

    # Assert
    assert sorted(collected) == [
        tmp_path / "a.md",
        tmp_path / "f.py",
        tmp_path / "g.json",
        tmp_path / "sub" / "e.md",
    ]


def test_collect_files_skips_environments_build_output_and_caches(tmp_path: Path) -> None:
    """Environments, build output, and caches are never scanned, however deep a cache sits."""
    # Arrange
    kept = tmp_path / "docs" / "kept.md"
    kept.parent.mkdir()
    kept.write_text("hello\n", encoding="utf-8")
    skipped = (
        ".venv/lib/pkg/readme.md",
        "site/index.md",
        "dist/notes.md",
        ".pytest_cache/README.md",
        ".mypy_cache/meta.json",
        ".ruff_cache/notes.md",
        "docs/__pycache__/cached.py",
        "goal.md",
        "commit-msg.md",
    )
    for relative in skipped:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("hello\n", encoding="utf-8")

    # Act
    collected = prose_scrub.collect_files(tmp_path)

    # Assert
    assert collected == [kept]


def test_build_output_names_only_skipped_at_the_top_level(tmp_path: Path) -> None:
    """A nested directory called site or dist is repo prose and is scanned."""
    # Arrange
    nested = tmp_path / "docs" / "site" / "page.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("hello\n", encoding="utf-8")

    # Act
    collected = prose_scrub.collect_files(tmp_path)

    # Assert
    assert collected == [nested]


def test_python_em_dash_in_comment_reported(tmp_path: Path) -> None:
    """A .py file with an em-dash in a comment line is reported with its line number."""
    # Arrange
    script_path = tmp_path / "sample.py"
    script_path.write_text("value = 1\n    # centralized map — change here\n", encoding="utf-8")

    # Act
    findings = prose_scrub.scan_file(script_path)

    # Assert
    assert [(finding.line, finding.rule) for finding in findings] == [(2, "em-dash")]


def test_python_em_dash_in_string_literal_not_reported(tmp_path: Path) -> None:
    """A .py file with an em-dash only in a string literal scans clean."""
    # Arrange
    script_path = tmp_path / "sample.py"
    script_path.write_text(
        'REPLACEMENTS = {"—": "-"}\nmessage = "a — b"  # trailing note\n',
        encoding="utf-8",
    )

    # Act
    findings = prose_scrub.scan_file(script_path)

    # Assert
    assert findings == []


def test_json_em_dash_in_description_value_reported(tmp_path: Path) -> None:
    """A .json file with an em-dash in a description value is reported, at any depth."""
    # Arrange
    manifest_path = tmp_path / "plugin.json"
    manifest_path.write_text(
        '{\n  "plugins": [\n    {"description": "system — management"}\n  ]\n}\n',
        encoding="utf-8",
    )

    # Act
    findings = prose_scrub.scan_file(manifest_path)

    # Assert
    assert [(finding.line, finding.rule) for finding in findings] == [(3, "em-dash")]


def test_json_em_dash_outside_description_not_reported(tmp_path: Path) -> None:
    """A .json file with an em-dash outside description values scans clean."""
    # Arrange
    manifest_path = tmp_path / "data.json"
    manifest_path.write_text(
        '{\n  "separator": "—",\n  "description": "a clean value",\n  "notes": "range 1 – 10"\n}\n',
        encoding="utf-8",
    )

    # Act
    findings = prose_scrub.scan_file(manifest_path)

    # Assert
    assert findings == []


def test_skip_vocabulary_flag_exempts_vocabulary_but_not_codepoints() -> None:
    """With skip_vocabulary, banned words pass but em-dashes are still reported."""
    # Arrange
    text = "we leverage the seamless tapestry\nbroken em-dash — line\n"

    # Act
    findings = prose_scrub.scan_text(text, path="doc.md", skip_vocabulary=True)

    # Assert
    assert [(finding.line, finding.rule) for finding in findings] == [(2, "em-dash")]


def test_vendored_writing_rules_are_vocabulary_exempt() -> None:
    """The vendored writing rules list the banned words, so they are allowlisted; lookalikes are not."""
    # Arrange
    lookalike_path = REPO_ROOT / "x.claude" / "rules" / "vendored" / "writing.md"
    sibling_path = REPO_ROOT / ".claude" / "rules" / "vendored" / "other.md"
    readme_path = REPO_ROOT / "README.md"

    # Act / Assert
    assert prose_scrub.is_vocabulary_exempt(WRITING_RULES)
    assert not prose_scrub.is_vocabulary_exempt(lookalike_path)
    assert not prose_scrub.is_vocabulary_exempt(sibling_path)
    assert not prose_scrub.is_vocabulary_exempt(readme_path)


def test_writing_rules_scan_clean_via_allowlist() -> None:
    """The committed writing rules pass scan_file because the allowlist exempts their vocabulary."""
    # Act
    findings = prose_scrub.scan_file(WRITING_RULES)

    # Assert
    assert findings == []


def test_writing_rules_content_fails_vocabulary_at_a_non_allowlisted_path(tmp_path: Path) -> None:
    """The same content at a non-allowlisted path fails on vocabulary: the allowlist keeps the real file clean."""
    # Arrange
    copy_path = tmp_path / "writing.md"
    copy_path.write_text(WRITING_RULES.read_text(encoding="utf-8"), encoding="utf-8")

    # Act
    findings = prose_scrub.scan_file(copy_path)

    # Assert
    assert not prose_scrub.is_vocabulary_exempt(copy_path)
    assert any(finding.rule == "banned-vocabulary" for finding in findings)


def test_cli_writing_rules_scan_clean() -> None:
    """The committed writing rules pass the scrub: vocabulary exempted, codepoints clean."""
    # Act
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(WRITING_RULES)],
        capture_output=True,
        text=True,
        check=False,
    )

    # Assert
    assert result.returncode == 0, result.stdout
    assert result.stdout == ""


def test_cli_reports_only_dirty_fixture_and_exits_1() -> None:
    """Run against the fixture directory: exit 1, output names only the dirty file."""
    # Act
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(FIXTURE_DIR)],
        capture_output=True,
        text=True,
        check=False,
    )

    # Assert
    assert result.returncode == 1
    assert "dirty.md" in result.stdout
    assert "clean.md" not in result.stdout


def test_cli_reports_dirty_fixture_rules_with_line_numbers() -> None:
    """The dirty fixture fails for an em-dash on line 3 and a banned word on line 5."""
    # Act
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(FIXTURE_DIR / "dirty.md")],
        capture_output=True,
        text=True,
        check=False,
    )

    # Assert
    assert result.returncode == 1
    lines = result.stdout.splitlines()
    assert len(lines) == 2
    assert lines[0].endswith("dirty.md:3: em-dash: This sentence has an em-dash — right here.")
    assert lines[1].endswith("dirty.md:5: banned-vocabulary: We plan to leverage the tooling.")


def test_cli_clean_file_exits_0_with_empty_output() -> None:
    """Run against only the clean fixture: exit 0, empty output."""
    # Act
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(FIXTURE_DIR / "clean.md")],
        capture_output=True,
        text=True,
        check=False,
    )

    # Assert
    assert result.returncode == 0
    assert result.stdout == ""


def test_non_exempt_path_with_banned_word_still_fails(tmp_path: Path) -> None:
    """A banned word outside the allowlisted globs still fails: the exemption is scoped, not repo-wide."""
    # Arrange
    plugin_file = tmp_path / "metacognition" / "references" / "a.md"
    plugin_file.parent.mkdir(parents=True)
    plugin_file.write_text("This approach is robust and well tested.\n", encoding="utf-8")

    # Act
    findings = prose_scrub.scan_file(plugin_file)

    # Assert
    assert [finding.rule for finding in findings] == ["banned-vocabulary"]


def test_glob_matcher_crosses_directories_on_double_star() -> None:
    """'**' matches zero or more path segments, so a nested path matches a trailing '/**' glob."""
    # Arrange
    globs = ("docs/verbatim/**",)

    # Act / Assert
    assert prose_scrub.path_matches_any_glob("docs/verbatim/x/y.md", globs)
    assert not prose_scrub.path_matches_any_glob("metacognition/references/a.md", globs)


def test_fixture_archive_banned_word_is_vocabulary_exempt() -> None:
    """A banned word inside the committed fixture archive.md is exempt: extraction data is verbatim."""
    # Arrange
    archive_path = REPO_ROOT / "tests" / "fixtures" / "extractions" / "woodworking" / "archive.md"
    text = archive_path.read_text(encoding="utf-8") + "\nThis is a robust jig.\n"

    # Act
    findings = prose_scrub.scan_text(text, path=str(archive_path), skip_vocabulary=False)
    exempt = prose_scrub.is_vocabulary_exempt(archive_path)

    # Assert
    assert any(finding.rule == "banned-vocabulary" for finding in findings)
    assert exempt
    findings_with_exemption = prose_scrub.scan_text(text, path=str(archive_path), skip_vocabulary=exempt)
    assert not any(finding.rule == "banned-vocabulary" for finding in findings_with_exemption)


def test_fixture_archive_em_dash_still_fails() -> None:
    """The extraction exemption is vocabulary-only: an em-dash inside the same archive.md still fails."""
    # Arrange
    archive_path = REPO_ROOT / "tests" / "fixtures" / "extractions" / "woodworking" / "archive.md"

    # Act
    exempt = prose_scrub.is_vocabulary_exempt(archive_path)
    findings = prose_scrub.scan_text("broken — line\n", path=str(archive_path), skip_vocabulary=exempt)

    # Assert
    assert exempt
    assert [finding.rule for finding in findings] == ["em-dash"]


@pytest.mark.parametrize(
    "relative_path",
    [
        "tests/fixtures/extractions/woodworking/archive.md",
        "tests/fixtures/extractions/woodworking/profile.md",
        "tests/fixtures/extractions/woodworking/compile-log.md",
        "tests/fixtures/extractions/woodworking/calibration/r.md",
        "tests/fixtures/extractions-bad/numbering-gap/archive.md",
        "tests/fixtures/extractions-bad/bad-yaml/profile.md",
        "tests/fixtures/calibration/corrections-round-02.md",
        "tests/fixtures/plugins/woodshop/skills/woodworking/references/profile.md",
        "tests/fixtures/plugins/woodshop/skills/woodworking/references/archive.md",
    ],
)
def test_verbatim_surfaces_are_vocabulary_exempt(tmp_path: Path, relative_path: str) -> None:
    """A banned word inside each verbatim surface (extraction data, bad extractions, calibration, skillify copies)."""
    # Arrange
    candidate_path = tmp_path / relative_path
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text("This approach is robust and comprehensive.\n", encoding="utf-8")

    # Act
    findings = prose_scrub.scan_file(candidate_path)

    # Assert
    assert prose_scrub.is_vocabulary_exempt(candidate_path)
    assert findings == []


@pytest.mark.parametrize(
    "relative_path",
    [
        "extractions/woodworking/archive.md",
        "tests/fixtures/prose/clean.md",
        "tests/fixtures/prose/dirty.md",
        "tests/test_something.md",
        "docs/index.md",
        "src/references/settings.md",
        "metacognition/skills/design/SKILL.md",
        "evals/README.md",
        ".ai-sessions/session-x.md",
        "spec.md",
    ],
)
def test_other_paths_are_not_vocabulary_exempt(tmp_path: Path, relative_path: str) -> None:
    """The allowlist is the verbatim surfaces only; the repo's own prose, and the same names elsewhere, are scanned."""
    # Arrange
    candidate_path = tmp_path / relative_path
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text("This approach is robust and comprehensive.\n", encoding="utf-8")

    # Act
    findings = prose_scrub.scan_file(candidate_path)

    # Assert
    assert not prose_scrub.is_vocabulary_exempt(candidate_path)
    assert [finding.rule for finding in findings] == ["banned-vocabulary"]


def test_cli_verbatim_fixture_surfaces_scan_clean() -> None:
    """The committed extractions, bad extractions, calibration round, and fixture plugin scan clean end to end."""
    # Arrange
    fixtures = REPO_ROOT / "tests" / "fixtures"
    targets = [str(fixtures / name) for name in ("extractions", "extractions-bad", "calibration", "plugins")]

    # Act
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *targets],
        capture_output=True,
        text=True,
        check=False,
    )

    # Assert
    assert result.returncode == 0, result.stdout
    assert result.stdout == ""


def test_repo_scan_skips_the_dirty_fixture_but_scans_the_clean_one(tmp_path: Path) -> None:
    """From the repo root the dirty prose fixture is skipped on purpose; clean.md is scanned like any file."""
    # Arrange
    prose_dir = tmp_path / "tests" / "fixtures" / "prose"
    prose_dir.mkdir(parents=True)
    (prose_dir / "dirty.md").write_text("broken — line\n", encoding="utf-8")
    (prose_dir / "clean.md").write_text("This is robust.\n", encoding="utf-8")

    # Act
    findings = prose_scrub.scan_paths([tmp_path])

    # Assert
    assert [(Path(finding.path).name, finding.rule) for finding in findings] == [("clean.md", "banned-vocabulary")]


def test_dirty_fixture_still_fails_when_scanned_directly_or_as_its_own_root() -> None:
    """The skip is relative to the scan root: pointing the gate at the fixture or its directory still finds it."""
    # Act
    direct = prose_scrub.scan_paths([FIXTURE_DIR / "dirty.md"])
    as_root = prose_scrub.scan_paths([FIXTURE_DIR])

    # Assert
    assert [finding.rule for finding in direct] == ["em-dash", "banned-vocabulary"]
    assert [finding.rule for finding in as_root] == ["em-dash", "banned-vocabulary"]


def test_main_reports_file_line_rule_excerpt_and_exits_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """With no paths, main scans the given repo root and prints one 'path:line: rule: excerpt' line per finding."""
    # Arrange
    doc = tmp_path / "docs" / "page.md"
    doc.parent.mkdir()
    doc.write_text("fine line\nWe leverage this.\n", encoding="utf-8")

    # Act
    exit_code = prose_scrub.main([], repo_root=tmp_path)

    # Assert
    assert exit_code == 1
    assert capsys.readouterr().out == f"{doc}:2: banned-vocabulary: We leverage this.\n"


def test_main_exits_0_silently_on_a_clean_tree(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A clean tree exits 0 with no output."""
    # Arrange
    (tmp_path / "page.md").write_text("A plain line.\n", encoding="utf-8")

    # Act
    exit_code = prose_scrub.main([], repo_root=tmp_path)

    # Assert
    assert exit_code == 0
    assert capsys.readouterr().out == ""


def test_excerpt_is_truncated_to_eighty_characters() -> None:
    """The reported excerpt is the stripped line cut at 80 characters."""
    # Arrange
    text = "  " + "x" * 100 + " —\n"

    # Act
    findings = prose_scrub.scan_text(text, path="doc.md")

    # Assert
    assert findings[0].excerpt == "x" * 80
