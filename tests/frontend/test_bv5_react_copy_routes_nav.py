"""Required v5 copy, navigation labels, and hash-route shape.

WHY these matter: the demo script and judges navigate by the exact labels and
hash routes defined in PRD/design v5. If a nav label or the hash-route parser
changes, deep links in the demo (and the Judge panel's phase/role switches)
break silently. These tests pin the user-visible vocabulary and the
``screen=…&phase=…&user=…`` deep-link contract.
"""
from react_build import app_source


def test_hash_route_parser_honors_screen_phase_and_user():
    # WHY: the v5 L1 route shape is screen=X&phase=Y&user=Z. The Judge panel and
    # demo deep links depend on all three keys being read from the hash.
    src = app_source()
    assert "parseHash" in src
    for key in ("hash.screen", "hash.phase", "hash.user"):
        assert key in src, f"hash route must read {key}"
    assert "window.location.hash" in src


def test_global_navigation_labels_present():
    # WHY: these are the primary entry points; the demo opens with them.
    src = app_source()
    for label in ("Home", "Plan a new trip", "Join a trip", "All trips"):
        assert label in src, f"missing nav label: {label}"


def test_trip_scoped_screen_labels_present():
    # WHY: every phase of a trip must be reachable; these labels are the
    # trip-scoped nav across planning/active/past phases.
    src = app_source()
    for label in (
        "Itinerary",
        "Flights",
        "Suggestions",
        "Today",
        "FlockMode",
        "Expenses",
        "Alerts",
        "Wrapped",
        "Profile",
    ):
        assert label in src, f"missing screen label: {label}"


def test_entry_conversation_hero_copy_is_exact():
    # WHY: this is the signature first-impression line from design v5; it is
    # quoted in the submission and must not drift.
    src = app_source()
    assert "Your trip starts here" in src
    assert "Tell me what" in src


def test_cut_scope_features_are_not_built():
    # WHY: scope contract forbids Travel DNA, dark mode, and multi-city trips as
    # features. Guard that they did not sneak in as real UI.
    src = app_source()
    assert "Travel DNA" not in src
    assert "dark mode" not in src
    # "multi-city" appears only in an internal fix comment, never as a feature
    # screen/route; assert there is no multi-city route or screen renderer.
    assert "MultiCity" not in src
    assert "multiCity" not in src
