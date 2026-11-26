"""Tests for start_service: running a product's web app in its own process."""
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import factory  # noqa: E402

APP = '''
def application(environ, start_response):
    if environ["PATH_INFO"] == "/boom":
        raise RuntimeError("boom")
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"%s %s" % (WORD, environ["PATH_INFO"].encode())]
'''


def make_code(folder: Path, word: str) -> Path:
    (folder / "app").mkdir(parents=True)
    (folder / "app" / "__init__.py").write_text("")
    (folder / "app" / "web.py").write_text(f"WORD = {word.encode()!r}\n" + APP)
    return folder


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=5) as answer:
        return answer.read().decode()


@pytest.mark.parametrize("entry", ["app.web", ":application", "app.web:", "", "a:b:c"])
def test_a_bad_entry_raises_value_error(tmp_path, entry):
    with pytest.raises(ValueError):
        factory.start_service(tmp_path, entry)


def test_the_service_answers_and_stops(tmp_path):
    with factory.start_service(make_code(tmp_path, "hello")) as service:
        assert service.url.startswith("http://127.0.0.1:") and not service.url.endswith("/")
        assert get(service.url + "/parcels") == "hello /parcels"
        output = service.output
    assert service.process.poll() is not None
    assert not output.exists()
    service.stop()  # a second stop is safe


def test_an_error_in_the_app_gives_500_and_the_service_goes_on(tmp_path):
    with factory.start_service(make_code(tmp_path, "hi")) as service:
        with pytest.raises(urllib.error.HTTPError) as error:
            get(service.url + "/boom")
        assert error.value.code == 500
        assert get(service.url + "/next") == "hi /next"


def test_two_services_run_side_by_side(tmp_path):
    with factory.start_service(make_code(tmp_path / "one", "one")) as first, \
            factory.start_service(make_code(tmp_path / "two", "two")) as second:
        assert first.url != second.url
        assert get(first.url + "/") == "one /"
        assert get(second.url + "/") == "two /"


def test_a_missing_module_fails_fast_with_the_error(tmp_path):
    started = time.monotonic()
    with pytest.raises(RuntimeError, match="No module named 'nothere'") as error:
        factory.start_service(tmp_path, "nothere:application", wait=30)
    assert str(error.value).startswith("The service could not start")
    assert time.monotonic() - started < 10


def test_a_missing_name_fails_with_the_name(tmp_path):
    with pytest.raises(RuntimeError, match="missing_app"):
        factory.start_service(make_code(tmp_path, "x"), "app.web:missing_app")


def test_a_service_that_never_listens_is_killed_after_the_wait(tmp_path):
    (tmp_path / "slow.py").write_text("import time\ntime.sleep(60)\napplication = None\n")
    started = time.monotonic()
    with pytest.raises(RuntimeError, match="could not start"):
        factory.start_service(tmp_path, "slow:application", wait=0.5)
    assert time.monotonic() - started < 5
