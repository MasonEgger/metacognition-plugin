# ABOUTME: Builds dist/metacognition-<version>.zip, the upload-install asset for claude.ai and Cowork.
# ABOUTME: Refuses, naming each offending file, when the plugin tree is not exactly installable.
"""Build the plugin zip: dist/metacognition-<version>.zip.

Input is the marketplace manifest and the plugin directory. Output is one archive
whose every entry path begins with ``metacognition/`` (the plugin directory's name),
so that directory is the single top-level entry. Marketplace install is the primary
path; this zip is the GitHub Release asset and the alternate upload path.

The tool refuses to build, and writes nothing, when any of these holds. Every
refusal found is reported in one run, one line each on stderr naming the file:

1. The marketplace manifest is missing, unreadable, or lacks a string
   ``metadata.version``.
2. A SKILL.md version, or plugin.json's version, differs from that version, or
   plugin.json is missing or unreadable.
3. A SKILL.md has frontmatter that is absent or does not parse.
4. A SKILL.md frontmatter key is outside name, version, description, compatibility.
5. A SKILL.md lacks one of those four keys, or one is not a string.
6. A description is longer than 1,024 characters.
7. A description contains an angle-bracket token. The strict reading is used: any
   "<" or ">" character in a description is refused, since an upload surface may
   parse such text as markup.
8. A compatibility is longer than 500 characters.
9. ``sync_skills.py --check`` logic reports drift (missing, extra, or differing
   files), a manifest source is missing, or a target directory is a symlink.
10. The plugin has a top-level ``bin/`` (a directory or a file). Claude.ai and
    Cowork refuse to install a plugin that has one.
11. The plugin directory contains a symlink anywhere. The archive would carry content
    from outside the plugin, or a link an upload surface may reject.
12. The plugin directory does not exist.

The archive holds only regular files from the plugin directory, hidden ones
included (``.claude-plugin/plugin.json`` belongs to the plugin). Litter, as defined
by sync_skills.is_litter (``__pycache__``, ``*.pyc``, ``.DS_Store``), is left out.
Entries are written in sorted order with fixed timestamps and permissions, so two
builds of the same tree are byte-identical. The archive is written to a temporary
file and renamed, so a failed build never leaves a partial zip, and a refusal
leaves any existing zip untouched.

Usage:
    python3 tools/build_zips.py [--marketplace PATH] [--plugin DIR] [--src DIR] [--out DIR]

Exit codes: 0 built (the zip path is printed on stdout); 1 refused (reasons on stderr).
"""

import argparse
import json
import os
import re
import sys
import zipfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = Path(__file__).resolve().parent
for _path in (REPO_ROOT / "src", TOOLS_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from sync_skills import MANIFEST, SourceMissingError, SymlinkTargetError, find_drift, is_litter  # noqa: E402

from scripts.yaml_subset import YamlSubsetError, extract_frontmatter, parse  # noqa: E402

DEFAULT_MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
DEFAULT_PLUGIN = REPO_ROOT / "metacognition"
DEFAULT_SRC = REPO_ROOT / "src"
DEFAULT_OUT = REPO_ROOT / "dist"

EXIT_OK = 0
EXIT_REFUSED = 1

ALLOWED_KEYS = ("name", "version", "description", "compatibility")
MAX_DESCRIPTION = 1024
MAX_COMPATIBILITY = 500
VERSION_PATTERN = re.compile(r"[0-9A-Za-z][0-9A-Za-z.+-]*")
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

Manifest = Mapping[str, Mapping[str, tuple[str, ...]]]


@dataclass(frozen=True)
class Refusal:
    """One reason not to build, naming the file at fault."""

    path: Path
    message: str

    def __str__(self) -> str:
        return f"refused: {self.path}: {self.message}"


def read_json_object(path: Path) -> tuple[dict[str, object] | None, Refusal | None]:
    """Return the JSON object at path, or a refusal when it is missing, invalid, or not an object."""
    try:
        data: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return None, Refusal(path, f"cannot read as JSON ({error})")
    if not isinstance(data, dict):
        return None, Refusal(path, "JSON root is not an object")
    return {str(key): value for key, value in data.items()}, None


def marketplace_version(marketplace: Path) -> tuple[str | None, list[Refusal]]:
    """Read metadata.version from the marketplace manifest. It must be a string of version characters."""
    data, refusal = read_json_object(marketplace)
    if data is None or refusal is not None:
        return None, [refusal] if refusal else []
    metadata = data.get("metadata")
    version = metadata.get("version") if isinstance(metadata, dict) else None
    if not isinstance(version, str):
        return None, [Refusal(marketplace, "metadata.version is missing or not a string")]
    if not VERSION_PATTERN.fullmatch(version):
        return None, [Refusal(marketplace, f"metadata.version {version!r} is not usable in a file name")]
    return version, []


def plugin_json_version_refusal(plugin_dir: Path, version: str) -> Refusal | None:
    """Return a refusal when plugin.json is unreadable or its version differs from the marketplace's."""
    manifest = plugin_dir / ".claude-plugin" / "plugin.json"
    data, refusal = read_json_object(manifest)
    if data is None:
        return refusal
    found = data.get("version")
    if found != version:
        return Refusal(manifest, f"version {found!r} differs from marketplace version {version!r}")
    return None


def skill_files(plugin_dir: Path) -> list[Path]:
    """Return every skills/<name>/SKILL.md under the plugin, sorted."""
    return sorted(plugin_dir.glob("skills/*/SKILL.md"))


def skill_refusals(skill_md: Path, version: str) -> list[Refusal]:
    """Return every upload-constraint and version refusal for one SKILL.md."""
    try:
        text = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return [Refusal(skill_md, f"cannot read ({error})")]
    block = extract_frontmatter(text)
    if block is None:
        return [Refusal(skill_md, "no frontmatter block")]
    try:
        fields = parse(block)
    except YamlSubsetError as error:
        return [Refusal(skill_md, f"frontmatter does not parse ({error})")]
    refusals: list[Refusal] = []
    for key in fields:
        if key not in ALLOWED_KEYS:
            refusals.append(Refusal(skill_md, f"frontmatter key {key!r} is outside {', '.join(ALLOWED_KEYS)}"))
    for key in ALLOWED_KEYS:
        if not isinstance(fields.get(key), str):
            refusals.append(Refusal(skill_md, f"frontmatter key {key!r} is missing or not a string"))
    found = fields.get("version")
    if isinstance(found, str) and found != version:
        refusals.append(Refusal(skill_md, f"version {found!r} differs from marketplace version {version!r}"))
    description = fields.get("description")
    if isinstance(description, str):
        if len(description) > MAX_DESCRIPTION:
            refusals.append(Refusal(skill_md, f"description is {len(description)} characters, over {MAX_DESCRIPTION}"))
        if "<" in description or ">" in description:
            refusals.append(Refusal(skill_md, "description contains an angle bracket"))
    compatibility = fields.get("compatibility")
    if isinstance(compatibility, str) and len(compatibility) > MAX_COMPATIBILITY:
        refusals.append(
            Refusal(skill_md, f"compatibility is {len(compatibility)} characters, over {MAX_COMPATIBILITY}")
        )
    return refusals


def drift_refusals(src_dir: Path, skills_dir: Path, manifest: Manifest) -> list[Refusal]:
    """Return a refusal per drifted file, or one for a missing source or symlinked target."""
    try:
        drift = find_drift(src_dir, skills_dir, manifest)
    except (SourceMissingError, SymlinkTargetError) as error:
        return [Refusal(src_dir if isinstance(error, SourceMissingError) else skills_dir, str(error))]
    return [Refusal(skills_dir / item.path, f"sync drift ({item.kind}); run tools/sync_skills.py") for item in drift]


def bin_refusal(plugin_dir: Path) -> Refusal | None:
    """Return a refusal when the plugin has a top-level bin (directory, file, or link)."""
    bin_path = plugin_dir / "bin"
    if bin_path.exists() or bin_path.is_symlink():
        return Refusal(bin_path, "plugin has a top-level bin/, which claude.ai and Cowork refuse to install")
    return None


def walk_plugin(plugin_dir: Path) -> tuple[list[Path], list[Path]]:
    """Return (regular files, symlinks) under plugin_dir, litter skipped, never following a link."""
    files: list[Path] = []
    links: list[Path] = []
    for directory, subdirs, names in os.walk(plugin_dir, followlinks=False):
        base = Path(directory)
        subdirs[:] = sorted(name for name in subdirs if not is_litter(Path(name)) and not (base / name).is_symlink())
        links.extend(base / name for name in os.listdir(base) if (base / name).is_symlink())
        files.extend(
            base / name for name in sorted(names) if not is_litter(Path(name)) and not (base / name).is_symlink()
        )
    return sorted(files), sorted(links)


def find_refusals(
    plugin_dir: Path, marketplace: Path, src_dir: Path, manifest: Manifest
) -> tuple[str | None, list[Refusal]]:
    """Run every refusal check. Returns the version (None when unreadable) and all refusals found."""
    version, refusals = marketplace_version(marketplace)
    if not plugin_dir.is_dir():
        return version, [*refusals, Refusal(plugin_dir, "plugin directory does not exist")]
    if version is not None:
        plugin_refusal = plugin_json_version_refusal(plugin_dir, version)
        if plugin_refusal:
            refusals.append(plugin_refusal)
        for skill_md in skill_files(plugin_dir):
            refusals.extend(skill_refusals(skill_md, version))
    refusals.extend(drift_refusals(src_dir, plugin_dir / "skills", manifest))
    bin_found = bin_refusal(plugin_dir)
    if bin_found:
        refusals.append(bin_found)
    refusals.extend(Refusal(link, "symlink inside the plugin directory") for link in walk_plugin(plugin_dir)[1])
    return version, refusals


def build_zip(plugin_dir: Path, version: str, out_dir: Path) -> Path:
    """Write out_dir/<plugin>-<version>.zip from the plugin directory's regular files, sorted."""
    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / f"{plugin_dir.name}-{version}.zip"
    partial = archive.with_name(archive.name + ".partial")
    files = walk_plugin(plugin_dir)[0]
    entries = sorted((f"{plugin_dir.name}/{path.relative_to(plugin_dir).as_posix()}", path) for path in files)
    try:
        with zipfile.ZipFile(partial, "w", zipfile.ZIP_DEFLATED) as opened:
            for arcname, path in entries:
                info = zipfile.ZipInfo(arcname, ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                opened.writestr(info, path.read_bytes())
        partial.replace(archive)
    finally:
        partial.unlink(missing_ok=True)
    return archive


def run(marketplace: Path, plugin_dir: Path, src_dir: Path, out_dir: Path, manifest: Manifest = MANIFEST) -> int:
    """Check, then build. Prints the zip path on success, every refusal on stderr otherwise."""
    version, refusals = find_refusals(plugin_dir, marketplace, src_dir, manifest)
    if refusals or version is None:
        for refusal in refusals:
            print(refusal, file=sys.stderr)
        return EXIT_REFUSED
    print(build_zip(plugin_dir, version, out_dir))
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    """Parse options (defaulting to the repo's real paths) and run."""
    parser = argparse.ArgumentParser(description="Build dist/metacognition-<version>.zip.")
    parser.add_argument("--marketplace", type=Path, default=DEFAULT_MARKETPLACE, help="marketplace.json path")
    parser.add_argument("--plugin", type=Path, default=DEFAULT_PLUGIN, help="plugin directory")
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC, help="src root for the drift check")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output directory")
    args = parser.parse_args(argv)
    return run(args.marketplace, args.plugin, args.src, args.out)


if __name__ == "__main__":
    sys.exit(main())
