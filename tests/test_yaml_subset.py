# ABOUTME: Behavior tests for scripts.yaml_subset using inline string inputs.
# ABOUTME: Covers the supported subset, rejected constructs, and edge cases.
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.yaml_subset import YamlSubsetError, parse

SCRIPT = Path(__file__).resolve().parent.parent / "src" / "scripts" / "yaml_subset.py"


def test_bare_pair() -> None:
    assert parse("key: value") == {"key": "value"}


def test_quoted_strings_strip_quotes() -> None:
    assert parse("a: \"double\"\nb: 'single'") == {"a": "double", "b": "single"}


def test_quoted_string_keeps_hash_and_colon() -> None:
    assert parse('a: "x # y: z"') == {"a": "x # y: z"}


def test_integer_is_int() -> None:
    result = parse("n: 42\nm: -3")
    assert result == {"n": 42, "m": -3}
    assert type(result["n"]) is int


def test_quoted_integer_stays_string() -> None:
    assert parse("n: '42'") == {"n": "42"}


def test_true_false_null() -> None:
    assert parse("a: true\nb: false\nc: null") == {"a": True, "b": False, "c": None}


def test_inline_list() -> None:
    assert parse("k: [a, b]") == {"k": ["a", "b"]}


def test_inline_map() -> None:
    assert parse("m: {k: v}") == {"m": {"k": "v"}}


def test_nested_inline_map_in_inline_list() -> None:
    assert parse("c: [{a: 1, b: true}, {a: 2, b: [x, y]}]") == {"c": [{"a": 1, "b": True}, {"a": 2, "b": ["x", "y"]}]}


def test_archive_categories_shape() -> None:
    text = (
        "categories:\n"
        "  joinery: {asked: 3, floor: 2, saturated: true}\n"
        "  safety: {asked: 0, floor: 1, saturated: false}\n"
    )
    assert parse(text) == {
        "categories": {
            "joinery": {"asked": 3, "floor": 2, "saturated": True},
            "safety": {"asked": 0, "floor": 1, "saturated": False},
        }
    }


def test_empty_inline_collections() -> None:
    assert parse("a: []\nb: {}") == {"a": [], "b": {}}


def test_block_map_nesting() -> None:
    text = "outer:\n  inner:\n    leaf: 1\n  sibling: x\ntop: y\n"
    assert parse(text) == {"outer": {"inner": {"leaf": 1}, "sibling": "x"}, "top": "y"}


def test_key_with_no_value_is_null() -> None:
    assert parse("a:\nb: 1") == {"a": None, "b": 1}


def test_comments_ignored() -> None:
    text = "# leading\na: 1 # trailing\n  # indented comment\nb: 'x # kept'\n"
    assert parse(text) == {"a": 1, "b": "x # kept"}


def test_hash_without_space_is_part_of_value() -> None:
    assert parse("a: c#d") == {"a": "c#d"}


def test_leading_document_marker_allowed() -> None:
    assert parse("---\na: 1") == {"a": 1}


@pytest.mark.parametrize(
    ("text", "lineno"),
    [
        ("a: 1\nb: &anchor x", 2),
        ("a: 1\n\nb: !!str x", 3),
        ("a: 1\n---\nb: 2", 2),
        ("a: 1\n...\n", 2),
        ("a: 1\nb: |\n  text", 2),
        ("a: 1\nb: >\n  text", 2),
        ("a: *alias", 1),
        ("a: 1\nb:\n  - x", 3),
        ("a: 1\nb: 1.5", 2),
        ("a: 1\nb: True", 2),
        ("a: 1\nb: 2026-09-21", 2),
        ("a: 1\nb: 007", 2),
        ("a: 1\nb: [x, y", 2),
        ("a: 1\nb: {k v}", 2),
        ("a: 1\nb: 'open", 2),
        ("a: 1\nb: x: y", 2),
        ("a: 1\nno colon here", 2),
        ("a:\n\ttab: 1", 2),
        ("a: 1\n1: x", 2),
    ],
)
def test_unsupported_constructs_name_the_line(text: str, lineno: int) -> None:
    with pytest.raises(YamlSubsetError, match=rf"^line {lineno}:"):
        parse(text)


def test_error_is_a_value_error() -> None:
    with pytest.raises(ValueError, match="line 1"):
        parse("a: &x 1")


def test_empty_document() -> None:
    assert parse("") == {}
    assert parse("\n# only a comment\n\n") == {}


def test_duplicate_keys_raise() -> None:
    with pytest.raises(YamlSubsetError, match=r"^line 3: duplicate key 'a'"):
        parse("a: 1\nb: 2\na: 3")


def test_duplicate_keys_in_nested_block_raise() -> None:
    with pytest.raises(YamlSubsetError, match=r"^line 3: duplicate key 'x'"):
        parse("m:\n  x: 1\n  x: 2")


def test_duplicate_keys_in_inline_map_raise() -> None:
    with pytest.raises(YamlSubsetError, match=r"^line 1: duplicate key 'k'"):
        parse("m: {k: 1, k: 2}")


def test_deeper_indent_without_parent_raises() -> None:
    with pytest.raises(YamlSubsetError, match=r"^line 3:"):
        parse("a:\n  b: 1\n   c: 2")


def test_indent_under_scalar_value_raises() -> None:
    with pytest.raises(YamlSubsetError, match=r"^line 2:"):
        parse("a: 1\n  b: 2")


def test_dedent_to_unopened_level_raises() -> None:
    with pytest.raises(YamlSubsetError, match=r"^line 4:"):
        parse("a:\n    b:\n        c: 1\n  d: 2")


def test_indented_first_line_raises() -> None:
    with pytest.raises(YamlSubsetError, match=r"^line 1:"):
        parse("  a: 1")


def test_cli_prints_json(tmp_path: Path) -> None:
    source = tmp_path / "in.yaml"
    source.write_text("a: 1\nb: [x, y]\n", encoding="utf-8")
    done = subprocess.run([sys.executable, str(SCRIPT), str(source)], capture_output=True, text=True, check=False)
    assert done.returncode == 0
    assert '"a": 1' in done.stdout


def test_cli_reports_line_on_error(tmp_path: Path) -> None:
    source = tmp_path / "bad.yaml"
    source.write_text("a: 1\nb: &x 2\n", encoding="utf-8")
    done = subprocess.run([sys.executable, str(SCRIPT), str(source)], capture_output=True, text=True, check=False)
    assert done.returncode == 2
    assert "line 2:" in done.stderr


def test_single_quote_doubling_keeps_hash_inside_string() -> None:
    assert parse("a: 'it''s # x'") == {"a": "it's # x"}


def test_single_quote_doubling_then_trailing_comment() -> None:
    assert parse("a: 'it''s # x'  # note") == {"a": "it's # x"}


def test_single_quote_doubled_quote_at_end_of_string() -> None:
    assert parse("a: 'ends with '''") == {"a": "ends with '"}
    assert parse("a: 'ends with '''  # note") == {"a": "ends with '"}


def test_double_quote_escaped_quote_keeps_hash_inside_string() -> None:
    assert parse('a: "say \\"hi\\" # x"') == {"a": 'say "hi" # x'}


def test_double_quote_escaped_quote_then_trailing_comment() -> None:
    assert parse('a: "say \\"hi\\" # x" # note') == {"a": 'say "hi" # x'}
