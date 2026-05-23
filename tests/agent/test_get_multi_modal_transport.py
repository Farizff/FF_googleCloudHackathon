from agent.tools.get_multi_modal_transport import get_multi_modal_transport


class FakeRome2RioClient:
    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def search(self, **kwargs):
        self.calls.append(kwargs)
        return self.routes


def test_get_multi_modal_transport_calls_rome2rio_and_returns_three_labelled_options():
    client = FakeRome2RioClient(
        [
            {"mode": "train", "duration_minutes": 42, "estimated_cost_usd": 18, "transfers": 1, "summary": "Narita Express"},
            {"mode": "taxi", "duration_minutes": 28, "estimated_cost_usd": 95, "transfers": 0, "summary": "Taxi"},
            {"mode": "bus", "duration_minutes": 55, "estimated_cost_usd": 9, "transfers": 0, "summary": "Airport Limousine Bus"},
            {"mode": "private_transfer", "duration_minutes": 35, "estimated_cost_usd": 120, "transfers": 0, "summary": "Private van"},
        ]
    )

    result = get_multi_modal_transport(
        origin={"lat": 35.772, "lng": 140.392},
        destination={"lat": 35.681, "lng": 139.767},
        date="2026-07-01",
        group_size=4,
        rome2rio_client=client,
    )

    assert client.calls == [
        {
            "origin": {"lat": 35.772, "lng": 140.392},
            "destination": {"lat": 35.681, "lng": 139.767},
            "date": "2026-07-01",
            "group_size": 4,
        }
    ]
    assert [option["tier"] for option in result["options"]] == ["budget", "recommended", "premium"]
    assert [option["mode"] for option in result["options"]] == ["bus", "train", "taxi"]


def test_get_multi_modal_transport_normalizes_rome2rio_response_shape():
    client = FakeRome2RioClient(
        {
            "routes": [
                {
                    "name": "Subway + walk",
                    "distance": 12.4,
                    "duration": 3600,
                    "indicativePrices": [{"price": 4.5, "currency": "USD"}],
                    "segments": [{"kind": "train"}, {"kind": "walk"}],
                }
            ]
        }
    )

    result = get_multi_modal_transport(
        "Shinjuku Station",
        "teamLab Borderless",
        "2026-07-04",
        8,
        client,
    )

    assert result == {
        "options": [
            {
                "tier": "recommended",
                "mode": "train+walk",
                "duration_minutes": 60,
                "estimated_cost_usd": 4.5,
                "transfers": 1,
                "summary": "Subway + walk",
                "group_transport_note": "8 people: chartered minibus (~$80) or 2 taxis (~$95 total).",
            }
        ]
    }


def test_get_multi_modal_transport_deduplicates_modes_before_ranking():
    client = FakeRome2RioClient(
        [
            {"mode": "train", "duration_minutes": 50, "estimated_cost_usd": 12, "summary": "Slow train"},
            {"mode": "train", "duration_minutes": 40, "estimated_cost_usd": 12, "summary": "Fast train"},
            {"mode": "bus", "duration_minutes": 60, "estimated_cost_usd": 8, "summary": "Bus"},
            {"mode": "taxi", "duration_minutes": 25, "estimated_cost_usd": 70, "summary": "Taxi"},
        ]
    )

    result = get_multi_modal_transport("A", "B", "2026-07-04", 2, client)

    assert [option["summary"] for option in result["options"]] == ["Bus", "Fast train", "Taxi"]


def test_get_multi_modal_transport_returns_empty_list_when_no_routes():
    result = get_multi_modal_transport(
        "A",
        "B",
        "2026-07-04",
        2,
        FakeRome2RioClient({"routes": []}),
    )

    assert result == {"options": []}
