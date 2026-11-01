"""
Weather service using the Open-Meteo API.

No API key required - completely free and open-source.
Docs: https://open-meteo.com/en/docs

All parsing helpers are pure functions over the decoded JSON payload so they
can be unit-tested against recorded fixtures (no network needed).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Final, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx

logger = logging.getLogger(__name__)

# Open-Meteo API endpoints
GEOCODING_API: Final[str] = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API: Final[str] = "https://api.open-meteo.com/v1/forecast"

# Weather cache settings
CACHE_DURATION_MINUTES: Final[int] = 30

#: ``celsius`` / ``fahrenheit``
VALID_UNITS: Final[tuple[str, ...]] = ("celsius", "fahrenheit")


@dataclass(frozen=True)
class CurrentWeather:
    """Current conditions for a location."""

    temperature: float
    weather_code: int
    icon: str
    description: str
    unit: str = "°C"


@dataclass(frozen=True)
class HourlyForecast:
    """One entry of the hourly forecast."""

    time: str
    temperature: float
    weather_code: int
    icon: str
    description: str
    unit: str = "°C"


class WeatherCache:
    """Simple in-memory cache for weather data, keyed by coordinates."""

    def __init__(self) -> None:
        self.data: Optional[dict[str, Any]] = None
        self.timestamp: Optional[datetime] = None
        self.key: Optional[tuple[float, float, str]] = None

    def is_valid(self, key: Optional[tuple[float, float, str]] = None) -> bool:
        """Check whether the cached payload is still usable for ``key``."""
        if self.data is None or self.timestamp is None:
            return False
        if key is not None and self.key != key:
            return False
        return datetime.now() - self.timestamp < timedelta(minutes=CACHE_DURATION_MINUTES)

    def set(self, data: dict[str, Any], key: Optional[tuple[float, float, str]] = None) -> None:
        """Store data in the cache."""
        self.data = data
        self.timestamp = datetime.now()
        self.key = key

    def get(self, key: Optional[tuple[float, float, str]] = None) -> Optional[dict[str, Any]]:
        """Get cached data if valid for ``key``."""
        return self.data if self.is_valid(key) else None

    def clear(self) -> None:
        self.data = None
        self.timestamp = None
        self.key = None


# Global weather cache
_weather_cache: WeatherCache = WeatherCache()


def _cache_key(latitude: float, longitude: float, units: str) -> tuple[float, float, str]:
    return (round(float(latitude), 4), round(float(longitude), 4), units)


def get_weather_icon(weather_code: int) -> str:
    """
    Convert a WMO weather code to an icon.

    WMO Weather interpretation codes (WW):
    0: Clear sky
    1, 2, 3: Mainly clear, partly cloudy, and overcast
    45, 48: Fog
    51, 53, 55: Drizzle
    56, 57: Freezing drizzle
    61, 63, 65: Rain
    66, 67: Freezing rain
    71, 73, 75: Snow fall
    77: Snow grains
    80, 81, 82: Rain showers
    85, 86: Snow showers
    95: Thunderstorm
    96, 99: Thunderstorm with hail
    """
    if weather_code in (0, 1):
        return "☀️"
    if weather_code in (2, 3):
        return "☁️"
    if weather_code in (45, 48):
        return "🌫️"
    if weather_code in (51, 53, 55, 56, 57):
        return "💧"
    if weather_code in (61, 63, 65) or weather_code in (66, 67):
        return "🌧️"
    if weather_code in (71, 73, 75, 77):
        return "❄️"
    if weather_code in (80, 81, 82):
        return "🌧️"
    if weather_code in (85, 86):
        return "🌨️"
    if weather_code >= 95:
        return "⛈️"
    return "🌤️"


def get_weather_description(weather_code: int) -> str:
    """Get human-readable weather description."""
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Rime fog",
        51: "Light drizzle",
        53: "Drizzle",
        55: "Heavy drizzle",
        56: "Freezing drizzle",
        57: "Freezing drizzle",
        61: "Light rain",
        63: "Rain",
        65: "Heavy rain",
        66: "Freezing rain",
        67: "Freezing rain",
        71: "Light snow",
        73: "Snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Light showers",
        81: "Showers",
        82: "Heavy showers",
        85: "Light snow showers",
        86: "Snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with hail",
    }
    return descriptions.get(weather_code, "Unknown")


async def geocode_city(city_name: str) -> Optional[tuple[str, float, float]]:
    """
    Convert a city name to coordinates using the Open-Meteo Geocoding API.

    Returns:
        ``(full_city_name, latitude, longitude)`` or ``None`` when not found.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                GEOCODING_API,
                params={"name": city_name, "count": 1, "language": "en", "format": "json"},
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("results")
            if not results:
                logger.warning("City not found: %s", city_name)
                return None

            result = results[0]
            full_name = result.get("name", city_name)
            country = result.get("country", "")
            if country:
                full_name = f"{full_name}, {country}"

            return (full_name, float(result["latitude"]), float(result["longitude"]))

    except httpx.TimeoutException:
        logger.error("Timeout geocoding city: %s", city_name)
    except httpx.HTTPError as e:
        logger.error("HTTP error geocoding city: %s", e)
    except (KeyError, TypeError, ValueError) as e:
        logger.error("Error parsing geocoding response: %s", e)
    return None


async def fetch_weather(
    latitude: float,
    longitude: float,
    use_cache: bool = True,
    units: str = "celsius",
) -> Optional[dict[str, Any]]:
    """
    Fetch current weather and hourly forecast from Open-Meteo.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        use_cache: Reuse the in-memory cache when it matches the location.
        units: ``celsius`` or ``fahrenheit``.
    """
    if units not in VALID_UNITS:
        units = "celsius"

    key = _cache_key(latitude, longitude, units)
    if use_cache:
        cached = _weather_cache.get(key)
        if cached:
            logger.debug("Using cached weather data")
            return cached

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                WEATHER_API,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,weather_code,wind_speed_10m",
                    "hourly": "temperature_2m,weather_code,precipitation_probability",
                    "timezone": "auto",
                    "temperature_unit": units,
                    "forecast_days": 2,
                },
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()

        _weather_cache.set(data, key)
        logger.debug("Fetched weather for (%.3f, %.3f)", latitude, longitude)
        return data

    except httpx.TimeoutException:
        logger.error("Timeout fetching weather data")
    except httpx.HTTPError as e:
        logger.error("HTTP error fetching weather: %s", e)
    except (KeyError, TypeError, ValueError) as e:
        logger.error("Error parsing weather response: %s", e)
    return None


def _unit_symbol(data: dict[str, Any]) -> str:
    units = data.get("current_units") or {}
    symbol = units.get("temperature_2m")
    return symbol if isinstance(symbol, str) else "°C"


def parse_current_weather(data: dict[str, Any]) -> Optional[CurrentWeather]:
    """Parse the ``current`` block of an Open-Meteo response."""
    try:
        current = data["current"]
        weather_code = int(current["weather_code"])
        return CurrentWeather(
            temperature=float(current["temperature_2m"]),
            weather_code=weather_code,
            icon=get_weather_icon(weather_code),
            description=get_weather_description(weather_code),
            unit=_unit_symbol(data),
        )
    except (KeyError, TypeError, ValueError) as e:
        logger.error("Error parsing current weather: %s", e)
        return None


def city_timezone(data: dict[str, Any]) -> Optional[ZoneInfo]:
    """Return the location's timezone as a ``ZoneInfo`` (``None`` if unknown)."""
    name = data.get("timezone")
    if not isinstance(name, str) or not name:
        return None
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        logger.warning("Unknown timezone %r in weather payload", name)
        return None


def _reference_time(data: dict[str, Any]) -> Optional[datetime]:
    """
    The API's own idea of "now" in the location's timezone.

    Falls back to the device clock when ``current.time`` is missing.
    """
    tz = city_timezone(data)
    current = data.get("current") or {}
    stamp = current.get("time")
    if isinstance(stamp, str):
        try:
            parsed = datetime.fromisoformat(stamp)
            return parsed.replace(tzinfo=tz) if tz else parsed
        except ValueError:
            pass
    return datetime.now(tz) if tz else datetime.now()


def parse_hourly_forecast(
    data: dict[str, Any],
    hours: int = 12,
    step: int = 1,
) -> list[HourlyForecast]:
    """
    Parse the hourly forecast starting at the location's current hour.

    Args:
        data: Weather API response.
        hours: Maximum number of entries to return.
        step: Take every ``step``-th hour (4 gives a 4-hourly overview).

    The comparison is done in the *location's* timezone (the API returns local
    times because the request uses ``timezone=auto``), which used to make
    forecasts for far-away cities show hours in the past.
    """
    try:
        hourly = data["hourly"]
        times = hourly["time"]
        temperatures = hourly["temperature_2m"]
        weather_codes = hourly["weather_code"]
    except (KeyError, TypeError) as e:
        logger.error("Error parsing hourly forecast: %s", e)
        return []

    tz = city_timezone(data)
    reference = _reference_time(data)
    step = max(1, step)

    forecast: list[HourlyForecast] = []
    index = 0
    while index < len(times):
        try:
            raw_time = times[index]
            forecast_time = datetime.fromisoformat(raw_time)
            if tz is not None:
                forecast_time = forecast_time.replace(tzinfo=tz)
        except (ValueError, TypeError):
            index += 1
            continue

        try:
            temperature = float(temperatures[index])
            weather_code = int(weather_codes[index])
        except (IndexError, TypeError, ValueError):
            index += 1
            continue

        if forecast_time >= reference - timedelta(minutes=59):
            forecast.append(
                HourlyForecast(
                    time=forecast_time.strftime("%H:%M"),
                    temperature=temperature,
                    weather_code=weather_code,
                    icon=get_weather_icon(weather_code),
                    description=get_weather_description(weather_code),
                    unit=_unit_symbol(data),
                )
            )
            if len(forecast) >= hours:
                break
            index += step
        else:
            index += 1

    return forecast


def clear_cache() -> None:
    """Drop the in-memory weather cache (used by tests)."""
    _weather_cache.clear()
