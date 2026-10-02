# ABOUTME: Behavior tests for scripts.resolve_config: five tiers, merging, loud errors, stderr echo.
# ABOUTME: Every test isolates HOME, XDG_CONFIG_HOME, and the working directory under tmp_path.
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.resolve_config import main

SCRIPT = Path(__file__).resolve().parent.parent / "src" / "scripts" / "resolve_config.py"


@pytest.fixture
def sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolate HOME, XDG_CONFIG_HOME, and the working directory; return the working directory."""
    home = tmp_path / "home"
    work = tmp_path / "work"
    home.mkdir()
    work.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.chdir(work)
    return tmp_path


def write_md(path: Path, frontmatter: str, body: str = "body text\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n{body}", encoding="utf-8")
    return path


def project_file(sandbox: Path) -> Path:
    return sandbox / "work" / ".claude" / "metacognition.local.md"


def claude_file(sandbox: Path) -> Path:
    return sandbox / "home" / ".claude" / "metacognition.local.md"


def xdg_default_file(sandbox: Path) -> Path:
    return sandbox / "home" / ".config" / "metacognition" / "config.yaml"


def write_yaml(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def run(capsys: pytest.CaptureFixture[str], *args: str) -> tuple[int, str, str]:
    code = main(list(args))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def resolve(capsys: pytest.CaptureFixture[str], *args: str) -> dict[str, dict[str, object]]:
    code, out, _ = run(capsys, *args)
    assert code == 0
    result: dict[str, dict[str, object]] = json.loads(out)
    return result


def test_all_defaults(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    result = resolve(capsys)
    assert result == {
        "extractions_root": {"value": str(sandbox / "work" / "extractions"), "source": "default"},
        "exemplar": {"value": None, "source": "default", "exists": False},
    }


def test_run_time_beats_every_file(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_md(project_file(sandbox), "extractions_root: from-project")
    write_md(claude_file(sandbox), "extractions_root: from-claude")
    write_yaml(xdg_default_file(sandbox), "extractions_root: from-xdg\n")
    result = resolve(capsys, "--set", "extractions_root=cli")
    assert result["extractions_root"] == {"value": str(sandbox / "work" / "cli"), "source": "run-time"}


def test_extractions_root_alias_is_run_time(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_md(project_file(sandbox), "extractions_root: from-project")
    result = resolve(capsys, "--extractions-root", "alias")
    assert result["extractions_root"] == {"value": str(sandbox / "work" / "alias"), "source": "run-time"}


def test_project_beats_user_files(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_md(project_file(sandbox), "extractions_root: from-project")
    write_md(claude_file(sandbox), "extractions_root: from-claude")
    write_yaml(xdg_default_file(sandbox), "extractions_root: from-xdg\n")
    result = resolve(capsys)
    assert result["extractions_root"] == {"value": str(sandbox / "work" / "from-project"), "source": "project"}


def test_user_claude_beats_xdg(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_md(claude_file(sandbox), "extractions_root: from-claude")
    write_yaml(xdg_default_file(sandbox), "extractions_root: from-xdg\n")
    result = resolve(capsys)
    assert result["extractions_root"] == {"value": str(sandbox / "work" / "from-claude"), "source": "user-claude"}


def test_xdg_wins_when_alone(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_yaml(xdg_default_file(sandbox), "extractions_root: from-xdg\n")
    result = resolve(capsys)
    assert result["extractions_root"] == {"value": str(sandbox / "work" / "from-xdg"), "source": "user-xdg"}


def test_xdg_config_home_set(
    sandbox: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    custom = sandbox / "custom-xdg"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(custom))
    write_yaml(custom / "metacognition" / "config.yaml", "extractions_root: from-custom\n")
    write_yaml(xdg_default_file(sandbox), "extractions_root: from-default-xdg\n")
    result = resolve(capsys)
    assert result["extractions_root"] == {"value": str(sandbox / "work" / "from-custom"), "source": "user-xdg"}


def test_xdg_config_home_unset_falls_back_to_home_config(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert "XDG_CONFIG_HOME" not in os.environ
    path = write_yaml(xdg_default_file(sandbox), "exemplar: skills/mine\n")
    code, out, err = run(capsys)
    assert code == 0
    assert json.loads(out)["exemplar"]["source"] == "user-xdg"
    assert f"Loaded config from: {path}" in err.splitlines()


def test_per_key_merge(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_md(project_file(sandbox), "extractions_root: proj-root")
    write_yaml(xdg_default_file(sandbox), "exemplar: xdg-skill\n")
    result = resolve(capsys)
    assert result["extractions_root"]["source"] == "project"
    assert result["exemplar"]["source"] == "user-xdg"
    assert result["exemplar"]["value"] == str(sandbox / "work" / "xdg-skill")


def test_relative_value_resolves_against_working_directory(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_md(project_file(sandbox), "extractions_root: sub/dir")
    result = resolve(capsys)
    assert result["extractions_root"]["value"] == str(sandbox / "work" / "sub" / "dir")


def test_absolute_value_is_kept(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = sandbox / "elsewhere"
    result = resolve(capsys, "--set", f"extractions_root={target}")
    assert result["extractions_root"]["value"] == str(target)


def test_tilde_expands_to_home(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    result = resolve(capsys, "--set", "extractions_root=~/stuff")
    assert result["extractions_root"]["value"] == str(sandbox / "home" / "stuff")


def test_project_file_is_not_found_by_upward_search(
    sandbox: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    write_md(sandbox / "work" / ".claude" / "metacognition.local.md", "extractions_root: parent")
    child = sandbox / "work" / "child"
    child.mkdir()
    monkeypatch.chdir(child)
    result = resolve(capsys)
    assert result["extractions_root"] == {"value": str(child / "extractions"), "source": "default"}


def test_unknown_key_is_loud(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write_md(project_file(sandbox), "extractions_root: ok\nfavorite_color: blue")
    code, out, err = run(capsys)
    assert code == 2
    assert out == ""
    assert len(err.strip().splitlines()) == 1
    assert str(path) in err
    assert "favorite_color" in err


def test_wrong_type_is_loud(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write_yaml(xdg_default_file(sandbox), "extractions_root: [a, b]\n")
    code, out, err = run(capsys)
    assert code == 2
    assert out == ""
    assert len(err.strip().splitlines()) == 1
    assert str(path) in err
    assert "extractions_root" in err


def test_integer_value_is_a_wrong_type(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write_md(claude_file(sandbox), "exemplar: 7")
    code, _, err = run(capsys)
    assert code == 2
    assert str(path) in err
    assert "exemplar" in err


def test_unparseable_file_is_loud(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write_md(project_file(sandbox), "extractions_root: &anchor x")
    code, out, err = run(capsys)
    assert code == 2
    assert out == ""
    assert len(err.strip().splitlines()) == 1
    assert str(path) in err


def test_error_in_a_lower_tier_still_fails_when_a_higher_tier_wins(
    sandbox: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write_yaml(xdg_default_file(sandbox), "nonsense: 1\n")
    code, _, err = run(capsys, "--set", "extractions_root=x")
    assert code == 2
    assert "nonsense" in err


def test_missing_files_are_silent(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, _, err = run(capsys)
    assert code == 0
    assert err == ""


def test_project_file_without_frontmatter_sets_nothing(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = project_file(sandbox)
    path.parent.mkdir(parents=True)
    path.write_text("just notes, no frontmatter\n", encoding="utf-8")
    code, out, err = run(capsys)
    assert code == 0
    assert json.loads(out)["extractions_root"]["source"] == "default"
    assert f"Loaded config from: {path}" in err.splitlines()


def test_body_of_local_md_is_ignored(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_md(project_file(sandbox), "extractions_root: real", body="exemplar: not-a-setting\nbogus: [\n")
    result = resolve(capsys)
    assert result["extractions_root"]["source"] == "project"
    assert result["exemplar"]["source"] == "default"


def test_exemplar_exists_true(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    skill = sandbox / "work" / "my-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("x", encoding="utf-8")
    result = resolve(capsys, "--set", "exemplar=my-skill")
    assert result["exemplar"] == {"value": str(skill), "source": "run-time", "exists": True}


def test_missing_exemplar_is_not_an_error(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = run(capsys, "--set", "exemplar=nowhere")
    assert code == 0
    assert json.loads(out)["exemplar"] == {
        "value": str(sandbox / "work" / "nowhere"),
        "source": "run-time",
        "exists": False,
    }


def test_loaded_lines_on_stderr_and_stdout_is_pure_json(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    proj = write_md(project_file(sandbox), "extractions_root: a")
    xdg = write_yaml(xdg_default_file(sandbox), "exemplar: b\n")
    code, out, err = run(capsys)
    assert code == 0
    assert err.splitlines() == [f"Loaded config from: {proj}", f"Loaded config from: {xdg}"]
    assert list(json.loads(out)) == ["extractions_root", "exemplar"]
    assert "Loaded config" not in out


def test_set_unknown_key_is_loud(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "--set", "bogus=1")
    assert code == 2
    assert out == ""
    assert len(err.strip().splitlines()) == 1
    assert "bogus" in err


def test_set_without_equals_is_loud(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "--set", "extractions_root")
    assert code == 2
    assert out == ""
    assert len(err.strip().splitlines()) == 1
    assert "extractions_root" in err


def test_set_empty_value_is_loud(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, _, err = run(capsys, "--set", "exemplar=")
    assert code == 2
    assert "exemplar" in err


def test_repeated_set_last_wins(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    result = resolve(capsys, "--set", "extractions_root=one", "--set", "extractions_root=two")
    assert result["extractions_root"]["value"] == str(sandbox / "work" / "two")


def test_all_five_tiers_overlap(
    sandbox: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    xdg_home = sandbox / "xdg"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_home))
    write_yaml(xdg_home / "metacognition" / "config.yaml", "extractions_root: xdg-root\nexemplar: xdg-skill\n")
    write_md(claude_file(sandbox), "extractions_root: claude-root\nexemplar: claude-skill")
    write_md(project_file(sandbox), "extractions_root: project-root")
    result = resolve(capsys, "--set", "exemplar=cli-skill")
    assert result["extractions_root"] == {"value": str(sandbox / "work" / "project-root"), "source": "project"}
    assert result["exemplar"]["source"] == "run-time"
    assert result["exemplar"]["value"] == str(sandbox / "work" / "cli-skill")
    # Drop the run-time exemplar: the next tier down (user-claude) must win it.
    result = resolve(capsys)
    assert result["exemplar"]["source"] == "user-claude"


def test_runs_as_a_direct_script_outside_the_repo(tmp_path: Path) -> None:
    home = tmp_path / "home"
    work = tmp_path / "work"
    home.mkdir()
    work.mkdir()
    env = {"HOME": str(home), "PATH": os.environ.get("PATH", "")}
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--set", "exemplar=x"],
        cwd=work,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["exemplar"]["source"] == "run-time"
    assert result["extractions_root"]["value"] == str(work.resolve() / "extractions")
