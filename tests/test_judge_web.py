"""Tests for the judge serving a product's web app: web_entry, pytest(serve=...), run_task and build."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import factory  # noqa: E402

APP = '''
def application(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"hello " + environ["PATH_INFO"].encode()]
'''

CHECK_URL = '''
import os, urllib.request

def test_the_app_answers():
    url = os.environ["PRODUCT_URL"]
    assert url.startswith("http://127.0.0.1:") and not url.endswith("/")
    with urllib.request.urlopen(url + "/parcels", timeout=5) as answer:
        assert answer.read() == b"hello /parcels"
'''

CHECK_NO_URL = '''
import os

def test_there_is_no_url():
    assert "PRODUCT_URL" not in os.environ
'''


def make(tmp_path: Path, check: str) -> tuple[Path, Path]:
    workspace, tests = tmp_path / "work", tmp_path / "checks"
    (workspace / "app").mkdir(parents=True)
    (workspace / "app" / "__init__.py").write_text("")
    (workspace / "app" / "web.py").write_text(APP)
    tests.mkdir()
    (tests / "test_web.py").write_text(check)
    return workspace, tests


def remember_services(monkeypatch) -> list:
    started, real = [], factory.start_service
    monkeypatch.setattr(factory, "start_service", lambda *a, **k: started.append(real(*a, **k)) or started[-1])
    return started


# web_entry

def test_no_web_txt_gives_none(tmp_path):
    assert factory.web_entry(tmp_path) is None


def test_the_first_line_that_is_not_blank_is_the_entry(tmp_path):
    (tmp_path / "web.txt").write_text("\n   \n  app.web:application  \nother:thing\n")
    assert factory.web_entry(tmp_path) == "app.web:application"


@pytest.mark.parametrize("text", ["", "\n  \n", "app.web", ":application", "app.web:", "a:b:c"])
def test_a_bad_web_txt_raises_value_error(tmp_path, text):
    (tmp_path / "web.txt").write_text(text)
    with pytest.raises(ValueError):
        factory.web_entry(tmp_path)


# pytest with serve

@pytest.mark.parametrize("serve", ["", "app.web", "a:b:c", ":x"])
def test_a_bad_serve_raises_before_any_folder_is_made(tmp_path, monkeypatch, serve):
    workspace, tests = make(tmp_path, CHECK_URL)
    monkeypatch.setattr(factory.tempfile, "mkdtemp", lambda **k: pytest.fail("a folder was made"))
    with pytest.raises(ValueError):
        factory.pytest(tests, workspace, tmp_path / "log.txt", serve)


def test_the_tests_reach_the_served_app_and_the_service_is_stopped(tmp_path, monkeypatch):
    workspace, tests = make(tmp_path, CHECK_URL)
    started = remember_services(monkeypatch)
    assert factory.pytest(tests, workspace, tmp_path / "log.txt", "app.web:application") == (1, 0, [])
    assert len(started) == 1 and started[0].process.poll() is not None


def test_the_service_is_stopped_and_the_judge_removed_when_the_run_raises(tmp_path, monkeypatch):
    workspace, tests = make(tmp_path, CHECK_URL)
    started, judges, real_mkdtemp = remember_services(monkeypatch), [], factory.tempfile.mkdtemp
    monkeypatch.setattr(factory.tempfile, "mkdtemp", lambda **k: judges.append(real_mkdtemp(**k)) or judges[-1])

    def broken_run(*args, **kwargs):
        raise TimeoutError("too slow")
    monkeypatch.setattr(factory, "run", broken_run)
    with pytest.raises(TimeoutError):
        factory.pytest(tests, workspace, tmp_path / "log.txt", "app.web:application")
    assert started[0].process.poll() is not None
    assert not any(Path(j).exists() for j in judges if "judge" in j)


def test_a_service_that_cannot_start_means_no_tests_run(tmp_path, monkeypatch):
    workspace, tests = make(tmp_path, CHECK_URL)
    monkeypatch.setattr(factory, "run", lambda *a, **k: pytest.fail("the tests ran"))
    log = tmp_path / "log.txt"
    assert factory.pytest(tests, workspace, log, "nothere:application") == (0, 1, [factory.COULD_NOT_RUN])
    text = log.read_text()
    assert "The service could not start" in text and "No module named 'nothere'" in text


def test_without_serve_product_url_is_removed_and_no_service_starts(tmp_path, monkeypatch):
    workspace, tests = make(tmp_path, CHECK_NO_URL)
    monkeypatch.setenv("PRODUCT_URL", "http://127.0.0.1:1")
    monkeypatch.setattr(factory, "start_service", lambda *a, **k: pytest.fail("a service started"))
    assert factory.pytest(tests, workspace, tmp_path / "log.txt") == (1, 0, [])


# run_task and build

def test_run_task_passes_serve_to_both_test_runs(tmp_path, monkeypatch):
    task = tmp_path / "01-task"
    (task / "hidden").mkdir(parents=True)
    (task / "task.md").write_text("Do it.")
    workspace = tmp_path / "work"
    (workspace / "tests").mkdir(parents=True)
    seen = []
    monkeypatch.setattr(factory, "HERE", tmp_path)
    monkeypatch.setattr(factory, "new_workspace", lambda t: workspace)
    monkeypatch.setattr(factory, "ask_agent", lambda prompt, ws, log: log.parent.mkdir(parents=True, exist_ok=True)
                        or {"ok": True, "said": "", "cost": 0.0, "steps": []})
    monkeypatch.setattr(factory, "run", lambda *a, **k: factory.subprocess.CompletedProcess(a, 0, "", ""))
    monkeypatch.setattr(factory, "pytest", lambda tests, ws, log, serve=None: seen.append(serve) or (1, 0, []))
    assert factory.run_task(task, serve="app.web:application")["passed"]
    assert seen == ["app.web:application", "app.web:application"]


@pytest.mark.parametrize("web, expected", [(None, None), ("app.web:application\n", "app.web:application")])
def test_build_passes_the_web_entry_to_every_task(tmp_path, monkeypatch, web, expected):
    product = tmp_path / "product"
    (product / "project").mkdir(parents=True)
    for name in ("01-a", "02-b"):
        (product / "tasks" / name / "hidden").mkdir(parents=True)
        (product / "tasks" / name / "task.md").write_text("Do it.")
    if web:
        (product / "web.txt").write_text(web)
    workspace = tmp_path / "work"
    workspace.mkdir()
    seen = []
    monkeypatch.setattr(factory, "PROJECT", factory.PROJECT)
    monkeypatch.setattr(factory, "run_task", lambda task, text, hidden=None, serve=None:
                        seen.append(serve) or {"passed": True, "workspace": str(workspace)})
    factory.build(product, "task.md")
    assert seen == [expected, expected]
