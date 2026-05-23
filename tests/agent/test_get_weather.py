from agent.tools.get_weather import get_weather


class FakeWeatherClient:
    def __init__(self, forecast):
        self.forecast = forecast
        self.calls = []

    def forecast(self, **kwargs):  # pragma: no cover - intentionally shadowed by instance attr if misused
        raise AssertionError("instance forecast data should be used through get_forecast")

    def get_forecast(self, **kwargs):
        self.calls.append(kwargs)
        return self.forecast


def test_get_weather_returns_daily_forecast_for_requested_date_from_injected_client():
    """Weather should come from injected Open-Meteo-style forecast data with no live network."""
    client = FakeWeatherClient(
        {
            "daily": {
                "time": ["2026-07-05", "2026-07-06"],
                "temperature_2m_max": [29.4, 30.1],
                "temperature_2m_min": [20.2, 21.0],
                "precipitation_sum": [1.6, 0.0],
                "weather_code": [3, 0],
            }
        }
    )

    result = get_weather(lat=35.6762, lng=139.6503, date="2026-07-05", weather_client=client)

    assert result == {
        "high_c": 29.4,
        "low_c": 20.2,
        "precipitation_mm": 1.6,
        "condition": "overcast",
    }
    assert client.calls == [
        {
            "lat": 35.6762,
            "lng": 139.6503,
            "start_date": "2026-07-05",
            "end_date": "2026-07-05",
        }
    ]


def test_get_weather_maps_rain_codes_to_rain_condition():
    """Rainy Open-Meteo weather codes should produce a simple rain condition for UI copy."""
    client = FakeWeatherClient(
        {
            "daily": {
                "time": ["2026-07-07"],
                "temperature_2m_max": [24.0],
                "temperature_2m_min": [18.5],
                "precipitation_sum": [12.2],
                "weather_code": [63],
            }
        }
    )

    result = get_weather(lat=35.6762, lng=139.6503, date="2026-07-07", weather_client=client)

    assert result["condition"] == "rain"
    assert result["precipitation_mm"] == 12.2


def test_get_weather_returns_standard_error_when_date_is_missing():
    """Missing forecast dates should fail loud with a standard tool error shape."""
    client = FakeWeatherClient(
        {
            "daily": {
                "time": ["2026-07-05"],
                "temperature_2m_max": [29.4],
                "temperature_2m_min": [20.2],
                "precipitation_sum": [1.6],
                "weather_code": [3],
            }
        }
    )

    result = get_weather(lat=35.6762, lng=139.6503, date="2026-07-08", weather_client=client)

    assert result == {
        "error": {
            "code": "WEATHER_DATE_NOT_FOUND",
            "message": "Weather forecast not found for 2026-07-08.",
        }
    }
