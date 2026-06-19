"""Offline unit tests for slithyt.update — every network/subprocess seam is injected."""

import io
import json

import pytest

from slithyt import update


class FakeResponse:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def make_opener(version: str):
    payload = json.dumps({"info": {"version": version}}).encode()

    def opener(url, timeout=None):
        return FakeResponse(payload)

    return opener


class FakeResult:
    def __init__(self, returncode: int):
        self.returncode = returncode


# --------------------------------------------------------------------- versions


def test_parse_version_orders_and_ignores_suffixes():
    assert update.parse_version("1.2.3") == (1, 2, 3)
    assert update.parse_version("1.2.3") > update.parse_version("1.2.0")
    assert update.parse_version("2.0.0") > update.parse_version("1.9.9")
    assert update.parse_version("0.0.0+dev") == (0, 0, 0)


def test_check_update_available(monkeypatch):
    monkeypatch.setattr(update, "__version__", "1.0.0")
    status = update.check_update(opener=make_opener("1.1.0"))
    assert status.update_available
    assert status.current_version == "1.0.0"
    assert status.latest_version == "1.1.0"


def test_check_update_not_available(monkeypatch):
    monkeypatch.setattr(update, "__version__", "1.1.0")
    status = update.check_update(opener=make_opener("1.1.0"))
    assert not status.update_available


# -------------------------------------------------------------------- self_update


def test_self_update_no_op_when_current(monkeypatch):
    monkeypatch.setattr(update, "__version__", "1.0.0")
    out = io.StringIO()
    status = update.self_update(opener=make_opener("1.0.0"), runner=lambda cmd: FakeResult(0), out=out)
    assert not status.update_available
    assert "up to date" in out.getvalue()


def test_self_update_runs_uv_tool_upgrade(monkeypatch):
    monkeypatch.setattr(update, "__version__", "1.0.0")
    monkeypatch.setattr(update.shutil, "which", lambda name: "/usr/bin/uv")
    calls = []

    def runner(cmd):
        calls.append(cmd)
        return FakeResult(0)

    update.self_update(opener=make_opener("2.0.0"), runner=runner, out=io.StringIO())
    assert calls == [["/usr/bin/uv", "tool", "upgrade", "slithyt"]]


def test_self_update_raises_without_uv(monkeypatch):
    monkeypatch.setattr(update, "__version__", "1.0.0")
    monkeypatch.setattr(update.shutil, "which", lambda name: None)
    with pytest.raises(update.UpdateError):
        update.self_update(opener=make_opener("2.0.0"), runner=lambda cmd: FakeResult(0), out=io.StringIO())


def test_self_update_raises_on_uv_failure(monkeypatch):
    monkeypatch.setattr(update, "__version__", "1.0.0")
    monkeypatch.setattr(update.shutil, "which", lambda name: "/usr/bin/uv")
    with pytest.raises(update.UpdateError):
        update.self_update(opener=make_opener("2.0.0"), runner=lambda cmd: FakeResult(1), out=io.StringIO())


# ---------------------------------------------------------------------------- nag


def test_nag_prints_and_caches_when_newer(monkeypatch, tmp_path):
    monkeypatch.setattr(update, "__version__", "1.0.0")
    cache = tmp_path / "check.json"
    out = io.StringIO()
    update.maybe_notify_update("generate", opener=make_opener("2.0.0"), cache_path=cache, now=1000.0, out=out)
    assert "newer slithyt is available" in out.getvalue()
    assert json.loads(cache.read_text())["latest_version"] == "2.0.0"


def test_nag_silent_for_non_nag_command(tmp_path):
    out = io.StringIO()
    update.maybe_notify_update("build-cache", opener=make_opener("2.0.0"), cache_path=tmp_path / "c.json", now=1.0, out=out)
    assert out.getvalue() == ""


def test_nag_uses_cache_within_ttl_without_network(monkeypatch, tmp_path):
    monkeypatch.setattr(update, "__version__", "1.0.0")
    cache = tmp_path / "c.json"
    cache.write_text(json.dumps({"latest_version": "1.0.0", "checked_at": 1000.0}))

    def boom(url, timeout=None):
        raise AssertionError("network must not be hit within TTL")

    out = io.StringIO()
    update.maybe_notify_update("generate", opener=boom, cache_path=cache, now=1050.0, out=out)
    assert out.getvalue() == ""  # cached latest == current -> no nag, and no network


def test_nag_rechecks_after_ttl(monkeypatch, tmp_path):
    monkeypatch.setattr(update, "__version__", "1.0.0")
    cache = tmp_path / "c.json"
    cache.write_text(json.dumps({"latest_version": "1.0.0", "checked_at": 0.0}))
    out = io.StringIO()
    update.maybe_notify_update(
        "generate", opener=make_opener("3.0.0"), cache_path=cache,
        now=update.CHECK_TTL_SECONDS + 1, out=out,
    )
    assert "-> 3.0.0" in out.getvalue()


def test_nag_swallows_network_error(monkeypatch, tmp_path):
    monkeypatch.setattr(update, "__version__", "1.0.0")

    def boom(url, timeout=None):
        raise OSError("offline")

    out = io.StringIO()
    update.maybe_notify_update("generate", opener=boom, cache_path=tmp_path / "c.json", now=1.0, out=out)
    assert out.getvalue() == ""


def test_nag_respects_no_check_flag(monkeypatch, tmp_path):
    monkeypatch.setattr(update, "__version__", "1.0.0")
    out = io.StringIO()
    update.maybe_notify_update(
        "generate", opener=make_opener("2.0.0"), cache_path=tmp_path / "c.json",
        now=1.0, no_check=True, out=out,
    )
    assert out.getvalue() == ""


def test_nag_respects_env_var(monkeypatch, tmp_path):
    monkeypatch.setattr(update, "__version__", "1.0.0")
    monkeypatch.setenv(update.ENV_NO_CHECK, "1")
    out = io.StringIO()
    update.maybe_notify_update("generate", opener=make_opener("2.0.0"), cache_path=tmp_path / "c.json", now=1.0, out=out)
    assert out.getvalue() == ""
