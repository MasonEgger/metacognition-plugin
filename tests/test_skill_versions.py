# ABOUTME: Pins version presence, shape, and uniformity across the skills, both manifests, and pyproject.toml.
# ABOUTME: Shape is SemVer 0.x during beta; the pattern in tree_helpers flips to CalVer at 1.0.
import json
import re
import tomllib
from pathlib import Path

import pytest
from tree_helpers import REPO_ROOT, collect_versions, is_active_version_shape, snippet_section


@pytest.mark.parametrize("good", ["0.1.0", "0.0.0", "0.12.345"])
def test_shape_accepts_beta_semver(good: str) -> None:
    assert is_active_version_shape(good)


@pytest.mark.parametrize("bad", ["1.0.0", "0.1", "0.1.0-beta", "2026.10.01", "v0.1.0", "", "0.1.0\n", "0.1.0.1"])
def test_shape_rejects_everything_else(bad: str) -> None:
    assert not is_active_version_shape(bad)


def test_collect_versions_reads_all_three_sources(tmp_path: Path) -> None:
    skill = tmp_path / "metacognition" / "skills" / "a"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: a\nversion: 0.1.0\n---\nbody\n", encoding="utf-8")
    (tmp_path / "metacognition" / ".claude-plugin").mkdir(parents=True)
    (tmp_path / "metacognition" / ".claude-plugin" / "plugin.json").write_text('{"version": "0.2.0"}', encoding="utf-8")
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps({"metadata": {"version": "0.3.0"}, "plugins": [{"name": "m", "version": "0.4.0"}]}), encoding="utf-8"
    )
    assert collect_versions(tmp_path) == {
        "metacognition/skills/a/SKILL.md": "0.1.0",
        "metacognition/.claude-plugin/plugin.json": "0.2.0",
        ".claude-plugin/marketplace.json (metadata.version)": "0.3.0",
        ".claude-plugin/marketplace.json (plugins[0].version)": "0.4.0",
    }


def test_collect_versions_records_missing_version_as_none(tmp_path: Path) -> None:
    skill = tmp_path / "metacognition" / "skills" / "a"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: a\n---\nbody\n", encoding="utf-8")
    assert collect_versions(tmp_path) == {
        "metacognition/skills/a/SKILL.md": None,
        "metacognition/.claude-plugin/plugin.json": None,
        ".claude-plugin/marketplace.json (metadata.version)": None,
    }


def test_at_least_five_skills_are_found() -> None:
    skills = [source for source in collect_versions(REPO_ROOT) if source.endswith("/SKILL.md")]
    assert len(skills) >= 5


def test_every_source_has_a_string_version() -> None:
    missing = [source for source, value in collect_versions(REPO_ROOT).items() if not isinstance(value, str)]
    assert not missing, f"no string version in: {missing}"


def test_every_version_has_the_active_shape() -> None:
    bad = {
        source: value
        for source, value in collect_versions(REPO_ROOT).items()
        if not (isinstance(value, str) and is_active_version_shape(value))
    }
    assert not bad, f"versions with the wrong shape: {bad}"


def test_versions_are_uniform() -> None:
    versions = collect_versions(REPO_ROOT)
    assert len(set(versions.values())) == 1, f"versions differ: {versions}"


def test_snippet_section_returns_the_text_between_its_markers() -> None:
    text = "intro\n<!-- --8<-- [start:beta] -->\nline one\nline two\n<!-- --8<-- [end:beta] -->\noutro\n"
    assert snippet_section(text, "beta") == "line one\nline two\n"


def test_snippet_section_is_none_when_a_marker_is_missing() -> None:
    assert snippet_section("no markers here\n", "beta") is None
    assert snippet_section("<!-- --8<-- [start:beta] -->\nunclosed\n", "beta") is None
    assert snippet_section("<!-- --8<-- [start:other] -->\nx\n<!-- --8<-- [end:other] -->\n", "beta") is None


def test_readme_beta_notice_names_the_manifest_version() -> None:
    """The docs home page shows this README section, so a version change must reach it."""
    version = collect_versions(REPO_ROOT)[".claude-plugin/marketplace.json (metadata.version)"]
    notice = snippet_section((REPO_ROOT / "README.md").read_text(encoding="utf-8"), "beta")
    assert notice is not None, "README.md has no beta section between snippet markers"
    assert re.search(rf"version {re.escape(str(version))}(?!\d)", notice), (
        f"README.md beta notice does not name version {version}"
    )


def test_pyproject_version_matches_the_manifest_version() -> None:
    """The development project carries the plugin's version, so one number describes the whole repo."""
    version = collect_versions(REPO_ROOT)[".claude-plugin/marketplace.json (metadata.version)"]
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["version"] == version
