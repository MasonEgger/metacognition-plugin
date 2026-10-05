# ABOUTME: Holds the domain-research agent's output contract equal to src/references/research-contract.md.
# ABOUTME: Also guards the agent's frontmatter (no model pin) and its read-only tool set.
"""Tests for the domain-research agent contract."""

from pathlib import Path

from scripts.yaml_subset import extract_frontmatter, parse

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_PATH = REPO_ROOT / "metacognition" / "agents" / "domain-research.md"
CONTRACT_PATH = REPO_ROOT / "src" / "references" / "research-contract.md"
BEGIN_MARKER = "<!-- research-contract:begin -->"
END_MARKER = "<!-- research-contract:end -->"
READ_ONLY_TOOLS = {"WebFetch", "WebSearch", "Read", "Grep", "Glob"}
BLOCK_LINE_STARTS = ("DIMENSIONS", "SCHOOLS", "VOCABULARY", "ARTIFACT TYPES")
NO_RESULTS_LINE = "no relevant results"


def _normalize(text: str) -> str:
    """Strip trailing whitespace from every line and from the whole text."""
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def _agent_text() -> str:
    return AGENT_PATH.read_text(encoding="utf-8")


def _extract_block(text: str) -> str:
    """Return the text between the marker lines, failing clearly on a missing or repeated marker."""
    lines = [line.strip() for line in text.splitlines()]
    for marker in (BEGIN_MARKER, END_MARKER):
        count = lines.count(marker)
        assert count == 1, f"expected exactly one {marker} line in {AGENT_PATH.name}, found {count}"
    begin = lines.index(BEGIN_MARKER)
    end = lines.index(END_MARKER)
    assert begin < end, "the begin marker must come before the end marker"
    return "\n".join(text.splitlines()[begin + 1 : end])


def _contract_text() -> str:
    return CONTRACT_PATH.read_text(encoding="utf-8")


def _frontmatter() -> dict[str, object]:
    raw = extract_frontmatter(_agent_text())
    assert raw is not None, "the agent file has no frontmatter block"
    return dict(parse(raw))


def test_contract_block_equals_reference() -> None:
    block = _extract_block(_agent_text())
    assert _normalize(block) == _normalize(_contract_text())


def test_agent_has_no_model_pin() -> None:
    frontmatter = _frontmatter()
    assert "model" not in frontmatter
    assert "disable-model-invocation" not in frontmatter
    for line in _agent_text().splitlines():
        assert not line.startswith("model:"), "no model: line anywhere in the agent file"
        assert not line.startswith("disable-model-invocation:")


def test_agent_has_no_plugin_root_variable() -> None:
    assert "CLAUDE_PLUGIN_ROOT" not in _agent_text()


def test_agent_name_is_domain_research() -> None:
    assert _frontmatter()["name"] == "domain-research"


def test_contract_names_four_blocks_and_no_results_line() -> None:
    contract = _contract_text()
    contract_lines = [line.strip() for line in contract.splitlines()]
    for start in BLOCK_LINE_STARTS:
        assert any(line.startswith(start) for line in contract_lines), f"missing {start} block"
    assert f"`{NO_RESULTS_LINE}`" in contract


def test_agent_tools_are_read_only() -> None:
    tools = _frontmatter()["tools"]
    if isinstance(tools, str):
        declared = {tool.strip() for tool in tools.split(",") if tool.strip()}
    else:
        assert isinstance(tools, list), "tools must be a comma list or a sequence"
        declared = {str(tool) for tool in tools}
    assert declared, "the agent declares no tools"
    assert declared <= READ_ONLY_TOOLS, f"non-read-only tools: {sorted(declared - READ_ONLY_TOOLS)}"


def _practice_section() -> str:
    """Return the contract's practice lookup section, from its heading to the end of the text."""
    contract = _contract_text()
    marker = "\n## Practice Lookup\n"
    assert contract.count(marker) == 1, "the contract needs exactly one Practice Lookup heading"
    return contract[contract.index(marker) :]


def test_contract_names_both_request_shapes() -> None:
    contract = _contract_text()
    assert "## Request Shapes" in contract
    shapes_start = contract.index("## Request Shapes")
    shapes = contract[shapes_start : contract.index("\n## ", shapes_start + 1)]
    assert "domain survey" in shapes.lower()
    assert "practice lookup" in shapes.lower()
    assert "/metacognition:design" in shapes
    assert "/metacognition:interview" in shapes


def test_practice_lookup_states_input() -> None:
    section = _practice_section().lower()
    assert "one question about practice" in section
    assert "stated lean" in section


def test_practice_lookup_states_output_cap_and_source_links() -> None:
    section = _practice_section().lower()
    assert "at most five" in section
    assert "bottom line" in section
    assert "one sentence" in section
    assert "source link" in section


def test_practice_lookup_keeps_no_results_line_and_never_recommends() -> None:
    section = _practice_section()
    assert f"`{NO_RESULTS_LINE}`" in section
    assert "never recommends" in section
    assert "reports what sources say" in section


def test_practice_lookup_has_woodworking_example_with_links() -> None:
    section = _practice_section().lower()
    assert "example" in section
    assert "http" in section
    assert "wood" in section


def test_agent_mentions_interview_dispatch() -> None:
    frontmatter = _frontmatter()
    description = str(frontmatter["description"])
    assert "practice lookup" in description.lower()
    assert "/metacognition:interview" in description
    body = _agent_text().split(END_MARKER, 1)[1]
    assert "practice lookup" in body.lower()
