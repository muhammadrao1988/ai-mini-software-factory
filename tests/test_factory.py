"""Tests for the factory itself. No AI is used here."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import factory  # noqa: E402

HERE = Path(factory.__file__).resolve().parent
TASK = HERE / "tasks" / "01-discount-code"


def test_judge_fails_the_untouched_project(tmp_path):
    workspace = factory.new_workspace(TASK)
    passed, failed, names = factory.pytest(TASK / "hidden", workspace, tmp_path / "log.txt")
    assert passed == 0 and failed == 9
    assert (tmp_path / "log.txt").read_text()


def test_judge_passes_the_reference_answer(tmp_path):
    workspace = factory.new_workspace(TASK)
    (workspace / "shop" / "cart.py").write_text((HERE / "reference" / "01-discount-code.py").read_text())
    passed, failed, names = factory.pytest(TASK / "hidden", workspace, tmp_path / "log.txt")
    assert (passed, failed, names) == (9, 0, [])


def test_judge_ignores_settings_files_the_agent_left_behind(tmp_path):
    workspace = factory.new_workspace(TASK)
    (workspace / "shop" / "cart.py").write_text((HERE / "reference" / "01-discount-code.py").read_text())
    (workspace / "pytest.ini").write_text("[pytest]\naddopts = --this-option-does-not-exist\n")
    (workspace / "conftest.py").write_text("raise RuntimeError('a broken helper file')\n")
    passed, failed, _ = factory.pytest(TASK / "hidden", workspace, tmp_path / "log.txt")
    assert (passed, failed) == (9, 0)


def test_code_that_cannot_load_counts_as_a_fail(tmp_path):
    workspace = factory.new_workspace(TASK)
    (workspace / "shop" / "cart.py").write_text("this is not python\n")
    passed, failed, names = factory.pytest(TASK / "hidden", workspace, tmp_path / "log.txt")
    assert passed == 0 and failed >= 1 and names == [factory.COULD_NOT_RUN]


def test_notes_are_the_plain_sentences_not_the_test_code():
    notes = factory.notes_for(["test_unknown_code", "test_rounding"], TASK / "hidden")
    assert notes == ["An unknown code must raise ValueError.", "The total must be rounded to 2 decimal places."]


def test_checklist_lists_every_hidden_test_in_plain_words():
    text = factory.checklist(TASK / "hidden")
    assert text.count("\n- ") == 9 and "An unknown code must raise ValueError." in text and "def test_" not in text


def test_steps_are_written_in_plain_words(tmp_path):
    assert factory.step_in_words("Read", {"file_path": str(tmp_path / "shop" / "cart.py")}, tmp_path) == "reads shop/cart.py"
    assert factory.step_in_words("Edit", {"file_path": str(tmp_path / "a.py")}, tmp_path) == "changes a.py"
    assert factory.step_in_words("Bash", {"command": "python3 -m pytest -q\nsecond line"}, tmp_path) == "runs: python3 -m pytest -q"


def test_workspace_is_a_fresh_copy_outside_the_project():
    workspace = factory.new_workspace(TASK)
    assert (workspace / "shop" / "cart.py").exists()
    assert HERE not in workspace.parents and not (workspace / "tasks").exists()


def test_agent_never_gets_an_api_key_by_accident(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    assert "ANTHROPIC_API_KEY" not in factory.agent_env()
