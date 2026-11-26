# /// script
# requires-python = ">=3.9"
# dependencies = ["pytest"]
# ///
"""A mini software factory.

A task goes in. An AI agent builds it alone in its own copy of the project. Hidden tests, which the agent
never sees, judge the result. A report shows what passed, how many tries it took and what it cost.

Usage:  uv run factory.py tasks/01-discount-code
        uv run factory.py tasks            (every task in the folder)
        uv run factory.py tasks --tickets  (the same tasks, each written as a one-line ticket)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE / "demo"      # the project the agents work on; change it with --project
MAX_TRIES = 3
COULD_NOT_RUN = "the code could not be loaded, or the tests could not start"
MODEL = os.environ.get("FACTORY_MODEL", "sonnet")
# The agent may read and change files in its workspace and run the tests. Nothing else.
AGENT_TOOLS = ["Read", "Edit", "Write", "Glob", "Grep", "Bash(python3 -m pytest:*)"]
RULES = """You are a software engineer working alone on one task in this project folder.
- Read the code first. Make the smallest change that fully does the task.
- Add tests for the new behaviour and run all tests with: python3 -m pytest -q
- Work only inside this folder. Do not ask questions; decide and finish.
- When you are done, reply with one short paragraph that says what you changed."""


def run(args: list[str], cwd: Path, env: dict | None = None, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)


USE_API_KEY = False


def agent_env() -> dict:
    """The agent runs on the Claude Code sign-in. API keys are removed so no bill can appear by accident,
    unless the factory was started with --api-key."""
    env = dict(os.environ)
    for name in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        if not USE_API_KEY:
            env.pop(name, None)
    # put this program's own Python first, so "python3 -m pytest" works for the agent
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    return env


def new_workspace(task: Path) -> Path:
    """A fresh copy of the project, in a temporary folder away from the tasks and the hidden tests."""
    folder = Path(tempfile.mkdtemp(prefix=f"factory-{task.name}-"))
    shutil.copytree(PROJECT, folder, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".venv", "node_modules"))
    run(["git", "init", "-q"], folder)
    (folder / ".git" / "info" / "exclude").write_text("__pycache__/\n.pytest_cache/\n*.pyc\n")
    run(["git", "add", "-A"], folder)
    run(["git", "-c", "user.name=factory", "-c", "user.email=factory@localhost", "commit", "-q", "-m", "start"], folder)
    return folder


def step_in_words(name: str, given: dict, workspace: Path) -> str:
    """One thing the agent does, as a short line a person can read."""
    path = str(given.get("file_path") or given.get("path") or "")
    try:
        path = str(Path(path).resolve().relative_to(workspace.resolve()))
    except ValueError:
        pass
    if name == "Read":
        return f"reads {path}"
    if name in ("Edit", "Write"):
        return f"{'changes' if name == 'Edit' else 'writes'} {path}"
    if name == "Bash":
        return f"runs: {(str(given.get('command', '')).strip().splitlines() or [''])[0][:80]}"
    if name in ("Glob", "Grep"):
        return f"searches for {given.get('pattern', '')!r}"
    return f"uses {name}"


def ask_agent(prompt: str, workspace: Path, log: Path) -> dict:
    """One run of the agent. Shows each step while it works, and saves the steps and its answer in the log."""
    agent = subprocess.Popen(["claude", "-p", "--model", MODEL, "--output-format", "stream-json", "--verbose",
                              "--append-system-prompt", RULES, "--allowedTools", *AGENT_TOOLS],
                             cwd=workspace, env=agent_env(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)
    agent.stdin.write(prompt)
    agent.stdin.close()
    steps, answer = [], None
    for line in agent.stdout:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant":
            for part in event.get("message", {}).get("content", []):
                if part.get("type") == "tool_use":
                    step = step_in_words(part.get("name", ""), part.get("input", {}), workspace)
                    steps.append(step)
                    print(f"      agent {step}", flush=True)
        elif event.get("type") == "user":      # the result of a step; a refused step is marked
            content = event.get("message", {}).get("content", [])
            for part in content if isinstance(content, list) else []:
                if part.get("type") == "tool_result" and part.get("is_error") and steps:
                    if "permission" in str(part.get("content", "")).lower() and not steps[-1].endswith("(not allowed)"):
                        steps[-1] += "  (not allowed)"
                        print("        -> not allowed, refused", flush=True)
        elif event.get("type") == "result":
            answer = event
    agent.wait(timeout=60)
    log.parent.mkdir(parents=True, exist_ok=True)
    if answer is None:
        problem = agent.stderr.read()[-500:]
        log.write_text("The agent did not answer.\n" + problem)
        return {"ok": False, "said": problem, "seconds": 0, "cost": 0.0, "turns": 0, "steps": steps}
    said = answer.get("result", "") or ""
    log.write_text("WHAT THE AGENT WAS TOLD\n" + prompt + "\n\nWHAT THE AGENT DID\n"
                   + "\n".join(f"- {s}" for s in steps) + "\n\nWHAT THE AGENT SAID AT THE END\n" + said + "\n")
    return {"ok": not answer.get("is_error", False), "said": said, "steps": steps,
            "seconds": round(answer.get("duration_ms", 0) / 1000), "cost": answer.get("total_cost_usd", 0.0),
            "turns": answer.get("num_turns", 0)}


def pytest(tests: Path, workspace: Path, log: Path) -> tuple[int, int, list[str]]:
    """Run tests against the agent's work with plain code (no AI). Returns passed, failed, and the failed test names.

    The work is copied to a clean folder first, and the tests run with an empty settings file. So nothing the
    agent left behind (settings files, caches, helper files) can change how the judge runs. The full output is
    saved in the log file, so every verdict can be checked by a person later.
    """
    judge = Path(tempfile.mkdtemp(prefix="factory-judge-"))
    try:
        code = judge / "code"
        shutil.copytree(workspace, code, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "*.pyc"))
        shutil.copytree(tests, judge / "checks", ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        (judge / "empty.ini").write_text("[pytest]\n")
        env = dict(os.environ, PYTHONPATH=str(code), PYTHONDONTWRITEBYTECODE="1")
        done = run([sys.executable, "-m", "pytest", str(judge / "checks"), "-q", "-c", str(judge / "empty.ini"),
                    "--rootdir", str(judge / "checks"), "--noconftest", "-p", "no:cacheprovider", "-rf", "--tb=short"],
                   judge, env, timeout=300)
    finally:
        shutil.rmtree(judge, ignore_errors=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(done.stdout + ("\n--- error output ---\n" + done.stderr if done.stderr.strip() else ""))
    failed = re.findall(r"^FAILED \S+::(\w+)", done.stdout, re.M)
    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", done.stdout)) else 0
    errors = int(m.group(1)) if (m := re.search(r"(\d+) error", done.stdout)) else 0
    if errors or (not passed and not failed):
        failed = failed or [COULD_NOT_RUN]
    return passed, len(failed), failed


def notes_for(failed: list[str], hidden: Path) -> list[str]:
    """Turn failed hidden tests into short notes. The agent gets the note, never the test itself."""
    text = "\n".join(p.read_text() for p in sorted(hidden.glob("test_*.py")))
    notes = []
    for name in failed:
        found = re.search(rf'def {re.escape(name)}\(.*?\):\s+"""(.*?)"""', text, re.S)
        notes.append(found.group(1).strip() if found else name)
    return notes


def run_task(task: Path, text: str = "task.md") -> dict:
    spec = (task / text).read_text()
    workspace = new_workspace(task)
    result = {"task": task.name, "passed": False, "tries": 0, "seconds": 0, "cost": 0.0, "workspace": str(workspace),
              "history": []}
    prompt = f"Your task:\n\n{spec}"
    for attempt in range(1, MAX_TRIES + 1):
        print(f"  try {attempt}: agent is working ...", flush=True)
        started = time.time()
        logs = HERE / "out" / "logs" / task.name
        answer = ask_agent(prompt, workspace, logs / f"try-{attempt}-agent.txt")
        run(["git", "add", "-A", "-N"], workspace)
        (logs / f"try-{attempt}-change.diff").write_text(run(["git", "diff", "HEAD"], workspace).stdout)
        seen_pass, seen_fail, _ = pytest(workspace / "tests", workspace, logs / f"try-{attempt}-visible.txt")
        hid_pass, hid_fail, failed = pytest(task / "hidden", workspace, logs / f"try-{attempt}-hidden.txt")
        notes = notes_for(failed, task / "hidden")
        result["tries"] = attempt
        result["seconds"] += round(time.time() - started)
        result["cost"] += answer["cost"]
        result["history"].append({"try": attempt, "agent_ok": answer["ok"], "agent_said": answer["said"][:400], "agent_steps": answer.get("steps", []),
                                  "visible_tests": f"{seen_pass} passed, {seen_fail} failed",
                                  "hidden_tests": f"{hid_pass} passed, {hid_fail} failed", "notes": notes})
        print(f"    tests the agent can see: {seen_pass} passed, {seen_fail} failed")
        print(f"    hidden tests:            {hid_pass} passed, {hid_fail} failed")
        if answer["ok"] and not seen_fail and not hid_fail and hid_pass:
            result["passed"] = True
            break
        prompt = ("Your work was checked by tests you cannot see. These points are still wrong:\n"
                  + "\n".join(f"- {n}" for n in notes)
                  + f"\n\nFix them. The task was:\n\n{spec}")
    result["cost"] = round(result["cost"], 4)
    result["change"] = run(["git", "diff", "--stat", "HEAD"], workspace).stdout.strip().splitlines()[-1:] or ["no change"]
    return result


def report(results: list[dict]) -> str:
    lines = ["| Task | Result | Tries | Time | Cost (API price) |", "|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['task']} | {'Passed' if r['passed'] else 'FAILED'} | {r['tries']} | {r['seconds']} s | ${r['cost']:.2f} |")
    ok = sum(r["passed"] for r in results)
    lines.append(f"\n{ok} of {len(results)} tasks passed. Total: {sum(r['seconds'] for r in results)} s, "
                 f"${sum(r['cost'] for r in results):.2f} at API prices (nothing is charged on a Claude subscription).")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the mini software factory on one task or a folder of tasks.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--tickets", action="store_true",
                        help="give the agent the one-line ticket (ticket.md) instead of the full spec (task.md)")
    parser.add_argument("--project", type=Path,
                        help="your own Python project to work on (default: the demo shop). It must have a tests/ folder")
    parser.add_argument("--api-key", action="store_true",
                        help="pay with the ANTHROPIC_API_KEY in your environment instead of the Claude sign-in")
    args = parser.parse_args()
    global USE_API_KEY, PROJECT
    USE_API_KEY = args.api_key
    if args.project:
        PROJECT = args.project.resolve()
        if not (PROJECT / "tests").is_dir():
            sys.exit(f"{PROJECT} has no tests/ folder.")
    if USE_API_KEY and not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("--api-key was given, but ANTHROPIC_API_KEY is not set.")
    if not shutil.which("claude"):
        sys.exit("Claude Code is not installed. See the README, step 1.")
    tasks = [args.path] if (args.path / "task.md").exists() else sorted(p for p in args.path.iterdir() if (p / "task.md").exists())
    if not tasks:
        sys.exit(f"No task found in {args.path}")
    results = []
    for task in tasks:
        print(f"Task {task.name}", flush=True)
        results.append(run_task(task, "ticket.md" if args.tickets else "task.md"))
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(results, indent=2))
    table = report(results)
    print(f"\nWhat each agent did, what it changed and every verdict: {out / 'logs'}")
    (out / "report.md").write_text(table + "\n")
    print("\n" + table)


if __name__ == "__main__":
    main()
