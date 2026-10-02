# ABOUTME: Tests for tools/build_zips.py: the happy path, each refusal, exclusions, and the real tree.
# ABOUTME: Every refusal case builds a small bad tree under tmp_path and never touches the real dist/.
import json
import os
import zipfile
from collections.abc import Mapping
from pathlib import Path

import pytest
from build_zips import run
from sync_skills import MANIFEST

REPO_ROOT = Path(__file__).resolve().parent.parent

SMALL_MANIFEST: Mapping[str, Mapping[str, tuple[str, ...]]] = {
    "alpha": {"references": ("shared.md",), "scripts": ("tool.py",)},
    "beta": {"references": ("shared.md",), "scripts": ()},
}
VERSION = "0.4.2"
SOURCES = {"references/shared.md": "shared reference\n", "scripts/tool.py": "print('tool')\n"}


def skill_text(
    name: str,
    version: str = VERSION,
    description: str = "Use this skill to do the thing.",
    compatibility: str = "Runs anywhere.",
    drop: str | None = None,
    extra: str = "",
) -> str:
    """Return a SKILL.md with the four frontmatter keys, minus `drop`, plus the `extra` raw lines."""
    keys = {"name": name, "version": version, "description": description, "compatibility": compatibility}
    keys.pop(drop or "", None)
    lines = [f"{key}: {value}" for key, value in keys.items()]
    return "---\n" + "\n".join(lines) + "\n" + extra + "---\n\n# Body\n"


class Tree:
    """A small valid plugin tree, in sync with a small src tree, under one tmp_path."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.marketplace = root / "repo" / ".claude-plugin" / "marketplace.json"
        self.plugin = root / "repo" / "metacognition"
        self.src = root / "repo" / "src"
        self.out = root / "out"
        self.skills = self.plugin / "skills"
        self.marketplace.parent.mkdir(parents=True)
        self.marketplace.write_text(json.dumps({"metadata": {"version": VERSION}}))
        (self.plugin / ".claude-plugin").mkdir(parents=True)
        (self.plugin / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "metacognition", "version": VERSION})
        )
        (self.plugin / "agents").mkdir()
        (self.plugin / "agents" / "helper.md").write_text("agent\n")
        for relative, text in SOURCES.items():
            (self.src / relative).parent.mkdir(parents=True, exist_ok=True)
            (self.src / relative).write_text(text)
        for skill, slice_ in SMALL_MANIFEST.items():
            (self.skills / skill).mkdir(parents=True)
            (self.skills / skill / "SKILL.md").write_text(skill_text(skill))
            for kind, names in slice_.items():
                (self.skills / skill / kind).mkdir()
                for name in names:
                    (self.skills / skill / kind / name).write_text(SOURCES[f"{kind}/{name}"])

    def skill_md(self, skill: str = "alpha") -> Path:
        return self.skills / skill / "SKILL.md"

    def build(self) -> int:
        return run(self.marketplace, self.plugin, self.src, self.out, SMALL_MANIFEST)

    def zips(self) -> list[Path]:
        return sorted(self.out.glob("*.zip")) if self.out.exists() else []


@pytest.fixture
def tree(tmp_path: Path) -> Tree:
    return Tree(tmp_path)


def names_in(archive: Path) -> list[str]:
    with zipfile.ZipFile(archive) as opened:
        return opened.namelist()


def assert_refused(tree: Tree, capsys: pytest.CaptureFixture[str], *named: Path) -> str:
    """Build, then assert a non-zero exit, every named file on stderr, and no zip written."""
    code = tree.build()
    captured = capsys.readouterr()
    assert code != 0
    for path in named:
        assert str(path) in captured.err
    assert tree.zips() == []
    return captured.err


def test_happy_path_builds_one_rooted_sorted_archive(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    assert tree.build() == 0
    archive = tree.out / f"metacognition-{VERSION}.zip"
    assert tree.zips() == [archive]
    assert str(archive) in capsys.readouterr().out
    names = names_in(archive)
    assert {name.split("/")[0] for name in names} == {"metacognition"}
    assert "metacognition/.claude-plugin/plugin.json" in names
    assert "metacognition/skills/alpha/SKILL.md" in names
    assert "metacognition/skills/beta/SKILL.md" in names
    assert "metacognition/skills/alpha/scripts/tool.py" in names
    assert "metacognition/skills/beta/references/shared.md" in names
    assert "metacognition/agents/helper.md" in names
    assert names == sorted(names)


def test_two_builds_of_the_same_tree_are_byte_identical(tree: Tree) -> None:
    assert tree.build() == 0
    archive = tree.out / f"metacognition-{VERSION}.zip"
    first = archive.read_bytes()
    assert tree.build() == 0
    assert archive.read_bytes() == first


def test_skill_version_differs(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    tree.skill_md("beta").write_text(skill_text("beta", version="0.9.9"))
    err = assert_refused(tree, capsys, tree.skill_md("beta"))
    assert "0.9.9" in err
    assert VERSION in err


def test_plugin_json_version_differs(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    plugin_json = tree.plugin / ".claude-plugin" / "plugin.json"
    plugin_json.write_text(json.dumps({"name": "metacognition", "version": "1.0.0"}))
    err = assert_refused(tree, capsys, plugin_json)
    assert "1.0.0" in err


@pytest.mark.parametrize("body", ['{"metadata": {}}', '{"metadata": {"version": 3}}', "{}", "not json"])
def test_marketplace_version_missing_or_not_a_string(tree: Tree, capsys: pytest.CaptureFixture[str], body: str) -> None:
    tree.marketplace.write_text(body)
    assert_refused(tree, capsys, tree.marketplace)


def test_description_over_1024(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    tree.skill_md().write_text(skill_text("alpha", description="x" * 1025))
    assert_refused(tree, capsys, tree.skill_md())


def test_description_of_exactly_1024_is_allowed(tree: Tree) -> None:
    tree.skill_md().write_text(skill_text("alpha", description="x" * 1024))
    assert tree.build() == 0


@pytest.mark.parametrize("description", ["Use <this> skill.", "a > b", "less than < ok"])
def test_description_with_angle_bracket(tree: Tree, capsys: pytest.CaptureFixture[str], description: str) -> None:
    tree.skill_md().write_text(skill_text("alpha", description=f'"{description}"'))
    assert_refused(tree, capsys, tree.skill_md())


def test_compatibility_over_500(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    tree.skill_md().write_text(skill_text("alpha", compatibility="y" * 501))
    assert_refused(tree, capsys, tree.skill_md())


def test_compatibility_of_exactly_500_is_allowed(tree: Tree) -> None:
    tree.skill_md().write_text(skill_text("alpha", compatibility="y" * 500))
    assert tree.build() == 0


def test_extra_frontmatter_key(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    tree.skill_md().write_text(skill_text("alpha", extra="model: opus\n"))
    err = assert_refused(tree, capsys, tree.skill_md())
    assert "model" in err


@pytest.mark.parametrize("missing", ["name", "version", "description", "compatibility"])
def test_missing_required_key(tree: Tree, capsys: pytest.CaptureFixture[str], missing: str) -> None:
    tree.skill_md().write_text(skill_text("alpha", drop=missing))
    err = assert_refused(tree, capsys, tree.skill_md())
    assert missing in err


def test_unparseable_or_absent_frontmatter(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    tree.skill_md("alpha").write_text("---\nname: [unclosed\n---\n")
    tree.skill_md("beta").write_text("# no frontmatter at all\n")
    assert_refused(tree, capsys, tree.skill_md("alpha"), tree.skill_md("beta"))


def test_sync_drift_one_changed_byte(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    drifted = tree.skills / "alpha" / "scripts" / "tool.py"
    drifted.write_text("print('tool!')\n")
    assert_refused(tree, capsys, drifted)


def test_missing_manifest_source(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    (tree.src / "references" / "shared.md").unlink()
    err = assert_refused(tree, capsys)
    assert "shared.md" in err


def test_top_level_bin_directory(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    (tree.plugin / "bin").mkdir()
    (tree.plugin / "bin" / "run").write_text("#!/bin/sh\n")
    assert_refused(tree, capsys, tree.plugin / "bin")


def test_top_level_bin_file(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    (tree.plugin / "bin").write_text("not a directory\n")
    assert_refused(tree, capsys, tree.plugin / "bin")


def test_nested_bin_is_allowed(tree: Tree) -> None:
    (tree.skills / "alpha" / "bin").mkdir()
    (tree.skills / "alpha" / "bin" / "x").write_text("x\n")
    assert tree.build() == 0


def test_several_problems_are_all_reported_in_one_run(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    tree.skill_md("alpha").write_text(skill_text("alpha", version="2.0.0", description="x" * 2000))
    tree.skill_md("beta").write_text(skill_text("beta", compatibility="z" * 600, extra="color: red\n"))
    (tree.plugin / "bin").mkdir()
    (tree.skills / "beta" / "references" / "shared.md").write_text("drifted\n")
    err = assert_refused(
        tree, capsys, tree.skill_md("alpha"), tree.skill_md("beta"), tree.plugin / "bin", tree.skills / "beta"
    )
    assert len([line for line in err.splitlines() if line.strip()]) >= 6


def test_litter_is_excluded(tree: Tree) -> None:
    scripts = tree.skills / "alpha" / "scripts"
    (scripts / "__pycache__").mkdir()
    (scripts / "__pycache__" / "tool.cpython-311.pyc").write_bytes(b"\0")
    (scripts / "stray.pyc").write_bytes(b"\0")
    (tree.plugin / ".DS_Store").write_bytes(b"\0")
    (tree.skills / ".DS_Store").write_bytes(b"\0")
    assert tree.build() == 0
    names = names_in(tree.out / f"metacognition-{VERSION}.zip")
    assert not [name for name in names if "__pycache__" in name or name.endswith((".pyc", ".DS_Store"))]
    assert "metacognition/skills/alpha/scripts/tool.py" in names


def test_files_outside_the_plugin_directory_are_excluded(tree: Tree) -> None:
    (tree.plugin.parent / "README.md").write_text("outside\n")
    (tree.plugin.parent / "other").mkdir()
    (tree.plugin.parent / "other" / "x.txt").write_text("outside\n")
    assert tree.build() == 0
    names = names_in(tree.out / f"metacognition-{VERSION}.zip")
    assert all(name.startswith("metacognition/") for name in names)
    assert not [name for name in names if name.endswith(("README.md", "x.txt")) or "marketplace.json" in name]


@pytest.mark.parametrize("kind", ["file", "directory"])
def test_symlink_under_the_plugin_directory_is_refused(
    tree: Tree, capsys: pytest.CaptureFixture[str], kind: str
) -> None:
    outside = tree.root / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("secret\n")
    link = tree.plugin / "agents" / "link"
    try:
        os.symlink(outside if kind == "directory" else outside / "secret.txt", link)
    except OSError:
        pytest.skip("symlinks cannot be created here")
    assert_refused(tree, capsys, link)


def test_refusal_leaves_an_existing_zip_untouched(tree: Tree) -> None:
    assert tree.build() == 0
    archive = tree.out / f"metacognition-{VERSION}.zip"
    before = archive.read_bytes()
    tree.skill_md().write_text(skill_text("alpha", version="9.9.9"))
    assert tree.build() != 0
    assert archive.read_bytes() == before
    assert sorted(path.name for path in tree.out.iterdir()) == [archive.name]


def test_missing_plugin_directory_is_a_refusal(tree: Tree, capsys: pytest.CaptureFixture[str]) -> None:
    missing = tree.root / "nowhere"
    code = run(tree.marketplace, missing, tree.src, tree.out, SMALL_MANIFEST)
    assert code != 0
    assert str(missing) in capsys.readouterr().err


def test_real_tree_is_packageable(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "dist"
    code = run(
        REPO_ROOT / ".claude-plugin" / "marketplace.json",
        REPO_ROOT / "metacognition",
        REPO_ROOT / "src",
        out,
        MANIFEST,
    )
    assert code == 0, capsys.readouterr().err
    (archive,) = out.glob("metacognition-*.zip")
    names = names_in(archive)
    assert {name.split("/")[0] for name in names} == {"metacognition"}
    skill_files = [name for name in names if name.endswith("/SKILL.md")]
    assert len(skill_files) == 5
    assert "metacognition/.claude-plugin/plugin.json" in names
    assert any(name.startswith("metacognition/agents/") and name.endswith(".md") for name in names)
