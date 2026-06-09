"""Shared helpers for testing the v5 React prototype build.

The canonical v5 prototype (``frontend/bounce_v5_prototype.html`` and the
byte-identical ``cloudrun/bounce-v5-prototype/index.html``) is a *self-contained
bundler artifact*: React, ReactDOM, Babel-standalone and every image asset are
base64-encoded inside ``<script type="__bundler/manifest">`` and decoded to blob
URLs at runtime. The application source (JSX) lives inside the ``text/babel``
script assets, NOT as greppable plaintext in the file.

These helpers reproduce the runtime unpack just far enough to recover the
decoded application source so tests can assert on the *real* copy and behaviour
the user sees, instead of on bytes that never appear literally in the file.
"""
from __future__ import annotations

import base64
import gzip
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "bounce_v5_prototype.html"
CLOUDRUN = ROOT / "cloudrun" / "bounce-v5-prototype" / "index.html"


def _block(html: str, block_type: str) -> str:
    m = re.search(
        r'<script type="%s">(.*?)</script>' % re.escape(block_type), html, re.S
    )
    assert m, f"bundler block {block_type!r} missing from build"
    return m.group(1).strip()


@lru_cache(maxsize=2)
def raw_html(path: str = str(FRONTEND)) -> str:
    return Path(path).read_text(encoding="utf-8")


@lru_cache(maxsize=2)
def _manifest(path: str = str(FRONTEND)) -> dict:
    return json.loads(_block(raw_html(path), "__bundler/manifest"))


@lru_cache(maxsize=2)
def _template(path: str = str(FRONTEND)) -> str:
    return json.loads(_block(raw_html(path), "__bundler/template"))


def _decode(path: str, uuid: str) -> bytes:
    entry = _manifest(path)[uuid]
    raw = base64.b64decode(entry["data"])
    return gzip.decompress(raw) if entry.get("compressed") else raw


@lru_cache(maxsize=2)
def app_source(path: str = str(FRONTEND)) -> str:
    """Concatenated decoded source of every ``text/babel`` application script."""
    template = _template(path)
    babel_uuids = re.findall(
        r'<script type=\\?"text/babel\\?" src=\\?"([0-9a-f-]+)', template
    )
    assert babel_uuids, "no inline text/babel app scripts found in build"
    return "".join(_decode(path, u).decode("utf-8", "replace") for u in babel_uuids)


@lru_cache(maxsize=2)
def lib_first_bytes(path: str = str(FRONTEND)) -> str:
    """First bytes of each inline plain ``<script src>`` (React/ReactDOM/Babel)."""
    template = _template(path)
    uuids = re.findall(r'<script src=\\?"([0-9a-f-]+)', template)
    return "\n".join(_decode(path, u)[:200].decode("utf-8", "replace") for u in uuids)
