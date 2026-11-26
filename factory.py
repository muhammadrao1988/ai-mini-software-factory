# /// script
# requires-python = ">=3.9"
# dependencies = ["pytest"]
# ///
"""A mini software factory.

A task goes in. An AI agent builds it alone in its own copy of the project. Hidden tests, which the agent
never sees, judge the result. A report shows what passed, how many tries it took and what it cost.

Usage:  uv run factory.py start "an online parcel tracking system" --name tracking
        uv run factory.py build products/tracking       (build your product, task by task)

        uv run factory.py tasks/01-discount-code         (the demo: one task on the demo shop)
        uv run factory.py tasks                          (the demo: every task)
        uv run factory.py tasks --tickets                (the demo: each task as a one-line ticket)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
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


SERVE = """import importlib, sys
from wsgiref.simple_server import make_server
application = getattr(importlib.import_module(sys.argv[1]), sys.argv[2])
make_server("127.0.0.1", int(sys.argv[3]), application).serve_forever()"""


class Service:
    """A product's web app running in its own process; stop it with stop() or a with-block."""

    def __init__(self, url: str, process: subprocess.Popen, output: Path):
        self.url, self.process, self.output = url, process, output

    def stop(self) -> None:
        """End the process and remove its output file; safe to call more than once."""
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process.wait()
        self.output.unlink(missing_ok=True)

    def __enter__(self) -> "Service":
        return self

    def __exit__(self, *exc) -> None:
        self.stop()


def start_service(code: Path, entry: str = "app.web:application", wait: float = 10.0) -> Service:
    """Serve the WSGI app `entry` ("module:name") from the folder `code` on a free port, and wait until it answers."""
    module, colon, name = entry.partition(":")
    if not module or not name or ":" in name:
        raise ValueError(f"entry must look like 'module:name', not {entry!r}")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    env = dict(os.environ, PYTHONPATH=str(code), PYTHONDONTWRITEBYTECODE="1")
    handle, name_of_file = tempfile.mkstemp(prefix="factory-service-", suffix=".log")
    output = Path(name_of_file)
    with os.fdopen(handle, "wb") as out:  # the child keeps its own copy of the file
        process = subprocess.Popen([sys.executable, "-c", SERVE, module, name, str(port)], cwd=code, env=env,
                                   stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT)
    service = Service(f"http://127.0.0.1:{port}", process, output)
    deadline = time.monotonic() + wait
    while process.poll() is None and time.monotonic() < deadline:
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
            return service
        except OSError:
            time.sleep(0.05)
    if process.poll() is None:
        process.kill()
    process.wait()
    tail = output.read_text(errors="replace")[-500:]
    service.stop()
    raise RuntimeError(f"The service could not start: {tail}")


def notes_for(failed: list[str], hidden: Path) -> list[str]:
    """Turn failed hidden tests into short notes. The agent gets the note, never the test itself."""
    text = "\n".join(p.read_text() for p in sorted(hidden.glob("test_*.py")))
    notes = []
    for name in failed:
        found = re.search(rf'def {re.escape(name)}\(.*?\):\s+"""(.*?)"""', text, re.S)
        notes.append(found.group(1).strip() if found else name)
    return notes


def run_task(task: Path, text: str = "task.md", hidden: Path | None = None) -> dict:
    spec = (task / text).read_text()
    hidden = hidden or task / "hidden"
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
        hid_pass, hid_fail, failed = pytest(hidden, workspace, logs / f"try-{attempt}-hidden.txt")
        notes = notes_for(failed, hidden)
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


PLANNER = """You plan small software products for a team of AI coding agents.
You get a product idea. Break it into small tasks that are built one after the other. Each task adds one thing.

Rules for the product:
- Plain Python, standard library only. No web framework, no outside packages, no network.
- All code lives in the package `app` (the folder app/ with __init__.py). Data is kept in memory or in sqlite3.
- The first task creates the core. Later tasks build on the earlier ones and must not break them.

Rules for each task:
- name: a short name in small letters with dashes, like "add-status-history".
- task: the full spec in plain, simple English. Name every public function or class, its inputs, what it
  returns and which errors it raises. Say in which module of `app` it lives.
- ticket: the same task as one short line.
- hidden_tests: a complete pytest file that checks the task through the public names in the spec only.
  6 to 9 tests. Every test starts with a docstring of one plain sentence that says what must be true, for
  example: An unknown tracking number must raise KeyError. Check normal cases and edge cases.
  The tests must be fair: a careful programmer who reads only the task text must be able to pass all of them.
"""

PLAN_SHAPE = {"type": "object", "required": ["summary", "tasks"], "additionalProperties": False, "properties": {
    "summary": {"type": "string"},
    "tasks": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                         "required": ["name", "task", "ticket", "hidden_tests"],
                                         "properties": {"name": {"type": "string"}, "task": {"type": "string"},
                                                        "ticket": {"type": "string"},
                                                        "hidden_tests": {"type": "string"}}}}}}


def checklist(hidden: Path) -> str:
    """The hidden tests as a list of plain sentences, so a person can read what will be checked without reading code."""
    text = "\n".join(f.read_text() for f in sorted(hidden.glob("test_*.py")))
    points = [" ".join(s.split()) for s in re.findall(r'def test_\w+\(.*?\):\s+"""(.*?)"""', text, re.S)]
    return ("# What the hidden tests check\n\nThe agent that builds this task never sees this list or the tests.\n"
            "You can: read it, and change the tests in `hidden/test_hidden.py` if a point is not what you want.\n\n"
            + "\n".join(f"- {point}" for point in points) + "\n")


def start(idea: str, name: str, how_many: int) -> None:
    """Turn an idea into a new product folder: an empty starter project and a list of tasks with hidden tests."""
    product = HERE / "products" / name
    if product.exists():
        sys.exit(f"{product} already exists. Choose another --name, or delete that folder.")
    print(f"The planner is turning your idea into {how_many} small tasks ...", flush=True)
    done = subprocess.run(["claude", "-p", "--model", MODEL, "--output-format", "json", "--tools", "",
                           "--system-prompt", PLANNER, "--json-schema", json.dumps(PLAN_SHAPE)],
                          input=f"The product idea: {idea}\n\nMake exactly {how_many} tasks.",
                          env=agent_env(), capture_output=True, text=True, timeout=1200)
    try:
        plan = json.loads(done.stdout)["structured_output"]
    except (json.JSONDecodeError, KeyError, TypeError):
        sys.exit("The planner did not return a plan:\n" + (done.stderr or done.stdout)[-500:])

    project = product / "project"
    (project / "app").mkdir(parents=True)
    (project / "tests").mkdir()
    (project / "app" / "__init__.py").write_text("")
    (project / "tests" / "test_start.py").write_text("def test_the_package_loads():\n    import app  # noqa: F401\n")
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    (project / "README.md").write_text(f"# {name}\n\n{plan['summary']}\n\nBuilt and tested by the factory with Python {version}. "
                                       f"Run the tests with `uv run --python {version} --with pytest pytest -q`.\n")
    (product / "idea.md").write_text(f"{idea}\n\n{plan['summary']}\n")
    for number, task in enumerate(plan["tasks"], 1):
        slug = re.sub(r"[^a-z0-9-]+", "-", task["name"].lower()).strip("-") or "task"
        folder = product / "tasks" / f"{number:02d}-{slug}"
        (folder / "hidden").mkdir(parents=True)
        (folder / "task.md").write_text(task["task"].rstrip() + "\n")
        (folder / "ticket.md").write_text(task["ticket"].rstrip() + "\n")
        (folder / "hidden" / "test_hidden.py").write_text(task["hidden_tests"].rstrip() + "\n")
        (folder / "checklist.md").write_text(checklist(folder / "hidden"))
        print(f"  {folder.name}: {task['ticket'].strip()}")
    print(f"\nYour product folder: {product}"
          f"\nRead task.md and checklist.md in each task folder first. The checklist says, in plain words, what the"
          f"\nhidden tests will check. The tests are yours: change anything that is not what you want."
          f"\nThen build it:  uv run factory.py build products/{name}")


def build(product: Path, text: str) -> list[dict]:
    """Build a product task by task. Each task starts from the work of the tasks before it, and is judged by
    the hidden tests of every task so far, so a new task cannot quietly break an old one."""
    global PROJECT
    PROJECT = product / "project"
    tasks = sorted(p for p in (product / "tasks").iterdir() if (p / "task.md").exists())
    if not PROJECT.is_dir() or not tasks:
        sys.exit(f"{product} is not a product folder. Make one with: uv run factory.py start \"your idea\" --name my-product")
    results, checks = [], Path(tempfile.mkdtemp(prefix="factory-checks-"))
    for task in tasks:
        for test_file in (task / "hidden").glob("test_*.py"):
            shutil.copy(test_file, checks / f"test_{task.name.replace('-', '_')}_{test_file.stem[5:]}.py")
        print(f"Task {task.name}", flush=True)
        result = run_task(task, text, hidden=checks)
        results.append(result)
        if not result["passed"]:
            print(f"  Stopped: {task.name} did not pass in {MAX_TRIES} tries. The product keeps the work up to the task before it."
                  f"\n  Look at out/logs/{task.name}/ . Often the task text or a hidden test needs a fix.")
            break
        # the passed work becomes the new state of the product
        workspace = Path(result["workspace"])
        shutil.rmtree(PROJECT)
        shutil.copytree(workspace, PROJECT, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "*.pyc"))
    shutil.rmtree(checks, ignore_errors=True)
    return results


def report(results: list[dict]) -> str:
    lines = ["| Task | Result | Tries | Time | Cost (API price) |", "|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['task']} | {'Passed' if r['passed'] else 'FAILED'} | {r['tries']} | {r['seconds']} s | ${r['cost']:.2f} |")
    ok = sum(r["passed"] for r in results)
    lines.append(f"\n{ok} of {len(results)} tasks passed. Total: {sum(r['seconds'] for r in results)} s, "
                 f"${sum(r['cost'] for r in results):.2f} at API prices (nothing is charged on a Claude subscription).")
    return "\n".join(lines)


def finish(results: list[dict], extra: str = "") -> None:
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(results, indent=2))
    table = report(results)
    (out / "report.md").write_text(table + "\n")
    print(f"\nWhat each agent did, what it changed and every verdict: {out / 'logs'}{extra}")
    print("\n" + table)


def main() -> None:
    global USE_API_KEY, PROJECT
    parser = argparse.ArgumentParser(description="A mini software factory. Start a product from an idea, build it, "
                                                 "or run the demo tasks.")
    parser.add_argument("command_or_path", help='"start", "build", or the path of a demo task folder')
    parser.add_argument("target", nargs="?", help='for start: your idea in quotes. For build: the product folder')
    parser.add_argument("--name", default="my-product", help="start: the name of the new product folder")
    parser.add_argument("--tasks", type=int, default=5, help="start: how many tasks the planner makes (default 5)")
    parser.add_argument("--tickets", action="store_true",
                        help="give the agent the one-line ticket (ticket.md) instead of the full spec (task.md)")
    parser.add_argument("--project", type=Path,
                        help="demo tasks only: your own Python project to work on. It must have a tests/ folder")
    parser.add_argument("--api-key", action="store_true",
                        help="pay with the ANTHROPIC_API_KEY in your environment instead of the Claude sign-in")
    args = parser.parse_args()
    USE_API_KEY = args.api_key
    if USE_API_KEY and not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("--api-key was given, but ANTHROPIC_API_KEY is not set.")
    if not shutil.which("claude"):
        sys.exit("Claude Code is not installed. See the README, step 1.")
    text = "ticket.md" if args.tickets else "task.md"

    if args.command_or_path == "start":
        if not args.target:
            sys.exit('Give your idea in quotes:  uv run factory.py start "an online parcel tracking system" --name tracking')
        start(args.target, re.sub(r"[^a-z0-9-]+", "-", args.name.lower()).strip("-") or "my-product", args.tasks)
        return
    if args.command_or_path == "build":
        if not args.target:
            sys.exit("Give the product folder:  uv run factory.py build products/tracking")
        product = Path(args.target).resolve()
        finish(build(product, text), f"\nYour product: {product / 'project'}")
        return

    path = Path(args.command_or_path)
    if args.project:
        PROJECT = args.project.resolve()
        if not (PROJECT / "tests").is_dir():
            sys.exit(f"{PROJECT} has no tests/ folder.")
    tasks = [path] if (path / "task.md").exists() else sorted(p for p in path.iterdir() if (p / "task.md").exists()) if path.is_dir() else []
    if not tasks:
        sys.exit(f"No task found in {path}")
    results = []
    for task in tasks:
        print(f"Task {task.name}", flush=True)
        results.append(run_task(task, text))
    finish(results)


if __name__ == "__main__":
    main()
