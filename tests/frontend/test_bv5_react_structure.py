"""Structural guarantees for the canonical v5 React prototype build.

WHY these matter: PRD v5 §AI BUILD specifies an L1 prototype that runs as a
single self-contained HTML file with NO browser storage and NO network calls
for prototype state. The build we adopted (Fariz-approved, 2026-06-09) is a
bundler artifact that inlines React, ReactDOM, Babel-standalone and every image
as base64. If any of those guarantees regress, the prototype stops being a
demo-safe single file (it would phone home to a CDN, or leak state across
sessions), so each assertion below pins one of those L1 invariants.
"""
import re

import pytest

from react_build import (
    CLOUDRUN,
    FRONTEND,
    app_source,
    lib_first_bytes,
    raw_html,
)


def test_frontend_and_cloudrun_builds_are_byte_identical():
    # WHY: the deployed prototype must be exactly what we test locally; a drift
    # between the two would let a green local suite hide a broken deploy.
    assert FRONTEND.read_bytes() == CLOUDRUN.read_bytes()


def test_build_is_a_self_contained_bundler_artifact():
    # WHY: a single-file L1 prototype has its manifest/template/assets inline.
    html = raw_html()
    assert '<script type="__bundler/manifest">' in html
    assert '<script type="__bundler/template">' in html
    assert app_source(), "decoded application source must be recoverable"


def test_react_reactdom_and_babel_are_inlined_not_loaded_from_a_cdn():
    # WHY: the PRD allows a Babel CDN exception, but the adopted build inlines
    # the toolchain so the demo works fully offline. Guard against a regression
    # that swaps the inline blobs back for <script src="https://...cdn">.
    libs = lib_first_bytes()
    assert "react.development.js" in libs
    assert "react-dom.development.js" in libs


def test_no_external_network_hosts_are_referenced():
    # WHY: "no external requests" is the demo-safety promise. The only allowed
    # absolute URL is the SVG xmlns (w3.org), which is a namespace string the
    # browser never fetches. Anything else (fonts, CDNs, analytics) is a leak.
    html = raw_html()
    hosts = {
        m.split("/")[2]
        for m in re.findall(r'https?://[^\\"\'\s)]+', html)
        if "//" in m
    }
    assert hosts <= {"www.w3.org"}, f"unexpected external hosts: {hosts}"


def test_no_browser_storage_or_fetch_apis_in_application_source():
    # WHY: L1 keeps all state in React memory. localStorage/fetch/SSE would make
    # the prototype claim persistence/backends it does not have.
    src = app_source()
    for banned in (
        "localStorage",
        "sessionStorage",
        "XMLHttpRequest",
        "EventSource",
    ):
        assert banned not in src, f"{banned} must not appear in L1 app source"
    # The bundler's own unpack loader uses fetch() against blob: URLs only; the
    # application code itself must never fetch.
    assert "fetch(" not in src


def test_google_maps_script_is_runtime_loaded_from_injected_key():
    # WHY: the itinerary map must be a real Google Maps widget in the hosted
    # prototype, but the browser-visible API key must still be injected by the
    # Cloud Run server instead of committed into the static artifact.
    src = app_source()
    assert "getGoogleMapsApiKey" in src
    assert "google-maps-api-key" in raw_html()
    assert "https://maps.googleapis.com/maps/api/js" in src
    assert "new google.maps.Map" in src
    assert "GoogleMapCard" in src


@pytest.mark.parametrize("path", [str(FRONTEND), str(CLOUDRUN)])
def test_no_hardcoded_google_maps_key_in_either_build(path):
    # WHY: Google Maps uses a browser-visible key injected by Cloud Run at
    # runtime. The committed single-file artifact must never contain a real key.
    assert "AIza" not in raw_html(path)
