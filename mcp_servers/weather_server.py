from __future__ import annotations

from datetime import datetime, timezone
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Singapore Weather MCP",
    instructions="Provides current Singapore weather and forecast data from Open-Meteo."
)

LATITUDE = 1.3521
LONGITUDE = 103.8198
TIMEZONE = "Asia/Singapore"
URL = "https://api.open-meteo.com/v1/forecast"

CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


@mcp.tool()
def get_singapore_weather(forecast_days: int = 3) -> str:
    """Retrieve current conditions and a daily Singapore forecast from Open-Meteo."""

    if not 1 <= forecast_days <= 16:
        return "TOOL_ERROR: forecast_days must be between 1 and 16."

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "timezone": TIMEZONE,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum",
        "forecast_days": forecast_days,
    }

    try:
        r = requests.get(URL, params=params, timeout=20)
        r.raise_for_status()

        data = r.json()
        cur = data["current"]
        daily = data["daily"]

        lines = [
            "MCP_SOURCE: Open-Meteo",
            f"retrieved_at: {cur.get('time')}",
            f"current_temperature_c: {cur.get('temperature_2m')}",
            f"current_condition: {CODES.get(cur.get('weather_code'), 'Unknown')}",
            f"current_precipitation_mm: {cur.get('precipitation')}",
            "FORECAST:"
        ]

        for i, day in enumerate(daily["time"]):
            lines.append(
                f"{day}: {CODES.get(daily['weather_code'][i], 'Unknown')}; "
                f"min_c={daily['temperature_2m_min'][i]}; "
                f"max_c={daily['temperature_2m_max'][i]}; "
                f"rain_probability_percent={daily['precipitation_probability_max'][i]}; "
                f"precipitation_mm={daily['precipitation_sum'][i]}"
            )

        return "\n".join(lines)

    except Exception as exc:
        return f"TOOL_ERROR: Weather service unavailable: {exc}"


if __name__ == "__main__":
    mcp.run(transport="stdio")