# ABOUTME: Checks every eval file parses and every tests/fixtures path an eval names exists on disk.
# ABOUTME: Also holds the sync stage out of evals/ and keeps evals out of the shipped metacognition/ bundle.
"""Eval integrity: every eval file parses, every fixture path it names exists, evals never ship in a bundle."""

import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parent.parent
EVALS = REPO / "evals"
BUNDLE = REPO / "metacognition"
STAGES = ("design", "interview", "compile", "calibrate", "skillify")

# A fixture path is a token that starts with tests/fixtures/ and is not itself the tail of a longer path
# (so "$SCRATCH/tests/fixtures/x" is a scratch path, not a committed fixture).
_FIXTURE_TOKEN = re.compile(r"(?<![\w/.$-])tests/fixtures/[\w./-]*")


def fixture_paths(text: str) -> list[str]:
    """Return every committed-fixture path named in text, with trailing sentence punctuation removed."""
    return [match.rstrip(".") for match in _FIXTURE_TOKEN.findall(text)]


def string_values(node: Any) -> Iterator[str]:
    """Yield every string value (never a key) in a parsed JSON document."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, list):
        for item in node:
            yield from string_values(item)
    elif isinstance(node, dict):
        for value in node.values():
            yield from string_values(value)


def load_stage(stage: str) -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads((EVALS / stage / "evals.json").read_text(encoding="utf-8"))
    return loaded


def all_eval_strings() -> list[str]:
    return [text for stage in STAGES for text in string_values(load_stage(stage))]


# The path-extraction rule, tested directly.


def test_extracts_a_path_followed_by_a_period() -> None:
    assert fixture_paths("Copy tests/fixtures/extractions/woodworking.") == ["tests/fixtures/extractions/woodworking"]


def test_extracts_a_path_followed_by_other_punctuation() -> None:
    text = "Use tests/fixtures/a/b.md, then tests/fixtures/c/d.md; also (tests/fixtures/e) and tests/fixtures/f/g.md's."
    assert fixture_paths(text) == [
        "tests/fixtures/a/b.md",
        "tests/fixtures/c/d.md",
        "tests/fixtures/e",
        "tests/fixtures/f/g.md",
    ]


def test_extracts_paths_inside_a_shell_command() -> None:
    command = 'cp -r tests/fixtures/extractions/woodworking "$SCRATCH/w" && git status --short tests/fixtures/'
    assert fixture_paths(command) == ["tests/fixtures/extractions/woodworking", "tests/fixtures/"]


def test_extracts_a_path_inside_quotes() -> None:
    assert fixture_paths("cat 'tests/fixtures/x/y.md' \"tests/fixtures/z.md\"") == [
        "tests/fixtures/x/y.md",
        "tests/fixtures/z.md",
    ]


def test_ignores_paths_under_a_scratch_variable() -> None:
    assert fixture_paths('"$SCRATCH/tests/fixtures/x" and "$PLUGINS/tests/fixtures/y"') == []


def test_ignores_text_with_no_fixture_path() -> None:
    assert fixture_paths("nothing to see in src/tests or fixtures/tests/") == []


def test_string_values_skips_keys_and_walks_nesting() -> None:
    doc = {"tests/fixtures/key": ["a", {"b": "c"}], "n": 3}
    assert sorted(string_values(doc)) == ["a", "c"]


# The shipped eval files.


def test_exactly_the_five_stages_have_evals() -> None:
    present = {path.name for path in EVALS.iterdir() if path.is_dir()}
    assert present == set(STAGES)


@pytest.mark.parametrize("stage", STAGES)
def test_eval_file_parses_and_each_eval_is_usable(stage: str) -> None:
    data = load_stage(stage)
    evals = data["evals"]
    assert isinstance(evals, list)
    assert evals, f"{stage} has no evals"
    ids = [entry["id"] for entry in evals]
    assert len(ids) == len(set(ids)), f"{stage} repeats an eval id"
    for entry in evals:
        prompt = entry["prompt"]
        assert isinstance(prompt, str)
        assert prompt.strip(), f"{stage} eval {entry['id']} has an empty prompt"


def test_every_named_fixture_path_exists() -> None:
    missing = sorted(
        {path for text in all_eval_strings() for path in fixture_paths(text) if not (REPO / path).exists()}
    )
    assert missing == []


def test_the_evals_name_at_least_one_fixture_path() -> None:
    assert any(fixture_paths(text) for text in all_eval_strings())


def test_readme_exists() -> None:
    assert (EVALS / "README.md").is_file()


def test_no_sync_stage_evals() -> None:
    assert not (EVALS / "sync").exists()
    offenders = [text for text in all_eval_strings() if re.search(r"\bsync\b", text, re.IGNORECASE)]
    assert offenders == []


def test_evals_never_ship_inside_the_bundle() -> None:
    shipped = sorted(str(path.relative_to(REPO)) for path in BUNDLE.rglob("*") if path.name.startswith("evals"))
    assert shipped == []
