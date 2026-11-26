# /// script
# requires-python = ">=3.9"
# dependencies = ["pytest"]
# ///
"""Check the hidden tests themselves, without AI.

For every task: the untouched project must FAIL the hidden tests, and the hand-written answer in reference/
must PASS them. If this is not true, the judge is wrong and no agent result can be trusted.

Usage:  uv run check_tasks.py
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import factory

HERE = Path(__file__).resolve().parent


def main() -> None:
    bad = 0
    for task in sorted(p for p in (HERE / "tasks").iterdir() if (p / "task.md").exists()):
        workspace = factory.new_workspace(task)
        log = Path(tempfile.mkdtemp()) / "log.txt"
        before = factory.pytest(task / "hidden", workspace, log)
        shutil.copy(HERE / "reference" / f"{task.name}.py", workspace / "shop" / "cart.py")
        after = factory.pytest(task / "hidden", workspace, log)
        ok = before[1] > 0 and after[1] == 0 and after[0] > 0
        bad += not ok
        print(f"{'ok ' if ok else 'BAD'} {task.name}: untouched project {before[0]} passed / {before[1]} failed, "
              f"reference answer {after[0]} passed / {after[1]} failed {after[2] if after[1] else ''}")
        shutil.rmtree(workspace, ignore_errors=True)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
