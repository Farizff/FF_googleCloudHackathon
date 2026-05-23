from typing import Any


WEATHER_DATE_NOT_FOUND = "WEATHER_DATE_NOT_FOUND"

WEATHER_CODE_CONDITIONS = {
    0: "clear",
    1: "partly cloudy",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "fog",
    51: "drizzle",
    53: "drizzle",
    55: "drizzle",
    56: "freezing drizzle",
    57: "freezing drizzle",
    61: "rain",
    63: "rain",
    65: "rain",
    66: "freezing rain",
    67: "freezing rain",
    71: "snow",
    73: "snow",
    75: "snow",
    77: "snow",
    80: "rain showers",
    81: "rain showers",
    82: "rain showers",
    85: "snow showers",
    86: "snow showers",
    95: "thunderstorm",
    96: "thunderstorm",
    99: "thunderstorm",
}


def get_weather(lat: float, lng: float, date: str, weather_client: Any) -> dict[str, Any]:
    """Return daily weather for a date using an injected Open-Meteo-style client."""
    forecast = weather_client.get_forecast(
        lat=lat,
        lng=lng,
        start_date=date,
        end_date=date,
    )
    daily = forecast["daily"]
    dates = daily["time"]

    if date not in dates:
        return {
            "error": {
                "code": WEATHER_DATE_NOT_FOUND,
                "message": f"Weather forecast not found for {date}.",
            }
        }

    index = dates.index(date)
    weather_code = daily["weather_code"][index]
    return {
        "high_c": daily["temperature_2m_max"][index],
        "low_c": daily["temperature_2m_min"][index],
        "precipitation_mm": daily["precipitation_sum"][index],
        "condition": WEATHER_CODE_CONDITIONS.get(weather_code, "unknown"),
    }
