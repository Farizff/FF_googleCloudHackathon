"""Google Maps client — nearby search and directions.

Wraps Google Maps JavaScript API / Places API / Distance Matrix API.
Falls back to deterministic fake responses when GOOGLE_MAPS_API_KEY
is not set, so the disruption pipeline works in demo without live keys.
"""

from __future__ import annotations

import math
import random
from typing import Any

from api.settings import get_settings

# ---------------------------------------------------------------------------
# Real client
# ---------------------------------------------------------------------------


class GoogleMapsClient:
    """Thin wrapper around Google Maps services for Places nearby search and directions."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    # Places nearby search — returns a list of venue dicts
    def nearby_search(
        self,
        *,
        city: str,
        destination_country: str,
        date: str,
        place_types: list[str],
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Return venues matching place_types near the city centre.

        Uses the Places API nearby search.  Falls back to the static
        Tokyo seed data if the Places API key is absent.
        """
        # Import here so the module doesn't hard-fail when the key is absent.
        from googlemaps import Client as MapsClient

        gmaps = MapsClient(key=self._api_key)
        # Use Tokyo centre as a default when lat/lng not provided.
        lat, lng = 35.6762, 139.6503

        results = gmaps.places_nearby(
            location=(lat, lng),
            radius=3000,
            type=place_types[0] if place_types else "tourist_attraction",
        ).get("results", [])[:limit]

        venues = []
        for place in results:
            location = place.get("geometry", {}).get("location", {})
            rating = place.get("rating")
            opening_hours = None
            if place.get("opening_hours"):
                opening_hours = {"open_now": place["opening_hours"].get("open_now")}
            venues.append(
                {
                    "venue_id": place.get("place_id"),
                    "name": place.get("name"),
                    "types": place.get("types", []),
                    "rating": rating,
                    "coordinates": {"lat": location.get("lat"), "lng": location.get("lng")},
                    "opening_hours": opening_hours,
                    "photos": [],
                    "dietary_supported": [],
                }
            )
        return venues

    # Directions — returns route legs
    def get_directions(
        self,
        *,
        origin: dict[str, float],
        destination: dict[str, float],
        departure_time: int,
        mode: str = "transit",
    ) -> list[dict[str, Any]]:
        """Return directions from origin to destination using the Distance Matrix API."""
        from googlemaps import Client as MapsClient

        gmaps = MapsClient(key=self._api_key)
        result = gmaps.distance_matrix(
            origins=[origin],
            destinations=[destination],
            departure_time=departure_time,
            mode=mode,
        )
        rows = result.get("rows", [])
        if not rows:
            return [{"legs": [{}]}]
        elements = rows[0].get("elements", [])
        if not elements:
            return [{"legs": [{}]}]
        element = elements[0]
        return [
            {
                "legs": [
                    {
                        "duration": element.get("duration", {}),
                        "distance": element.get("distance", {}),
                        "duration_in_traffic": element.get("duration_in_traffic", element.get("duration", {})),
                    }
                ]
            }
        ]


# ---------------------------------------------------------------------------
# Deterministic fake client — works without API keys
# ---------------------------------------------------------------------------

TOKYO_VENUES = [
    {
        "venue_id": "mori_art_museum",
        "name": "Mori Art Museum",
        "types": ["museum", "tourist_attraction"],
        "rating": 4.5,
        "coordinates": {"lat": 35.6604, "lng": 139.7292},
        "opening_hours": {"open_now": True},
        "photos": [],
        "dietary_supported": [],
        "estimated_duration_minutes": 120,
    },
    {
        "venue_id": "ueno_park",
        "name": "Ueno Park",
        "types": ["park", "tourist_attraction"],
        "rating": 4.4,
        "coordinates": {"lat": 35.7148, "lng": 139.7737},
        "opening_hours": {"open_now": True},
        "photos": [],
        "dietary_supported": [],
        "estimated_duration_minutes": 90,
    },
    {
        "venue_id": "sensoji_temple",
        "name": "Senso-ji Temple",
        "types": ["place_of_worship", "tourist_attraction"],
        "rating": 4.6,
        "coordinates": {"lat": 35.7148, "lng": 139.7967},
        "opening_hours": {"open_now": True},
        "photos": [],
        "dietary_supported": [],
        "estimated_duration_minutes": 60,
    },
    {
        "venue_id": "shibuya_crossing",
        "name": "Shibuya Crossing",
        "types": ["point_of_interest"],
        "rating": 4.3,
        "coordinates": {"lat": 35.6595, "lng": 139.7004},
        "opening_hours": {"open_now": True},
        "photos": [],
        "dietary_supported": [],
        "estimated_duration_minutes": 30,
    },
    {
        "venue_id": "meiji_shrine",
        "name": "Meiji Shrine",
        "types": ["place_of_worship", "tourist_attraction"],
        "rating": 4.5,
        "coordinates": {"lat": 35.6764, "lng": 139.6993},
        "opening_hours": {"open_now": True},
        "photos": [],
        "dietary_supported": [],
        "estimated_duration_minutes": 75,
    },
    {
        "venue_id": "teamlab_borderless",
        "name": "teamLab Borderless",
        "types": ["museum", "tourist_attraction"],
        "rating": 4.4,
        "coordinates": {"lat": 35.6262, "lng": 139.7839},
        "opening_hours": {"open_now": False},
        "photos": [],
        "dietary_supported": [],
        "estimated_duration_minutes": 150,
    },
    {
        "venue_id": "ghibli_museum",
        "name": "Ghibli Museum",
        "types": ["museum", "tourist_attraction"],
        "rating": 4.6,
        "coordinates": {"lat": 35.6962, "lng": 139.5704},
        "opening_hours": {"open_now": True},
        "photos": [],
        "dietary_supported": [],
        "estimated_duration_minutes": 120,
    },
    {
        "venue_id": "tsukiji_market",
        "name": "Tsukiji Outer Market",
        "types": ["market", "food"],
        "rating": 4.5,
        "coordinates": {"lat": 35.6654, "lng": 139.7707},
        "opening_hours": {"open_now": True},
        "photos": [],
        "dietary_supported": ["seafood", "no_pork"],
        "estimated_duration_minutes": 90,
    },
    {
        "venue_id": "akihabara",
        "name": "Akihabara Electric Town",
        "types": ["shopping_mall", "store"],
        "rating": 4.2,
        "coordinates": {"lat": 35.7023, "lng": 139.7745},
        "opening_hours": {"open_now": True},
        "photos": [],
        "dietary_supported": [],
        "estimated_duration_minutes": 120,
    },
    {
        "venue_id": "harajuku_takeshita",
        "name": "Harajuku Takeshita Street",
        "types": ["shopping_mall", "store"],
        "rating": 4.3,
        "coordinates": {"lat": 35.6702, "lng": 139.7027},
        "opening_hours": {"open_now": True},
        "photos": [],
        "dietary_supported": [],
        "estimated_duration_minutes": 90,
    },
]

# Fake transit durations (km → rough transit minutes)
TRANSIT_SPEED_KM_MIN = 0.5  # ~30 km/h in city


def _fake_transit_time(
    origin: dict[str, float],
    destination: dict[str, float],
    group_size: int,
) -> dict[str, Any]:
    """Deterministic transit estimate between two coordinates."""
    dx = destination["lng"] - origin["lng"]
    dy = destination["lat"] - origin["lat"]
    dist_km = math.sqrt(dx * dx + dy * dy) * 111.0
    minutes = math.ceil(dist_km / TRANSIT_SPEED_KM_MIN)
    note = None
    if group_size > 6:
        taxis = math.ceil(group_size / 4)
        note = f"{group_size} people: chartered minibus (~$80) or {taxis} taxis (~$95 total)."
    return {"duration_minutes": minutes, "distance_km": round(dist_km, 2), "mode": "transit", "group_transport_note": note}


class FakeMapsClient:
    """Deterministic fake that returns static Tokyo venues and rough transit times."""

    def nearby_search(self, **kwargs) -> list[dict[str, Any]]:  # type: ignore[no-untyped-def]
        return TOKYO_VENUES

    def get_directions(self, *, origin, destination, departure_time=None, mode=None, group_size=1) -> list[dict[str, Any]]:  # type: ignore[no-untyped-def]
        transit = _fake_transit_time(origin, destination, group_size=group_size or 1)
        return [
            {
                "legs": [
                    {
                        "duration": {"value": transit["duration_minutes"] * 60},
                        "distance": {"value": int(transit["distance_km"] * 1000)},
                        "duration_in_traffic": {"value": transit["duration_minutes"] * 60},
                    }
                ]
            }
        ]


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def get_mapped_disruption_deps() -> dict[str, Any]:
    """Return a dict of the dependencies apply_disruption needs.

    Returns real Google Maps clients when GOOGLE_MAPS_API_KEY is set,
    otherwise deterministic fakes that work in demo without credentials.
    """
    settings = get_settings()
    api_key = settings.google_maps_api_key

    if api_key:
        client = GoogleMapsClient(api_key)
    else:
        client = FakeMapsClient()

    return {
        "places_client": client,
        "directions_client": client,
        "enrichment_collection": None,  # will be fetched from DB in the route
    }