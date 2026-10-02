# ABOUTME: Drift guard for the generated per-skill copies of src/references and src/scripts.
# ABOUTME: Mutating tests run on a tmp_path tree; the real tree is only ever read.
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import sync_skills
from sync_skills import MANIFEST

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_SRC = REPO_ROOT / "src"
REAL_SKILLS = REPO_ROOT / "metacognition" / "skills"
TOOL = REPO_ROOT / "tools" / "sync_skills.py"


@pytest.fixture
def tree(tmp_path: Path) -> tuple[Path, Path]:
    """A tmp copy of the real src/ (shipping dirs only, plus dev litter) and an empty skills root."""
    src = tmp_path / "src"
    for kind in ("references", "scripts"):
        shutil.copytree(REAL_SRC / kind, src / kind, ignore=shutil.ignore_patterns("__pycache__"))
    skills = tmp_path / "skills"
    skills.mkdir()
    for skill in MANIFEST:
        (skills / skill).mkdir()
        (skills / skill / "SKILL.md").write_text(f"# {skill}\n")
    return src, skills


def snapshot(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


def run_main(src: Path, skills: Path, *extra: str) -> int:
    return sync_skills.main(["--src", str(src), "--skills", str(skills), *extra])


def test_real_tree_has_no_drift(capsys: pytest.CaptureFixture[str]) -> None:
    code = sync_skills.main(["--check"])
    out = capsys.readouterr().out
    assert code == 0, f"synced copies drifted from src/; run `just sync`:\n{out}"
    assert out == ""


def test_sync_makes_every_copy_byte_identical(tree: tuple[Path, Path]) -> None:
    src, skills = tree
    assert run_main(src, skills) == 0
    for skill, slice_ in MANIFEST.items():
        for kind, names in slice_.items():
            assert sorted(path.name for path in (skills / skill / kind).iterdir()) == sorted(names)
            for name in names:
                assert (skills / skill / kind / name).read_bytes() == (src / kind / name).read_bytes()


def test_sync_does_not_normalize_line_endings(tree: tuple[Path, Path]) -> None:
    src, skills = tree
    (src / "references" / "settings.md").write_bytes(b"a\r\nb\rc\n\xff\xfe")
    run_main(src, skills)
    assert (skills / "design" / "references" / "settings.md").read_bytes() == b"a\r\nb\rc\n\xff\xfe"


def test_sync_never_ships_dev_only_files(tree: tuple[Path, Path]) -> None:
    src, skills = tree
    (src / "scripts" / "__init__.py").write_text("")
    run_main(src, skills)
    assert not list(skills.rglob("__init__.py"))


def test_sync_leaves_skill_md_and_other_files_alone(tree: tuple[Path, Path]) -> None:
    src, skills = tree
    (skills / "design" / "notes.txt").write_text("keep")
    run_main(src, skills)
    assert (skills / "design" / "SKILL.md").read_text() == "# design\n"
    assert (skills / "design" / "notes.txt").read_text() == "keep"


def test_clean_check_is_silent_and_exits_zero(tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    src, skills = tree
    run_main(src, skills)
    capsys.readouterr()
    assert run_main(src, skills, "--check") == 0
    assert capsys.readouterr().out == ""


def test_one_byte_mutation_is_reported_as_differing(
    tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    src, skills = tree
    run_main(src, skills)
    target = skills / "interview" / "scripts" / "validate_artifacts.py"
    data = bytearray(target.read_bytes())
    data[0] ^= 1
    target.write_bytes(bytes(data))
    capsys.readouterr()
    assert run_main(src, skills, "--check") != 0
    lines = capsys.readouterr().out.splitlines()
    assert lines == ["differing: interview/scripts/validate_artifacts.py"]


def test_deleted_copy_is_reported_as_missing(tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    src, skills = tree
    run_main(src, skills)
    (skills / "compile" / "references" / "profile-format.md").unlink()
    capsys.readouterr()
    assert run_main(src, skills, "--check") != 0
    assert capsys.readouterr().out.splitlines() == ["missing: compile/references/profile-format.md"]


def test_unsynced_tree_reports_every_file_missing(tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    src, skills = tree
    assert run_main(src, skills, "--check") != 0
    lines = capsys.readouterr().out.splitlines()
    expected = sum(len(names) for slice_ in MANIFEST.values() for names in slice_.values())
    assert len(lines) == expected
    assert all(line.startswith("missing: ") for line in lines)


@pytest.mark.parametrize("kind", ["references", "scripts"])
def test_extra_file_is_reported_as_extra(
    tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str], kind: str
) -> None:
    src, skills = tree
    run_main(src, skills)
    (skills / "design" / kind / "stray.txt").write_text("x")
    capsys.readouterr()
    assert run_main(src, skills, "--check") != 0
    assert capsys.readouterr().out.splitlines() == [f"extra: design/{kind}/stray.txt"]


def test_file_from_another_skills_slice_is_extra(tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    src, skills = tree
    run_main(src, skills)
    shutil.copy(src / "references" / "skill-scaffold.md", skills / "design" / "references" / "skill-scaffold.md")
    capsys.readouterr()
    assert run_main(src, skills, "--check") != 0
    assert capsys.readouterr().out.splitlines() == ["extra: design/references/skill-scaffold.md"]


def test_check_reports_every_problem_one_per_line(tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    src, skills = tree
    run_main(src, skills)
    (skills / "design" / "references" / "settings.md").write_text("changed")
    (skills / "interview" / "references" / "archive-format.md").unlink()
    (skills / "skillify" / "scripts" / "stray.py").write_text("x")
    capsys.readouterr()
    assert run_main(src, skills, "--check") != 0
    assert sorted(capsys.readouterr().out.splitlines()) == [
        "differing: design/references/settings.md",
        "extra: skillify/scripts/stray.py",
        "missing: interview/references/archive-format.md",
    ]


def test_sync_removes_extra_files_and_directories(tree: tuple[Path, Path]) -> None:
    src, skills = tree
    run_main(src, skills)
    (skills / "design" / "references" / "stray.md").write_text("x")
    (skills / "design" / "scripts" / "nested").mkdir()
    (skills / "design" / "scripts" / "nested" / "deep.py").write_text("x")
    assert run_main(src, skills, "--check") != 0
    assert run_main(src, skills) == 0
    assert not (skills / "design" / "references" / "stray.md").exists()
    assert not (skills / "design" / "scripts" / "nested").exists()
    assert run_main(src, skills, "--check") == 0


def test_sync_repairs_a_mutated_copy(tree: tuple[Path, Path]) -> None:
    src, skills = tree
    run_main(src, skills)
    (skills / "design" / "references" / "settings.md").write_text("changed")
    run_main(src, skills)
    assert run_main(src, skills, "--check") == 0


def test_check_writes_nothing(tree: tuple[Path, Path]) -> None:
    src, skills = tree
    run_main(src, skills)
    (skills / "design" / "references" / "settings.md").write_text("changed")
    (skills / "design" / "references" / "stray.md").write_text("x")
    (skills / "compile" / "scripts" / "yaml_subset.py").unlink()
    before = snapshot(skills.parent)
    assert run_main(src, skills, "--check") != 0
    assert snapshot(skills.parent) == before


def test_check_writes_nothing_on_a_fresh_tree(tree: tuple[Path, Path]) -> None:
    src, skills = tree
    before = snapshot(skills.parent)
    assert run_main(src, skills, "--check") != 0
    assert snapshot(skills.parent) == before
    assert not (skills / "design" / "references").exists()


@pytest.mark.parametrize("check", [False, True])
def test_missing_source_file_is_a_loud_error(
    tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str], check: bool
) -> None:
    src, skills = tree
    (src / "references" / "research-contract.md").unlink()
    before = snapshot(skills.parent)
    code = run_main(src, skills, *(["--check"] if check else []))
    captured = capsys.readouterr()
    assert code != 0
    assert "research-contract.md" in captured.err
    assert snapshot(skills.parent) == before


def test_missing_source_raises_from_the_api(tree: tuple[Path, Path]) -> None:
    src, skills = tree
    (src / "scripts" / "yaml_subset.py").unlink()
    with pytest.raises(sync_skills.SourceMissingError, match="yaml_subset.py"):
        sync_skills.sync(src, skills)
    with pytest.raises(sync_skills.SourceMissingError, match="yaml_subset.py"):
        sync_skills.find_drift(src, skills)


def test_interpreter_litter_is_removed_by_sync_and_ignored_by_check(
    tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    src, skills = tree
    run_main(src, skills)
    scripts = skills / "interview" / "scripts"
    (scripts / "__pycache__").mkdir()
    (scripts / "__pycache__" / "resolve_config.cpython-311.pyc").write_bytes(b"\x00")
    (scripts / "stray.pyc").write_bytes(b"\x00")
    (skills / "interview" / "references" / ".DS_Store").write_bytes(b"\x00")
    capsys.readouterr()
    assert run_main(src, skills, "--check") == 0
    assert capsys.readouterr().out == ""
    assert run_main(src, skills) == 0
    assert sorted(path.name for path in scripts.iterdir()) == sorted(MANIFEST["interview"]["scripts"])
    assert not (skills / "interview" / "references" / ".DS_Store").exists()


def test_sync_never_copies_litter_from_src(tree: tuple[Path, Path]) -> None:
    src, skills = tree
    (src / "scripts" / "__pycache__").mkdir()
    (src / "scripts" / "__pycache__" / "yaml_subset.cpython-311.pyc").write_bytes(b"\x00")
    run_main(src, skills)
    assert not list(skills.rglob("*.pyc"))
    assert not list(skills.rglob("__pycache__"))


def test_command_line_entry_point(tree: tuple[Path, Path]) -> None:
    src, skills = tree
    base = [sys.executable, str(TOOL), "--src", str(src), "--skills", str(skills)]
    dirty = subprocess.run(base + ["--check"], capture_output=True, text=True, check=False)
    assert dirty.returncode == 1
    assert dirty.stdout.splitlines()[0].startswith("missing: ")
    assert subprocess.run(base, capture_output=True, text=True, check=False).returncode == 0
    assert subprocess.run(base + ["--check"], capture_output=True, text=True, check=False).returncode == 0


def symlink_or_skip(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("this platform cannot create symlinks")


def outside_dir(tmp_path: Path) -> Path:
    """A directory outside the skills root holding a sentinel file."""
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "sentinel.txt").write_bytes(b"do not touch\x00")
    (outside / "stray.md").write_text("also keep")
    return outside


def symlink_case(skills: Path, outside: Path, case: str) -> Path:
    """Replace one skill path with a symlink to outside; return the symlinked path."""
    if case == "skill":
        shutil.rmtree(skills / "interview")
        link = skills / "interview"
    else:
        link = skills / "interview" / case
    symlink_or_skip(link, outside)
    return link


@pytest.mark.parametrize("case", ["scripts", "references", "skill"])
def test_sync_refuses_a_symlinked_directory(
    tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str], tmp_path: Path, case: str
) -> None:
    src, skills = tree
    outside = outside_dir(tmp_path)
    link = symlink_case(skills, outside, case)
    before_outside = snapshot(outside)
    before_skills = snapshot(skills)
    code = run_main(src, skills)
    captured = capsys.readouterr()
    assert code == 2
    assert str(link) in captured.err
    assert snapshot(outside) == before_outside
    assert snapshot(skills) == before_skills


@pytest.mark.parametrize("case", ["scripts", "references", "skill"])
def test_check_reports_a_symlinked_directory_without_reading_through_it(
    tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str], tmp_path: Path, case: str
) -> None:
    src, skills = tree
    run_main(src, skills)
    outside = outside_dir(tmp_path)
    for kind in ("references", "scripts"):
        for name in MANIFEST["interview"][kind]:
            (outside / name).write_bytes((src / kind / name).read_bytes())
    if case != "skill":
        shutil.rmtree(skills / "interview" / case)
    link = symlink_case(skills, outside, case)
    before_outside = snapshot(outside)
    capsys.readouterr()
    code = run_main(src, skills, "--check")
    captured = capsys.readouterr()
    assert code == 2
    assert str(link) in captured.err
    assert captured.out == ""
    assert snapshot(outside) == before_outside


def test_refusal_happens_before_any_write(tree: tuple[Path, Path], tmp_path: Path) -> None:
    src, skills = tree
    run_main(src, skills)
    (skills / "design" / "references" / "settings.md").write_text("changed")
    (skills / "design" / "references" / "stray.md").write_text("x")
    outside = outside_dir(tmp_path)
    shutil.rmtree(skills / "skillify" / "scripts")
    symlink_or_skip(skills / "skillify" / "scripts", outside)
    before_outside = snapshot(outside)
    before_skills = snapshot(skills)
    assert run_main(src, skills) == 2
    assert snapshot(skills) == before_skills
    assert snapshot(outside) == before_outside


def file_link_or_skip(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("this platform cannot create symlinks")


def linked_entry(skills: Path, tmp_path: Path, kind: str, mode: str) -> tuple[Path, Path, str]:
    """Replace one design/<kind> entry with a symlink. Returns (link, outside target, entry label)."""
    in_slice = MANIFEST["design"][kind][0]
    name = in_slice if mode != "extra" else "stray.txt"
    link = skills / "design" / kind / name
    link.unlink(missing_ok=True)
    outside = tmp_path / "outside.bin"
    if mode == "dangling":
        outside = tmp_path / "nowhere.bin"
    elif mode == "identical":
        outside.write_bytes((REAL_SRC / kind / name).read_bytes())
    else:
        outside.write_bytes(b"outside bytes\x00")
    file_link_or_skip(link, outside)
    return link, outside, f"design/{kind}/{name}"


@pytest.mark.parametrize("kind", ["references", "scripts"])
@pytest.mark.parametrize("mode", ["different", "identical", "dangling"])
def test_sync_replaces_an_in_slice_file_symlink_without_writing_through_it(
    tree: tuple[Path, Path], tmp_path: Path, kind: str, mode: str
) -> None:
    src, skills = tree
    run_main(src, skills)
    link, outside, _ = linked_entry(skills, tmp_path, kind, mode)
    outside_before = outside.read_bytes() if outside.exists() else None
    assert run_main(src, skills) == 0
    assert not link.is_symlink()
    assert link.is_file()
    assert link.read_bytes() == (src / kind / link.name).read_bytes()
    assert (outside.read_bytes() if outside.exists() else None) == outside_before
    assert run_main(src, skills, "--check") == 0


@pytest.mark.parametrize("kind", ["references", "scripts"])
@pytest.mark.parametrize("mode", ["different", "identical", "dangling"])
def test_check_reports_an_in_slice_file_symlink_and_writes_nothing(
    tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str], tmp_path: Path, kind: str, mode: str
) -> None:
    src, skills = tree
    run_main(src, skills)
    link, outside, label = linked_entry(skills, tmp_path, kind, mode)
    before = snapshot(tmp_path) if mode != "dangling" else None
    capsys.readouterr()
    assert run_main(src, skills, "--check") == 1
    assert capsys.readouterr().out.splitlines() == [f"differing: {label}"]
    assert link.is_symlink()
    assert outside.exists() == (mode != "dangling")
    if before is not None:
        assert snapshot(tmp_path) == before


@pytest.mark.parametrize("kind", ["references", "scripts"])
def test_extra_file_symlink_is_removed_by_sync_and_reported_by_check(
    tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str], tmp_path: Path, kind: str
) -> None:
    src, skills = tree
    run_main(src, skills)
    link, outside, label = linked_entry(skills, tmp_path, kind, "extra")
    capsys.readouterr()
    assert run_main(src, skills, "--check") == 1
    assert capsys.readouterr().out.splitlines() == [f"extra: {label}"]
    assert run_main(src, skills) == 0
    assert not link.is_symlink()
    assert not link.exists()
    assert outside.read_bytes() == b"outside bytes\x00"
    assert run_main(src, skills, "--check") == 0


@pytest.mark.parametrize("kind", ["references", "scripts"])
@pytest.mark.parametrize("in_slice", [True, False])
def test_directory_symlink_inside_a_real_directory_is_removed_not_followed(
    tree: tuple[Path, Path], capsys: pytest.CaptureFixture[str], tmp_path: Path, kind: str, in_slice: bool
) -> None:
    src, skills = tree
    run_main(src, skills)
    outside = outside_dir(tmp_path)
    name = MANIFEST["design"][kind][0] if in_slice else "linked"
    link = skills / "design" / kind / name
    link.unlink(missing_ok=True)
    symlink_or_skip(link, outside)
    before_outside = snapshot(outside)
    capsys.readouterr()
    assert run_main(src, skills, "--check") == 1
    assert capsys.readouterr().out.splitlines() == [f"{'differing' if in_slice else 'extra'}: design/{kind}/{name}"]
    assert link.is_symlink()
    assert snapshot(outside) == before_outside
    assert run_main(src, skills) == 0
    assert not link.is_symlink()
    assert link.is_file() == in_slice
    assert snapshot(outside) == before_outside
    assert run_main(src, skills, "--check") == 0
