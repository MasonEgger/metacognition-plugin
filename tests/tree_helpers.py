# ABOUTME: Shared helpers for the doctrine and version guard tests: a scoped file walker and scanners.
# ABOUTME: Every scanner takes a repo root so tests can plant violations under tmp_path, never in the real tree.
import json
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from scripts.yaml_subset import YamlMap, YamlSubsetError, extract_frontmatter, parse

REPO_ROOT = Path(__file__).resolve().parent.parent

# Spec Component I: the five directories the token guard scans, each only if it exists.
SCOPE_DIRS = ("metacognition", "src", "evals", "tests/fixtures", "docs")

# Spec Component I: "The README, LICENSE, manifests, and this spec are outside its scope, since they carry
# the author name and the credit line by design." Only the plugin manifest sits inside SCOPE_DIRS; the root
# marketplace.json, README, LICENSE, and spec.md are already outside it. Do not add anything else here.
EXEMPT_PATHS = frozenset({"metacognition/.claude-plugin/plugin.json"})

# Spec Component I, spelled exactly as the spec spells them. Matching is case-sensitive substring, like grep.
PRIVATE_TOKENS = (
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

# Same litter rule as tools/sync_skills.py: interpreter caches and OS litter are gitignored and never shipped.
LITTER_DIRS = frozenset({"__pycache__"})
LITTER_NAMES = frozenset({".DS_Store"})
LITTER_SUFFIXES = frozenset({".pyc"})

UNDECODABLE = "not valid UTF-8"
MODEL_KEY = re.compile(r"^\s*(model|disable-model-invocation)\s*:")

# Active version shape: SemVer MAJOR.MINOR.PATCH with MAJOR fixed at 0 during beta.
# At the 1.0 maturity milestone this flips to the CalVer shape YYYY.MM.DD with an optional .N suffix:
#     re.compile(r"\d{4}\.\d{2}\.\d{2}(\.\d+)?")
VERSION_SHAPE = re.compile(r"0\.\d+\.\d+")


@dataclass(frozen=True)
class Finding:
    """One violation: a file, a 1-indexed line (0 when the whole file is at fault), and what was found."""

    path: Path
    line: int
    detail: str

    def render(self) -> str:
        """Return "path:line: detail" so a failing assertion names exactly what to fix."""
        return f"{self.path.as_posix()}:{self.line}: {self.detail}"


@dataclass(frozen=True)
class ScanResult:
    """Findings plus how many files the scan actually read."""

    findings: list[Finding]
    files_scanned: int


def is_litter(path: Path) -> bool:
    """Return True for interpreter caches and OS litter."""
    return bool(LITTER_DIRS.intersection(path.parts)) or path.name in LITTER_NAMES or path.suffix in LITTER_SUFFIXES


def iter_files(repo_root: Path, directories: tuple[str, ...]) -> Iterator[Path]:
    """Yield non-litter files under each existing directory, as paths relative to repo_root, sorted."""
    for directory in directories:
        base = repo_root / directory
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            relative = path.relative_to(repo_root)
            if path.is_file() and not is_litter(relative):
                yield relative


def find_tokens(text: str) -> list[tuple[int, str]]:
    """Return (1-indexed line, token) for every private token on every line, in line then list order."""
    return [
        (line_number, token)
        for line_number, line in enumerate(text.splitlines(), start=1)
        for token in PRIVATE_TOKENS
        if token in line
    ]


def scan_tree(
    repo_root: Path,
    scope: tuple[str, ...] = SCOPE_DIRS,
    exempt: frozenset[str] = EXEMPT_PATHS,
) -> ScanResult:
    """Scan every scoped file for private tokens.

    A file that is not valid UTF-8 is a finding, not a skip: shipped content is text, and a binary could
    hide a token from a text search.
    """
    findings: list[Finding] = []
    scanned = 0
    for relative in iter_files(repo_root, scope):
        if relative.as_posix() in exempt:
            continue
        scanned += 1
        try:
            text = (repo_root / relative).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(Finding(relative, 0, UNDECODABLE))
            continue
        findings.extend(Finding(relative, line, token) for line, token in find_tokens(text))
    return ScanResult(findings, scanned)


def _read(repo_root: Path, relative: Path) -> str | None:
    try:
        return (repo_root / relative).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def skill_files(repo_root: Path) -> list[Path]:
    """Return every metacognition/skills/*/SKILL.md, relative to repo_root."""
    return sorted(path.relative_to(repo_root) for path in (repo_root / "metacognition" / "skills").glob("*/SKILL.md"))


def agent_files(repo_root: Path) -> list[Path]:
    """Return every metacognition/agents/*.md, relative to repo_root."""
    return sorted(path.relative_to(repo_root) for path in (repo_root / "metacognition" / "agents").glob("*.md"))


def read_frontmatter(path: Path) -> YamlMap | None:
    """Parse a markdown file's frontmatter with scripts.yaml_subset; None when absent or unparseable."""
    block = extract_frontmatter(path.read_text(encoding="utf-8"))
    if block is None:
        return None
    try:
        return parse(block)
    except YamlSubsetError:
        return None


def find_model_keys(repo_root: Path) -> list[Finding]:
    """Flag a model: or disable-model-invocation: key in any SKILL.md or agent file.

    Checks the parsed frontmatter and also every frontmatter line, so a file whose frontmatter fails to
    parse cannot slip through. With no complete frontmatter block, every line is checked.
    """
    findings: list[Finding] = []
    for relative in skill_files(repo_root) + agent_files(repo_root):
        text = _read(repo_root, relative)
        if text is None:
            findings.append(Finding(relative, 0, UNDECODABLE))
            continue
        lines = text.splitlines()
        block = extract_frontmatter(text)
        limit = len(lines) if block is None else len(block.splitlines()) + 1
        flagged: set[int] = set()
        for line_number, line in enumerate(lines[:limit], start=1):
            match = MODEL_KEY.match(line)
            if match:
                flagged.add(line_number)
                findings.append(Finding(relative, line_number, match.group(1)))
        parsed = read_frontmatter(repo_root / relative)
        if parsed is not None and not flagged:
            findings.extend(Finding(relative, 0, key) for key in ("model", "disable-model-invocation") if key in parsed)
    return findings


def find_parent_refs(repo_root: Path) -> list[Finding]:
    """Flag "../" in every file under each skill directory (SKILL.md, references/, scripts/).

    Each skill runs alone, so it may only reach its own files by relative path.
    """
    findings: list[Finding] = []
    for skill in skill_files(repo_root):
        for relative in iter_files(repo_root, (skill.parent.as_posix(),)):
            text = _read(repo_root, relative)
            if text is None:
                findings.append(Finding(relative, 0, UNDECODABLE))
                continue
            findings.extend(
                Finding(relative, line_number, '"../"')
                for line_number, line in enumerate(text.splitlines(), start=1)
                if "../" in line
            )
    return findings


def is_active_version_shape(version: str) -> bool:
    """Return True when version matches VERSION_SHAPE exactly (no surrounding whitespace)."""
    return VERSION_SHAPE.fullmatch(version) is not None


def collect_versions(repo_root: Path) -> dict[str, str | None]:
    """Map each version source to its value, or None when the source has no string version.

    Sources: every skill's SKILL.md frontmatter, the plugin manifest, the marketplace metadata, and any
    version field on a marketplace plugin entry (held to the same value only if present).
    """
    versions: dict[str, str | None] = {}
    for relative in skill_files(repo_root):
        parsed = read_frontmatter(repo_root / relative)
        value = parsed.get("version") if parsed else None
        versions[relative.as_posix()] = value if isinstance(value, str) else None

    plugin_path = "metacognition/.claude-plugin/plugin.json"
    plugin = _load_json(repo_root / plugin_path)
    versions[plugin_path] = _string_or_none(plugin.get("version"))

    market_path = ".claude-plugin/marketplace.json"
    market = _load_json(repo_root / market_path)
    metadata = market.get("metadata")
    meta_version = metadata.get("version") if isinstance(metadata, dict) else None
    versions[f"{market_path} (metadata.version)"] = _string_or_none(meta_version)
    plugins = market.get("plugins")
    if isinstance(plugins, list):
        for index, entry in enumerate(plugins):
            if isinstance(entry, dict) and "version" in entry:
                versions[f"{market_path} (plugins[{index}].version)"] = _string_or_none(entry["version"])
    return versions


def snippet_section(text: str, name: str) -> str | None:
    """Return the lines between a section's start and end snippet markers, or None when either is missing.

    The markers are the ones the docs build reads: a line holding ``--8<-- [start:<name>]`` and a later
    line holding ``--8<-- [end:<name>]``.
    """
    lines = text.splitlines(keepends=True)
    start = next((index for index, line in enumerate(lines) if f"--8<-- [start:{name}]" in line), None)
    if start is None:
        return None
    end = next((index for index, line in enumerate(lines) if index > start and f"--8<-- [end:{name}]" in line), None)
    if end is None:
        return None
    return "".join(lines[start + 1 : end])


def _string_or_none(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _load_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}
