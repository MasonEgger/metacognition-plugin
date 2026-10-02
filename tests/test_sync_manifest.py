# ABOUTME: Checks that each SKILL.md names exactly the references/ and scripts/ files its manifest slice ships.
# ABOUTME: The expected manifest is the spec G2 table, written out here so drift from the spec fails.
import re
from pathlib import Path

import pytest
from sync_skills import MANIFEST

SKILLS_ROOT = Path(__file__).resolve().parent.parent / "metacognition" / "skills"

# A references/ or scripts/ path counts only when it is not the tail of a longer path:
# the character before it must not be a word character, "/", ".", "-", or "~".
# That excludes "<target-skill>/references/x.md", "../references/x.md", "src/scripts/x.py".
NAMED_PATH = re.compile(r"(?<![\w/.~-])(references|scripts)/([A-Za-z0-9_-]+\.(?:md|py))")

EXPECTED: dict[str, dict[str, set[str]]] = {
    "design": {
        "references": {"settings.md", "extraction-theory.md", "interview-spec-format.md", "research-contract.md"},
        "scripts": {"yaml_subset.py", "resolve_config.py"},
    },
    "interview": {
        "references": {"settings.md", "extraction-theory.md", "interview-spec-format.md", "archive-format.md"},
        "scripts": {"yaml_subset.py", "resolve_config.py", "validate_artifacts.py"},
    },
    "compile": {
        "references": {
            "settings.md",
            "extraction-theory.md",
            "interview-spec-format.md",
            "archive-format.md",
            "profile-format.md",
        },
        "scripts": {"yaml_subset.py", "resolve_config.py", "validate_artifacts.py"},
    },
    "calibrate": {
        "references": {
            "settings.md",
            "extraction-theory.md",
            "interview-spec-format.md",
            "profile-format.md",
            "calibration-protocol.md",
        },
        "scripts": {"yaml_subset.py", "resolve_config.py", "validate_artifacts.py"},
    },
    "skillify": {
        "references": {
            "settings.md",
            "extraction-theory.md",
            "interview-spec-format.md",
            "archive-format.md",
            "profile-format.md",
            "skill-scaffold.md",
        },
        "scripts": {"yaml_subset.py", "resolve_config.py"},
    },
}


def named_paths(text: str) -> dict[str, set[str]]:
    found: dict[str, set[str]] = {"references": set(), "scripts": set()}
    for match in NAMED_PATH.finditer(text):
        found[match.group(1)].add(match.group(2))
    return found


def test_manifest_matches_the_spec_g2_table() -> None:
    actual = {skill: {kind: set(names) for kind, names in slice_.items()} for skill, slice_ in MANIFEST.items()}
    assert actual == EXPECTED


@pytest.mark.parametrize("skill", sorted(EXPECTED))
def test_skill_names_only_files_its_slice_ships(skill: str) -> None:
    named = named_paths((SKILLS_ROOT / skill / "SKILL.md").read_text())
    for kind in ("references", "scripts"):
        assert named[kind] - set(MANIFEST[skill][kind]) == set(), (
            f"{skill} SKILL.md names {kind}/ files its slice lacks"
        )


@pytest.mark.parametrize("skill", sorted(EXPECTED))
def test_slice_ships_only_files_skill_names(skill: str) -> None:
    named = named_paths((SKILLS_ROOT / skill / "SKILL.md").read_text())
    for kind in ("references", "scripts"):
        assert set(MANIFEST[skill][kind]) - named[kind] == set(), (
            f"{skill} slice ships {kind}/ files SKILL.md never names"
        )


def test_extraction_finds_a_bare_path() -> None:
    assert named_paths("Read `references/settings.md` first.") == {"references": {"settings.md"}, "scripts": set()}


def test_extraction_finds_a_script_command() -> None:
    assert named_paths("Run `python3 scripts/resolve_config.py --x`.")["scripts"] == {"resolve_config.py"}


def test_extraction_finds_both_halves_of_a_markdown_link() -> None:
    text = "[references/settings.md](references/settings.md) and [scripts/yaml_subset.py](scripts/yaml_subset.py)"
    assert named_paths(text) == {"references": {"settings.md"}, "scripts": {"yaml_subset.py"}}


def test_extraction_skips_a_target_skill_prefixed_path() -> None:
    text = "Write `<target-skill>/references/archive.md` and <target-skill>/scripts/x.py."
    assert named_paths(text) == {"references": set(), "scripts": set()}


def test_extraction_counts_the_bare_path_next_to_a_prefixed_one() -> None:
    text = "Copy <target-skill>/references/profile.md per references/skill-scaffold.md."
    assert named_paths(text) == {"references": {"skill-scaffold.md"}, "scripts": set()}


@pytest.mark.parametrize(
    "text",
    [
        "see ../references/settings.md",
        "see src/references/settings.md",
        "see ./scripts/resolve_config.py",
        "see myreferences/settings.md",
        "see my-scripts/resolve_config.py",
    ],
)
def test_extraction_skips_paths_that_are_part_of_a_longer_path(text: str) -> None:
    assert named_paths(text) == {"references": set(), "scripts": set()}


def test_extraction_ignores_directories_and_globs() -> None:
    assert named_paths("under references/ and scripts/ plus references/mode-*.md") == {
        "references": set(),
        "scripts": set(),
    }


def test_extraction_stops_at_sentence_punctuation() -> None:
    assert named_paths("Read references/settings.md.")["references"] == {"settings.md"}
