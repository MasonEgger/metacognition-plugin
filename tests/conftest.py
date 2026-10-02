# ABOUTME: Puts the repo's tools/ directory on sys.path so tests can import sync_skills.
# ABOUTME: Keeps pyproject's pytest pythonpath at ["src"] as the spec fixes it.
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
