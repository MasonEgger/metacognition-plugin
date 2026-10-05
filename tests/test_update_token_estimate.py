# ABOUTME: Behavior tests for scripts.update_token_estimate, the profile token_estimate rewriter.
# ABOUTME: Profiles are built under tmp_path; the committed fixtures are only read, never written.
"""Tests for scripts.update_token_estimate."""

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.update_token_estimate import main
from scripts.validate_artifacts import estimate_tokens

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "src" / "scripts" / "update_token_estimate.py"
EXTRACTIONS = REPO_ROOT / "tests" / "fixtures" / "extractions"


def _profile(directory: Path, body: str, stored: int | str | None, name: str = "profile.md") -> Path:
    """Write a profile with the given body and stored estimate (None omits the line) and return its path."""
    estimate_line = "" if stored is None else f"token_estimate: {stored}\n"
    path = directory / name
    path.write_bytes(f"---\ndomain: woodworking\n{estimate_line}calibrated: false\n---\n{body}".encode())
    return path


def test_arithmetic_counts_characters_with_integer_division() -> None:
    assert estimate_tokens("a" * 4000) == 1000
    assert estimate_tokens("a" * 4003) == 1000
    assert estimate_tokens("é" * 4000) == 1000
    assert estimate_tokens("é" * 3998 + "中") == 999


def test_current_profile_is_reported_and_untouched(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _profile(tmp_path, "é" * 4000, 1000)
    before = path.read_bytes()
    assert main([str(path)]) == 0
    assert "current" in capsys.readouterr().out
    assert path.read_bytes() == before


def test_stale_profile_is_rewritten(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _profile(tmp_path, "é" * 4003, 7)
    before = path.read_bytes()
    assert main([str(path)]) == 0
    output = capsys.readouterr().out
    assert "7" in output
    assert "1000" in output
    assert path.read_bytes() == before.replace(b"token_estimate: 7\n", b"token_estimate: 1000\n")
    assert path.read_bytes() != before


def test_body_line_with_the_key_is_not_touched(tmp_path: Path) -> None:
    body = "token_estimate: 5\n" + "a" * 4000
    path = _profile(tmp_path, body, 3)
    assert main([str(path)]) == 0
    text = path.read_text(encoding="utf-8")
    assert "\ntoken_estimate: 5\n" in text
    assert text.count("token_estimate: 1004\n") == 1


@pytest.mark.parametrize("flag", ["--check", "-c"])
def test_check_reports_stale_and_writes_nothing(tmp_path: Path, capsys: pytest.CaptureFixture[str], flag: str) -> None:
    path = _profile(tmp_path, "a" * 4000, 5)
    before = path.read_bytes()
    assert main([flag, str(path)]) == 1
    assert str(path) in capsys.readouterr().out
    assert path.read_bytes() == before


def test_missing_path_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "absent.md"
    assert main([str(path)]) == 2
    lines = capsys.readouterr().err.strip().splitlines()
    assert len(lines) == 1
    assert str(path) in lines[0]


@pytest.mark.parametrize(
    "content",
    [
        b"no frontmatter here\n",
        b"---\ndomain: x\ntoken_estimate: 1\n",
        b"---\ndomain: x\n---\nbody\n",
    ],
    ids=["no-frontmatter", "no-closing-delimiter", "no-estimate-line"],
)
def test_malformed_profile_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str], content: bytes) -> None:
    path = tmp_path / "profile.md"
    path.write_bytes(content)
    assert main([str(path)]) == 2
    lines = capsys.readouterr().err.strip().splitlines()
    assert len(lines) == 1
    assert str(path) in lines[0]
    assert path.read_bytes() == content


def test_paths_are_independent_and_exit_two_outranks_one(tmp_path: Path) -> None:
    current = _profile(tmp_path, "a" * 400, 100, "current.md")
    stale = _profile(tmp_path, "a" * 400, 1, "stale.md")
    broken = tmp_path / "broken.md"
    broken.write_bytes(b"plain\n")
    stale_before = stale.read_bytes()
    assert main(["--check", str(current), str(stale), str(broken)]) == 2
    assert stale.read_bytes() == stale_before
    assert main([str(current), str(stale), str(broken)]) == 2
    assert b"token_estimate: 100\n" in stale.read_bytes()


def test_validator_agrees_after_rewrite(tmp_path: Path) -> None:
    from scripts.validate_artifacts import parse_frontmatter

    path = _profile(tmp_path, "a" * 1234, 9)
    assert main([str(path)]) == 0
    frontmatter, body, findings = parse_frontmatter(path)
    assert findings == []
    assert frontmatter is not None
    assert frontmatter["token_estimate"] == estimate_tokens(body) == 308


def test_no_temporary_file_is_left(tmp_path: Path) -> None:
    path = _profile(tmp_path, "a" * 400, 1)
    assert main([str(path)]) == 0
    assert [entry.name for entry in tmp_path.iterdir()] == ["profile.md"]


def test_write_failure_exits_two_and_leaves_original(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    import os

    path = _profile(tmp_path, "a" * 400, 1)
    before = path.read_bytes()

    def fail(source: object, destination: object) -> None:
        raise PermissionError("denied")

    monkeypatch.setattr(os, "replace", fail)
    assert main([str(path)]) == 2
    assert len(capsys.readouterr().err.strip().splitlines()) == 1
    assert path.read_bytes() == before
    assert [entry.name for entry in tmp_path.iterdir()] == ["profile.md"]


def test_every_good_fixture_profile_is_current() -> None:
    profiles = sorted(str(path) for path in EXTRACTIONS.glob("*/profile.md"))
    assert profiles
    assert main(["--check", *profiles]) == 0


def test_runs_as_a_script_from_another_directory(tmp_path: Path) -> None:
    path = _profile(tmp_path, "a" * 400, 1)
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert b"token_estimate: 100\n" in path.read_bytes()


def _mismatches(directory: Path) -> list[str]:
    """Return the validator's profile-token-estimate-mismatch findings for the profile in directory."""
    from scripts.validate_artifacts import validate_extraction

    return [
        finding.message
        for finding in validate_extraction(directory)
        if finding.check == "profile-token-estimate-mismatch"
    ]


def _raw_profile(directory: Path, content: bytes) -> Path:
    path = directory / "profile.md"
    path.write_bytes(content)
    return path


_LF_FRONTMATTER = b"---\ndomain: woodworking\ntoken_estimate: 7\ncalibrated: false\n---\n"
_CRLF_FRONTMATTER = _LF_FRONTMATTER.replace(b"\n", b"\r\n")
_CRLF_BODY = (b"line one\r\n" * 300) + b"tail\r\n"
_LF_BODY = (b"line one\n" * 300) + b"tail\n"


def _assert_rewritten_like_validator(path: Path, before: bytes) -> None:
    """Assert exit 0, the validator is satisfied, and only the token_estimate line changed."""
    assert main([str(path)]) == 0
    assert _mismatches(path.parent) == []
    after = path.read_bytes()
    assert after != before
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    assert len(before_lines) == len(after_lines)
    changed = [index for index, pair in enumerate(zip(before_lines, after_lines, strict=True)) if pair[0] != pair[1]]
    assert len(changed) == 1
    old_line, new_line = before_lines[changed[0]], after_lines[changed[0]]
    assert old_line.lstrip(b"\xef\xbb\xbf").startswith(b"token_estimate: 7")
    ending = b"\r\n" if old_line.endswith(b"\r\n") else b"\n" if old_line.endswith(b"\n") else b""
    assert new_line.endswith(ending)
    assert new_line.startswith(b"token_estimate: ")


def test_stale_crlf_profile_matches_validator(tmp_path: Path) -> None:
    path = _raw_profile(tmp_path, _CRLF_FRONTMATTER + _CRLF_BODY)
    _assert_rewritten_like_validator(path, path.read_bytes())


def test_stale_lf_frontmatter_crlf_body_matches_validator(tmp_path: Path) -> None:
    path = _raw_profile(tmp_path, _LF_FRONTMATTER + _CRLF_BODY)
    _assert_rewritten_like_validator(path, path.read_bytes())


def test_stale_profile_with_byte_order_mark_matches_validator(tmp_path: Path) -> None:
    path = _raw_profile(tmp_path, b"\xef\xbb\xbf" + _LF_FRONTMATTER + _LF_BODY)
    before = path.read_bytes()
    assert main([str(path)]) == 0
    assert _mismatches(tmp_path) == []
    after = path.read_bytes()
    assert after.startswith(b"\xef\xbb\xbf---\n")
    assert after.replace(b"token_estimate: 676\n", b"token_estimate: 7\n") == before


def test_stale_profile_without_trailing_newline_matches_validator(tmp_path: Path) -> None:
    path = _raw_profile(tmp_path, _LF_FRONTMATTER + b"a" * 4001)
    before = path.read_bytes()
    assert main([str(path)]) == 0
    assert _mismatches(tmp_path) == []
    assert path.read_bytes() == before.replace(b"token_estimate: 7\n", b"token_estimate: 1000\n")


def test_current_crlf_profile_is_left_byte_identical(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from scripts.validate_artifacts import parse_frontmatter

    path = _raw_profile(tmp_path, _CRLF_FRONTMATTER + _CRLF_BODY)
    assert main([str(path)]) == 0
    capsys.readouterr()
    current = path.read_bytes()
    assert _mismatches(tmp_path) == []
    assert main([str(path)]) == 0
    assert "current" in capsys.readouterr().out
    assert path.read_bytes() == current
    assert parse_frontmatter(path)[0] is not None


def test_check_on_stale_crlf_profile_writes_nothing(tmp_path: Path) -> None:
    path = _raw_profile(tmp_path, _CRLF_FRONTMATTER + _CRLF_BODY)
    before = path.read_bytes()
    assert main(["--check", str(path)]) == 1
    assert path.read_bytes() == before
