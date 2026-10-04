# ABOUTME: Behavior tests for scripts.validate_artifacts, the extraction structure validator.
# ABOUTME: Covers the good fixtures, each seeded bad case, and tmp-dir cases for checks the fixtures do not isolate.
"""Tests for scripts.validate_artifacts."""

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.validate_artifacts import main

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "src" / "scripts" / "validate_artifacts.py"
GOOD_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "extractions" / "woodworking"
AUGMENT_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "extractions" / "woodworking-augment"
TRUNCATED_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "extractions" / "woodworking-truncated"
BAD_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "extractions-bad"


def _run_validator(extraction_dir: Path, capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    """Run main() against extraction_dir and return (exit code, stdout)."""
    code = main([str(extraction_dir)])
    return code, capsys.readouterr().out


def _checks(stdout: str) -> list[str]:
    """Return the check name of each finding line, in order."""
    return [line.split(": ")[1] for line in stdout.splitlines()]


def _profile_markdown_of_size(body_tokens: int) -> str:
    """Build a valid profile.md whose body is exactly body_tokens by the validator's count.

    The count is body characters divided by four, so the fingerprint section is padded until the
    body holds body_tokens * 4 characters, and the stored estimate is set to match.
    """
    fingerprint = "fingerprint text"
    markdown = _minimal_profile_markdown(token_estimate=body_tokens)
    body = markdown.split("---\n", 2)[2]
    padding = "x" * (body_tokens * 4 - len(body))
    return markdown.replace(fingerprint, fingerprint + padding)


def _minimal_profile_markdown(
    *,
    token_estimate: int = 1,
    include_do_not_infer: bool = True,
    why_line: str = "<why>the specific rule this demonstrates</why>",
) -> str:
    """Build a minimal but otherwise-valid profile.md for tmp-dir test cases.

    Every required section is present except do_not_infer when
    include_do_not_infer is False, and the golden example carries why_line
    verbatim, so a caller can omit it to test the golden-example check in
    isolation.
    """
    do_not_infer_block = "\n<do_not_infer>\nboundary text\n</do_not_infer>\n" if include_do_not_infer else "\n"
    return f"""---
domain: test
registers: [test]
consumer: test consumer
target_skill: null
version: 2026.01.01
token_estimate: {token_estimate}
calibrated: false
---

<profile>

<usage>
usage text
</usage>

<priority>
priority text
</priority>

<identity_context>
identity text
</identity_context>

<judgment_fingerprint>
fingerprint text
</judgment_fingerprint>

<domain_laws>
<law>Do: X. Avoid: Y. Example: Z.</law>
</domain_laws>

<communication_laws>
<law>communication text</law>
</communication_laws>

<hard_refusals>
<never>Never X. Bad: Y. Use: Z.</never>
</hard_refusals>

<taste_loves>
loves text
</taste_loves>

<taste_disgusts>
disgusts text
</taste_disgusts>

<phrase_bank>
<use>use text</use>
<avoid>avoid text</avoid>
</phrase_bank>

<signature_tells>
tells text
</signature_tells>

<decision_rules>
rules text
</decision_rules>

<productive_contradictions>
<tension>tension text. Preserve by: resolution.</tension>
</productive_contradictions>

<golden_examples>
<example>
<context>context text</context>
<bad>bad text</bad>
<good>good text</good>
{why_line}
</example>
</golden_examples>
{do_not_infer_block}
<calibration_state>
<rounds>1</rounds>
<last_date>2026-01-01</last_date>
<last_correction_count>0</last_correction_count>
</calibration_state>

<final_instruction>
final text
</final_instruction>

</profile>
"""


def _minimal_archive_markdown(*, stated_asked: int, actual_question_count: int) -> str:
    """Build a minimal archive.md whose frontmatter categories.asked can disagree with the body."""
    questions = "\n\n".join(
        f"### Q{question_index:02d} [cat-a] [test] [probe: forced-choice]\n"
        f"**Q:** question {question_index}\n"
        f"**A:** answer {question_index}"
        for question_index in range(1, actual_question_count + 1)
    )
    return f"""---
domain: test
registers: [test]
questions_asked: {actual_question_count}
categories:
  cat-a: {{asked: {stated_asked}, floor: 1, saturated: true}}
status: complete
---

# Archive: Test

## Questions

{questions}
"""


def test_nonexistent_directory_fails_loudly(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A nonexistent extraction directory exits non-zero naming the problem, not silently exit 0."""
    missing_dir = tmp_path / "does-not-exist"

    code, out = _run_validator(missing_dir, capsys)

    assert code != 0
    assert _checks(out) == ["extraction-dir-missing"]
    assert str(missing_dir) in out


def test_existing_directory_with_no_artifacts_fails_loudly(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """An extraction directory that exists but holds none of the four artifact files fails loudly."""
    empty_dir = tmp_path / "no-artifacts"
    empty_dir.mkdir()

    code, out = _run_validator(empty_dir, capsys)

    assert code != 0
    assert _checks(out) == ["extraction-dir-empty"]
    assert str(empty_dir) in out


@pytest.mark.parametrize("fixture", [GOOD_FIXTURE, AUGMENT_FIXTURE])
def test_good_fixtures_pass_with_no_findings(fixture: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The woodworking and woodworking-augment fixtures validate clean: exit 0, no findings on stdout."""
    code, out = _run_validator(fixture, capsys)

    assert code == 0
    assert out == ""


def test_truncated_fixture_flags_category_count_by_design(capsys: pytest.CaptureFixture[str]) -> None:
    """The woodworking-truncated fixture exits 1 with one archive-category-count finding, on purpose.

    The archive is an interview interrupted mid-question (status: in-progress), and the
    validator is status-agnostic, so the admired-makers count mismatch is reported.
    The interview stage's resume eval depends on this fixture's exact shape.
    """
    code, out = _run_validator(TRUNCATED_FIXTURE, capsys)

    assert code == 1
    assert _checks(out) == ["archive-category-count"]
    assert "admired-makers" in out


def test_bad_yaml_flags_frontmatter_parse(capsys: pytest.CaptureFixture[str]) -> None:
    """The bad-yaml fixture fails with a frontmatter-parse finding and no unrelated finding."""
    code, out = _run_validator(BAD_FIXTURES / "bad-yaml", capsys)

    assert code == 1
    assert set(_checks(out)) == {"frontmatter-parse"}
    assert "YAML failed to parse" in out


def test_numbering_gap_flags_archive_question_contiguity(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The numbering-gap fixture fails with an archive question-contiguity finding only."""
    code, out = _run_validator(BAD_FIXTURES / "numbering-gap", capsys)

    assert code == 1
    assert _checks(out) == ["archive-question-numbering"]


def test_oversize_profile_flags_token_ceiling(capsys: pytest.CaptureFixture[str]) -> None:
    """The oversize-profile fixture fails with a token-over-ceiling finding only."""
    code, out = _run_validator(BAD_FIXTURES / "oversize-profile", capsys)

    assert code == 1
    assert _checks(out) == ["profile-token-ceiling"]
    assert "10000 ceiling" in out


@pytest.mark.parametrize("body_tokens", [7500, 10000])
def test_profile_up_to_the_ceiling_passes(body_tokens: int, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A multi-register profile above the single-register target passes, up to and including the ceiling."""
    extraction_dir = tmp_path / "large-profile"
    extraction_dir.mkdir()
    (extraction_dir / "profile.md").write_text(_profile_markdown_of_size(body_tokens), encoding="utf-8")

    code, out = _run_validator(extraction_dir, capsys)

    assert code == 0, out


def test_profile_one_token_over_the_ceiling_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The first estimate above the ceiling is flagged, and nothing else is."""
    extraction_dir = tmp_path / "over-ceiling"
    extraction_dir.mkdir()
    (extraction_dir / "profile.md").write_text(_profile_markdown_of_size(10001), encoding="utf-8")

    code, out = _run_validator(extraction_dir, capsys)

    assert code == 1
    assert _checks(out) == ["profile-token-ceiling"]


def test_missing_section_flags_missing_required_xml_section(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The missing-section fixture fails with a missing-required-section finding for do_not_infer."""
    code, out = _run_validator(BAD_FIXTURES / "missing-section", capsys)

    assert code == 1
    assert _checks(out) == ["profile-missing-section"]
    assert "do_not_infer" in out


def test_noncontiguous_rounds_flags_calibration_round_contiguity(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The noncontiguous-rounds fixture fails with a calibration-round-contiguity finding only."""
    code, out = _run_validator(BAD_FIXTURES / "noncontiguous-rounds", capsys)

    assert code == 1
    assert _checks(out) == ["calibration-round-contiguity"]


def test_category_count_mismatch_flagged(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """An archive whose frontmatter categories.asked disagrees with the body count fails."""
    extraction_dir = tmp_path / "category-mismatch"
    extraction_dir.mkdir()
    (extraction_dir / "archive.md").write_text(
        _minimal_archive_markdown(stated_asked=5, actual_question_count=2), encoding="utf-8"
    )

    code, out = _run_validator(extraction_dir, capsys)

    assert code == 1
    assert _checks(out) == ["archive-category-count"]


def test_profile_token_estimate_recompute_flagged_under_ceiling(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A stale frontmatter token_estimate is flagged even when the profile is under the ceiling."""
    extraction_dir = tmp_path / "token-mismatch"
    extraction_dir.mkdir()
    (extraction_dir / "profile.md").write_text(_minimal_profile_markdown(token_estimate=1), encoding="utf-8")

    code, out = _run_validator(extraction_dir, capsys)

    assert code == 1
    assert "profile-token-estimate-mismatch" in out
    assert "profile-token-ceiling" not in out


def test_golden_example_missing_why_flagged(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A golden example missing its why child fails validation."""
    extraction_dir = tmp_path / "missing-why"
    extraction_dir.mkdir()
    (extraction_dir / "profile.md").write_text(_minimal_profile_markdown(why_line=""), encoding="utf-8")

    code, out = _run_validator(extraction_dir, capsys)

    assert code == 1
    assert "golden-example-incomplete" in out
    assert "<why>" in out


def test_profile_section_order_flagged(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Two sections swapped out of the required order yield a profile-section-order finding."""
    extraction_dir = tmp_path / "section-order"
    extraction_dir.mkdir()
    text = _minimal_profile_markdown()
    usage = "<usage>\nusage text\n</usage>"
    priority = "<priority>\npriority text\n</priority>"
    assert usage in text
    swapped = text.replace(usage, "@@").replace(priority, usage).replace("@@", priority)
    (extraction_dir / "profile.md").write_text(swapped, encoding="utf-8")

    code, out = _run_validator(extraction_dir, capsys)

    assert code == 1
    assert "profile-section-order" in _checks(out)


def test_multiple_findings_are_reported_in_file_then_check_order(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """One run reports every finding: archive first, then profile, then calibration."""
    extraction_dir = tmp_path / "multi"
    extraction_dir.mkdir()
    (extraction_dir / "archive.md").write_text(
        _minimal_archive_markdown(stated_asked=5, actual_question_count=2), encoding="utf-8"
    )
    (extraction_dir / "profile.md").write_text(
        _minimal_profile_markdown(token_estimate=1, include_do_not_infer=False),
        encoding="utf-8",
    )
    calibration = extraction_dir / "calibration"
    calibration.mkdir()
    (calibration / "round-02.md").write_text("---\nround: 2\n---\nbody\n", encoding="utf-8")

    code, out = _run_validator(extraction_dir, capsys)

    assert code == 1
    assert _checks(out) == [
        "archive-category-count",
        "profile-missing-section",
        "profile-token-estimate-mismatch",
        "calibration-round-contiguity",
    ]


def test_cli_subprocess_runs_from_another_directory(tmp_path: Path) -> None:
    """The file runs directly as a script (sibling import fallback) from any working directory."""
    good = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(GOOD_FIXTURE)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )
    bad = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(BAD_FIXTURES / "bad-yaml")],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    assert good.returncode == 0
    assert good.stdout == ""
    assert bad.returncode == 1
    assert "frontmatter-parse" in bad.stdout
