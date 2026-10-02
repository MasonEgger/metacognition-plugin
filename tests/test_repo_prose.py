# ABOUTME: Runs tools/prose_scrub.py over this repo's own prose and asserts no finding.
# Uses the gate's own file selection, so build output, environments, and caches are never scanned.
"""The repo's own prose passes the writing-rules gate."""

from pathlib import Path

import prose_scrub

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_repo_prose_is_clean() -> None:
    """The gate, run from the repo root, reports nothing; a failure lists every finding with file and line."""
    # Act
    findings = prose_scrub.scan_paths([REPO_ROOT])

    # Assert
    report = "\n".join(
        f"{Path(finding.path).relative_to(REPO_ROOT).as_posix()}:{finding.line}: {finding.rule}: {finding.excerpt}"
        for finding in findings
    )
    assert findings == [], f"{len(findings)} prose finding(s):\n{report}"


def test_repo_scan_reaches_the_repos_own_prose() -> None:
    """Guard against a vacuous pass: the gate's file selection includes the planning docs and skills."""
    # Act
    collected = {path.relative_to(REPO_ROOT).as_posix() for path in prose_scrub.collect_files(REPO_ROOT)}

    # Assert
    assert {"spec.md", "plan.md", "README.md", "metacognition/skills/design/SKILL.md"} <= collected
    assert "tests/fixtures/prose/clean.md" in collected
    assert "tests/fixtures/prose/dirty.md" not in collected
    assert not any(part in {".venv", "site", "dist", ".git"} for path in collected for part in path.split("/")[:1])
