# ABOUTME: Parity test between scripts.yaml_subset and PyYAML over every fixture's frontmatter.
# ABOUTME: Guards the shipped parser against drifting from what PyYAML reads.
from pathlib import Path

import pytest
import yaml

from scripts.yaml_subset import YamlSubsetError, extract_frontmatter, parse

FIXTURES = Path(__file__).resolve().parent / "fixtures"
BAD_YAML = FIXTURES / "extractions-bad" / "bad-yaml" / "archive.md"


def _withextract_frontmatter() -> list[Path]:
    return sorted(
        path
        for path in FIXTURES.rglob("*.md")
        if path != BAD_YAML and extract_frontmatter(path.read_text(encoding="utf-8")) is not None
    )


def _assert_same(actual: object, expected: object, where: str) -> None:
    """Assert equal values AND equal types at every level, so True never matches 1."""
    assert type(actual) is type(expected), f"{where}: {type(actual)} != {type(expected)}"
    if isinstance(expected, dict):
        assert isinstance(actual, dict)
        assert list(actual) == list(expected), where
        for key in expected:
            _assert_same(actual[key], expected[key], f"{where}.{key}")
    elif isinstance(expected, list):
        assert isinstance(actual, list)
        assert len(actual) == len(expected), where
        for position, item in enumerate(expected):
            _assert_same(actual[position], item, f"{where}[{position}]")
    else:
        assert actual == expected, where


def test_fixtures_with_frontmatter_are_collected() -> None:
    assert _withextract_frontmatter(), "no fixture frontmatter found; the parity test would pass vacuously"


@pytest.mark.parametrize("path", _withextract_frontmatter(), ids=lambda path: str(path.relative_to(FIXTURES)))
def test_parser_matches_pyyaml(path: Path) -> None:
    block = extract_frontmatter(path.read_text(encoding="utf-8"))
    assert block is not None
    _assert_same(parse(block), yaml.safe_load(block), path.name)


def test_bad_yaml_fails_in_both_parsers() -> None:
    block = extract_frontmatter(BAD_YAML.read_text(encoding="utf-8"))
    assert block is not None
    with pytest.raises(YamlSubsetError):
        parse(block)
    with pytest.raises(yaml.YAMLError):
        yaml.safe_load(block)
