default:
    @just --list

# Format check, lint, types, tests, docs build (in that order).
check:
    uv run ruff format --check .
    uv run ruff check .
    uv run mypy src/scripts tests
    uv run pytest
    uv run mkdocs build --strict

fmt:
    uv run ruff format .
    uv run ruff check --fix .

test:
    uv run pytest

# Regenerate the per-skill copies from src/.
sync:
    uv run python tools/sync_skills.py

docs-build:
    uv run mkdocs build --strict

docs-serve:
    uv run mkdocs serve

# Build the per-skill zips without publishing.
release-dry:
    uv run python tools/build_zips.py
