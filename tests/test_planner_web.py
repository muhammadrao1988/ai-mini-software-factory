"""Tests for planner_prompt, write_plan and start with --web."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import factory  # noqa: E402

HIDDEN = 'def test_one():\n    """One must be one."""\n    assert 1 == 1\n'


def a_plan(*names):
    return {"summary": "A small thing.", "tasks": [{"name": n, "task": f"Do {n}.", "ticket": f"{n} ticket",
                                                     "hidden_tests": HIDDEN} for n in names]}


def test_planner_prompt_without_web_is_planner():
    assert factory.planner_prompt() is factory.PLANNER and factory.planner_prompt(False) == factory.PLANNER


def test_web_planner_prompt_has_the_web_rules_and_keeps_intro_and_task_rules():
    text = factory.planner_prompt(True)
    for piece in ("standard library", "app/web.py", "app.web:application", "PRODUCT_URL", "urllib.request",
                  "unique", "setup_testing_defaults", "HTTPError", "must not import `app`"):
        assert piece in text
    intro = factory.PLANNER.split("Rules for the product:")[0]
    task_rules = factory.PLANNER.split("Rules for each task:")[1]
    assert text.startswith(intro) and text.endswith(task_rules)
    assert "no network" not in text


def test_write_plan_without_web(tmp_path):
    product = tmp_path / "p"
    folders = factory.write_plan(product, a_plan("Add Thing!", "***"), "p")
    assert folders == [product / "tasks" / "01-add-thing", product / "tasks" / "02-task"]
    for folder in folders:
        assert {f.name for f in folder.iterdir()} == {"task.md", "ticket.md", "hidden", "checklist.md"}
        assert "One must be one." in (folder / "checklist.md").read_text()
    project = product / "project"
    assert (project / "app" / "__init__.py").read_text() == ""
    assert (project / "tests" / "test_start.py").read_text() == "def test_the_package_loads():\n    import app  # noqa: F401\n"
    assert "# p\n\nA small thing." in (project / "README.md").read_text()
    assert not (product / "web.txt").exists() and not (project / "app" / "web.py").exists()
    assert not (product / "idea.md").exists()
    assert factory.web_entry(product) is None


def test_write_plan_with_web_makes_a_working_starter_app(tmp_path):
    product = tmp_path / "p"
    factory.write_plan(product, a_plan("one"), "p", web=True)
    assert (product / "web.txt").read_text().strip() == "app.web:application"
    assert factory.web_entry(product) == "app.web:application"
    assert "app.web:application" in (product / "project" / "README.md").read_text()
    env = {k: v for k, v in factory.os.environ.items() if k != "PRODUCT_URL"}
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                          cwd=product / "project", env=env, capture_output=True, text=True)
    assert "2 passed" in done.stdout, done.stdout + done.stderr


def test_the_starter_app_answers_404_json_for_anything(tmp_path):
    factory.write_plan(tmp_path / "p", a_plan("one"), "p", web=True)
    code = (tmp_path / "p" / "project" / "app" / "web.py").read_text()
    space = {}
    exec(code, space)
    from wsgiref.util import setup_testing_defaults
    for method, path in (("GET", "/"), ("POST", "/things/7")):
        environ, seen = {"REQUEST_METHOD": method, "PATH_INFO": path}, []
        setup_testing_defaults(environ)
        body = b"".join(space["application"](environ, lambda s, h, e=None: seen.append((s, h))))
        assert seen[0][0] == "404 Not Found" and ("Content-Type", "application/json") in seen[0][1]
        assert json.loads(body) == {"error": "not found"}


@pytest.mark.parametrize("plan", [None, [], {"tasks": []}, {"summary": "s", "tasks": []},
                                  {"summary": 1, "tasks": a_plan("a")["tasks"]}, {"summary": "s", "tasks": ["x"]},
                                  {"summary": "s", "tasks": [{"name": "a", "task": "b", "ticket": "c"}]},
                                  {"summary": "s", "tasks": [{"name": "a", "task": "b", "ticket": "c", "hidden_tests": 3}]}])
def test_a_bad_plan_raises_and_writes_nothing(tmp_path, plan):
    with pytest.raises(ValueError):
        factory.write_plan(tmp_path / "p", plan, "p")
    assert not (tmp_path / "p").exists()


def test_an_existing_folder_raises_before_the_plan_is_checked(tmp_path):
    (tmp_path / "p").mkdir()
    with pytest.raises(FileExistsError):
        factory.write_plan(tmp_path / "p", None, "p")
    assert list((tmp_path / "p").iterdir()) == []


@pytest.mark.parametrize("web", [False, True])
def test_start_uses_the_right_prompt_and_writes_the_plan(tmp_path, monkeypatch, capsys, web):
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, json.dumps({"structured_output": a_plan("first", "second")}), "")

    monkeypatch.setattr(factory, "HERE", tmp_path)
    monkeypatch.setattr(factory.subprocess, "run", fake_run)
    factory.start("a booking tool", "book", 2, web=web)
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[args.index("--system-prompt") + 1] == factory.planner_prompt(web)
    assert ("web API" in kwargs["input"]) == web and "a booking tool" in kwargs["input"]
    product = tmp_path / "products" / "book"
    assert (product / "idea.md").read_text().startswith("a booking tool")
    assert (product / "web.txt").exists() == web
    out = capsys.readouterr().out
    assert "01-first: first ticket" in out and "02-second: second ticket" in out
