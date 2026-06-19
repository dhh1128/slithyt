"""slithyt.update — a "newer version available" nag plus self-update via uv.

slithyt is installed as a uv tool (``uv tool install slithyt``), so updating is
``uv tool upgrade slithyt``. The latest published version is read straight from
PyPI's JSON API. Every network path is best-effort: the nag swallows any failure
(offline, DNS, malformed JSON) so normal commands never stall or error, while an
explicit ``slithyt update`` surfaces problems clearly.

Stdlib only — no runtime dependency added. The public functions take injectable
seams (``opener``, ``cache_path``, ``now``, ``runner``) so the behavior is fully
unit-testable offline.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlopen

from slithyt import __version__

PACKAGE = "slithyt"
PYPI_JSON_URL = f"https://pypi.org/pypi/{PACKAGE}/json"

# The nag hits the network at most once per this window; within it the cached
# answer is reused so commands stay instant and offline-safe.
CHECK_TTL_SECONDS = 24 * 60 * 60
# Which subcommands may emit the nag (to stderr). `build-cache` is setup and
# `update` checks on its own, so neither nags.
NAG_COMMANDS = {"generate", "validate", "rhyme"}

ENV_NO_CHECK = "SLITHYT_NO_UPDATE_CHECK"


class UpdateError(RuntimeError):
    pass


@dataclass(frozen=True)
class UpdateStatus:
    current_version: str
    latest_version: str
    update_available: bool


def parse_version(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.split(r"[.\-+]", value) if part.isdigit())


# --------------------------------------------------------------------- fetching


def latest_version(timeout: float = 10.0, opener=None) -> str:
    """Return the latest version string published on PyPI."""
    opener = opener or urlopen
    with opener(PYPI_JSON_URL, timeout=timeout) as response:  # noqa: S310 (https by construction)
        raw = response.read()
    data = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)
    return data["info"]["version"]


def check_update(opener=None) -> UpdateStatus:
    latest = latest_version(opener=opener)
    return UpdateStatus(
        current_version=__version__,
        latest_version=latest,
        update_available=parse_version(latest) > parse_version(__version__),
    )


# ------------------------------------------------------------------- self-update


def self_update(*, opener=None, runner=None, out=None) -> UpdateStatus:
    """Update slithyt in place via ``uv tool upgrade``.

    Raises UpdateError with actionable guidance if uv is missing or the upgrade
    fails (e.g. slithyt was not installed as a uv tool).
    """
    out = out if out is not None else sys.stdout
    runner = runner or subprocess.run
    status = check_update(opener=opener)
    if not status.update_available:
        print(f"slithyt is up to date ({status.current_version}).", file=out)
        return status

    uv = shutil.which("uv")
    if not uv:
        raise UpdateError(
            "uv was not found on PATH. Update manually with:\n"
            "  pip install --upgrade slithyt"
        )
    print(
        f"Updating slithyt {status.current_version} -> {status.latest_version} "
        f"via `uv tool upgrade {PACKAGE}`...",
        file=out,
    )
    result = runner([uv, "tool", "upgrade", PACKAGE])
    if result.returncode != 0:
        raise UpdateError(
            f"`uv tool upgrade {PACKAGE}` failed (exit {result.returncode}). "
            f"If slithyt was not installed as a uv tool, install it with:\n"
            f"  uv tool install {PACKAGE}"
        )
    return status


# ------------------------------------------------------------------------- nag


def default_cache_path() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or os.path.join(os.path.expanduser("~"), ".local", "state")
    return Path(base) / "slithyt" / "update-check.json"


def _read_cache(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def _write_cache(path: Path, latest: str, checked_at: float) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"latest_version": latest, "checked_at": checked_at}))
    except OSError:
        pass  # a missing cache just means we recheck next time — never fatal


def maybe_notify_update(
    command: str,
    *,
    opener=None,
    cache_path: Path | None = None,
    now: float | None = None,
    ttl: float = CHECK_TTL_SECONDS,
    no_check: bool = False,
    out=None,
) -> None:
    """Print a pip-style "newer version available" line on stderr, at most once
    per `ttl`. Network is hit only on a cold/expired cache; any failure (offline,
    no network, bad JSON) is swallowed so commands never stall or error."""
    if command not in NAG_COMMANDS:
        return
    if no_check or os.environ.get(ENV_NO_CHECK) == "1":
        return

    out = out if out is not None else sys.stderr
    path = cache_path if cache_path is not None else default_cache_path()
    now = now if now is not None else time.time()

    cache = _read_cache(path)
    if cache and (now - cache.get("checked_at", 0)) < ttl:
        latest = cache.get("latest_version")
    else:
        try:
            latest = latest_version(opener=opener)
        except Exception:
            return  # offline / unreachable / malformed — stay quiet
        _write_cache(path, latest, now)

    if latest and parse_version(latest) > parse_version(__version__):
        print(
            f"A newer slithyt is available: {__version__} -> {latest}. "
            f"Run: slithyt update",
            file=out,
        )
