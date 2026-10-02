# ABOUTME: Doctrine guard over the shipped tree: no private tokens, no model-pinning keys, no "../" in skills.
# ABOUTME: Detection logic is tested on synthetic trees under tmp_path; the real-tree tests run the same scanners.
from pathlib import Path

import pytest
from tree_helpers import (
    EXEMPT_PATHS,
    PRIVATE_TOKENS,
    REPO_ROOT,
    SCOPE_DIRS,
    find_model_keys,
    find_parent_refs,
    find_tokens,
    scan_tree,
)

SPEC_TOKENS = (
    "Mason",
    "Arcadia",
    "claude-code-plugin-private",
    "CLAUDE_PLUGIN_ROOT",
    "CLAUDE_HELP",
    "Fable",
    "Wispr",
    "content-design",
    "vault-routing",
    "Hassid",
)


def write(root: Path, relative: str, text: str | bytes) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")
    return path


def test_token_list_is_the_spec_list() -> None:
    assert PRIVATE_TOKENS == SPEC_TOKENS


@pytest.mark.parametrize("token", SPEC_TOKENS)
def test_matcher_detects_each_token(token: str) -> None:
    assert find_tokens(f"first line\nsome {token} here\n") == [(2, token)]


def test_matcher_ignores_clean_text_and_is_case_sensitive() -> None:
    assert find_tokens("plain text\nmason arcadia fable\n") == []


def test_matcher_reports_every_token_on_every_line() -> None:
    assert find_tokens("Mason and Hassid\nok\nFable\n") == [(1, "Mason"), (1, "Hassid"), (3, "Fable")]


def test_scan_finds_planted_token_with_path_and_line(tmp_path: Path) -> None:
    write(tmp_path, "metacognition/skills/demo/SKILL.md", "---\nname: demo\n---\n\nfine\nsee Wispr notes\n")
    result = scan_tree(tmp_path)
    assert [(item.path.as_posix(), item.line, item.detail) for item in result.findings] == [
        ("metacognition/skills/demo/SKILL.md", 6, "Wispr")
    ]
    assert "metacognition/skills/demo/SKILL.md:6" in result.findings[0].render()


def test_scan_covers_all_five_scope_dirs_and_skips_missing_ones(tmp_path: Path) -> None:
    for scope in SCOPE_DIRS:
        write(tmp_path, f"{scope}/note.txt", "Arcadia\n")
    assert len(scan_tree(tmp_path).findings) == len(SCOPE_DIRS) == 5
    assert scan_tree(tmp_path / "empty").findings == []


def test_scan_ignores_files_outside_scope(tmp_path: Path) -> None:
    write(tmp_path, "README.md", "Mason\n")
    write(tmp_path, "tests/test_x.py", "Mason\n")
    write(tmp_path, "spec.md", "Hassid\n")
    assert scan_tree(tmp_path).findings == []


def test_scan_exempts_only_the_plugin_manifest(tmp_path: Path) -> None:
    assert frozenset({"metacognition/.claude-plugin/plugin.json"}) == EXEMPT_PATHS
    write(tmp_path, "metacognition/.claude-plugin/plugin.json", '{"author": "Mason"}\n')
    write(tmp_path, "metacognition/.claude-plugin/other.json", '{"author": "Mason"}\n')
    result = scan_tree(tmp_path)
    assert [item.path.as_posix() for item in result.findings] == ["metacognition/.claude-plugin/other.json"]


def test_scan_skips_caches_but_not_other_hidden_files(tmp_path: Path) -> None:
    write(tmp_path, "src/scripts/__pycache__/mod.cpython-311.pyc", b"\x00Mason")
    write(tmp_path, "src/.DS_Store", b"\x00Mason")
    write(tmp_path, "src/mod.pyc", b"Mason")
    write(tmp_path, "src/.hidden.md", "Mason\n")
    result = scan_tree(tmp_path)
    assert [item.path.as_posix() for item in result.findings] == ["src/.hidden.md"]


def test_scan_reports_undecodable_files_as_findings(tmp_path: Path) -> None:
    write(tmp_path, "docs/blob.bin", b"\xff\xfe\x00Mason")
    result = scan_tree(tmp_path)
    assert [(item.path.as_posix(), item.detail) for item in result.findings] == [("docs/blob.bin", "not valid UTF-8")]


def test_scan_counts_scanned_files(tmp_path: Path) -> None:
    write(tmp_path, "docs/a.md", "ok\n")
    write(tmp_path, "docs/sub/b.md", "ok\n")
    write(tmp_path, "docs/__pycache__/c.pyc", b"x")
    assert scan_tree(tmp_path).files_scanned == 2


def test_model_key_in_skill_frontmatter_is_flagged(tmp_path: Path) -> None:
    write(tmp_path, "metacognition/skills/a/SKILL.md", "---\nname: a\nmodel: sonnet\n---\nbody\n")
    write(tmp_path, "metacognition/skills/b/SKILL.md", "---\nname: b\ndisable-model-invocation: true\n---\nbody\n")
    write(tmp_path, "metacognition/skills/c/SKILL.md", "---\nname: c\n---\nbody\n")
    found = [(item.path.as_posix(), item.line, item.detail) for item in find_model_keys(tmp_path)]
    assert ("metacognition/skills/a/SKILL.md", 3, "model") in found
    assert ("metacognition/skills/b/SKILL.md", 3, "disable-model-invocation") in found
    assert not any("/c/" in entry[0] for entry in found)


def test_model_key_in_agent_is_flagged(tmp_path: Path) -> None:
    write(tmp_path, "metacognition/agents/x.md", "---\nname: x\nmodel: haiku\n---\nbody\n")
    found = find_model_keys(tmp_path)
    assert [(item.path.as_posix(), item.line, item.detail) for item in found] == [
        ("metacognition/agents/x.md", 3, "model")
    ]


def test_model_key_is_flagged_even_when_frontmatter_does_not_parse(tmp_path: Path) -> None:
    write(tmp_path, "metacognition/skills/a/SKILL.md", "---\nname: a\n  bad: [indent\nmodel: opus\nno closing fence\n")
    found = find_model_keys(tmp_path)
    assert [(item.line, item.detail) for item in found] == [(4, "model")]


def test_model_word_in_body_or_other_key_is_not_flagged(tmp_path: Path) -> None:
    write(tmp_path, "metacognition/skills/a/SKILL.md", "---\nname: a\nmodels: x\n---\nmodel: shown in a body example\n")
    assert find_model_keys(tmp_path) == []


def test_parent_ref_in_skill_body_is_flagged(tmp_path: Path) -> None:
    write(tmp_path, "metacognition/skills/a/SKILL.md", "---\nname: a\n---\nread ../other/x.md\n")
    found = find_parent_refs(tmp_path)
    assert [(item.path.as_posix(), item.line) for item in found] == [("metacognition/skills/a/SKILL.md", 4)]


def test_parent_ref_in_synced_skill_file_is_flagged(tmp_path: Path) -> None:
    write(tmp_path, "metacognition/skills/a/SKILL.md", "---\nname: a\n---\nclean\n")
    write(tmp_path, "metacognition/skills/a/references/r.md", "line\nsee ../../src/x\n")
    found = find_parent_refs(tmp_path)
    assert [(item.path.as_posix(), item.line) for item in found] == [("metacognition/skills/a/references/r.md", 2)]


def test_real_tree_has_no_private_tokens() -> None:
    result = scan_tree(REPO_ROOT)
    assert result.files_scanned > 0
    assert not result.findings, "private tokens found:\n" + "\n".join(item.render() for item in result.findings)


def test_real_tree_has_no_model_keys() -> None:
    found = find_model_keys(REPO_ROOT)
    assert not found, "model-pinning keys found:\n" + "\n".join(item.render() for item in found)


def test_real_tree_has_no_parent_refs_in_skills() -> None:
    found = find_parent_refs(REPO_ROOT)
    assert not found, 'skills must not contain "../":\n' + "\n".join(item.render() for item in found)
