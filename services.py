"""
Application services.

State that must survive screen changes (the Pomodoro clock, the weather data)
lives here instead of inside widgets: every screen rebuilds its header, but the
service is owned by the ``App`` and keeps running.

Both services are plain Python (no Textual imports) so they can be unit tested
without an event loop. Screens subscribe with ``add_listener`` to be told when
they should re-render.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from config import Config
from config import config as global_config
from utils import paths, storage
from utils.weather import (
    CurrentWeather,
    DailyForecast,
    HourlyForecast,
    fetch_weather,
    geocode_city,
    parse_current_weather,
    parse_daily_forecast,
    parse_hourly_forecast,
)

logger = logging.getLogger(__name__)

Listener = Callable[[], None]


class _Observable:
    """Minimal observer support shared by the services."""

    def __init__(self) -> None:
        self._listeners: list[Listener] = []

    def add_listener(self, listener: Listener) -> Callable[[], None]:
        """Register ``listener``; returns a callable that removes it again."""
        if listener not in self._listeners:
            self._listeners.append(listener)

        def remove() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return remove

    def _notify(self) -> None:
        for listener in list(self._listeners):
            try:
                listener()
            except Exception:  # pragma: no cover - a bad listener must not break state
                logger.exception("Service listener failed")


class PomodoroService(_Observable):
    """Pomodoro clock driven by a monotonic deadline (no drift, no per-screen state)."""

    WORK = "Work"
    SHORT_BREAK = "Short Break"
    LONG_BREAK = "Long Break"

    def __init__(
        self,
        work_seconds: int = 25 * 60,
        short_break_seconds: int = 5 * 60,
        long_break_seconds: int = 15 * 60,
        cycles_before_long_break: int = 4,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        super().__init__()
        self.work_seconds = work_seconds
        self.short_break_seconds = short_break_seconds
        self.long_break_seconds = long_break_seconds
        self.cycles_before_long_break = max(1, cycles_before_long_break)
        self._clock = clock

        self.session_type: str = self.WORK
        self.work_count: int = 0
        self._deadline: float | None = None
        self._paused = False
        self._remaining: int = work_seconds

    # ------------------------------------------------------------------ state
    @property
    def is_running(self) -> bool:
        return self._deadline is not None and not self._paused

    @property
    def is_paused(self) -> bool:
        return self._deadline is not None and self._paused

    @property
    def is_idle(self) -> bool:
        return self._deadline is None

    @property
    def duration(self) -> int:
        """Length of the current session in seconds."""
        return {
            self.WORK: self.work_seconds,
            self.SHORT_BREAK: self.short_break_seconds,
            self.LONG_BREAK: self.long_break_seconds,
        }[self.session_type]

    @property
    def remaining(self) -> int:
        """Seconds left in the current session."""
        if self._deadline is None or self._paused:
            return self._remaining
        return max(0, int(round(self._deadline - self._clock())))

    def formatted_remaining(self) -> str:
        remaining = self.remaining
        return f"{remaining // 60:02d}:{remaining % 60:02d}"

    # ---------------------------------------------------------------- control
    def start(self) -> None:
        """Start or resume the current session."""
        if self.is_running:
            return
        self._deadline = self._clock() + self._remaining
        self._paused = False
        self._notify()

    def pause(self) -> None:
        """Pause the session, remembering the remaining time."""
        if not self.is_running:
            return
        self._remaining = self.remaining
        self._paused = True
        self._deadline = self._clock() + self._remaining
        self._notify()

    def reset(self) -> None:
        """Stop and return to a fresh work session."""
        self._deadline = None
        self._paused = False
        self.session_type = self.WORK
        self.work_count = 0
        self._remaining = self.work_seconds
        self._notify()

    def _set_session(self, session_type: str, seconds: int) -> None:
        self.session_type = session_type
        self._remaining = seconds
        self._deadline = None
        self._paused = False

    def tick(self) -> str | None:
        """
        Advance the clock.

        Returns the name of the session that just finished (so the caller can
        notify the user), or ``None`` when nothing happened.
        """
        if not self.is_running:
            return None

        if self.remaining > 0:
            self._notify()
            return None

        finished = self.session_type
        if finished == self.WORK:
            self.work_count += 1
            if self.work_count % self.cycles_before_long_break == 0:
                self._set_session(self.LONG_BREAK, self.long_break_seconds)
            else:
                self._set_session(self.SHORT_BREAK, self.short_break_seconds)
        else:
            self._set_session(self.WORK, self.work_seconds)

        self._notify()
        return finished


class WeatherService(_Observable):
    """Holds the weather configuration/data for the whole app."""

    def __init__(self, config_obj: Config | None = None, cache_file: Path | None = None) -> None:
        super().__init__()
        self._config = config_obj or global_config
        self._cache_file = cache_file

        self.city: str | None = None
        self.latitude: float | None = None
        self.longitude: float | None = None
        self.current: CurrentWeather | None = None
        self.forecast: list[HourlyForecast] = []
        self.daily: list[DailyForecast] = []
        self.last_updated: datetime | None = None
        self.error: str | None = None
        self.loading: bool = False
        self.load_from_config()

    # ------------------------------------------------------------------ paths
    @property
    def cache_file(self) -> Path:
        return self._cache_file or paths.data_dir() / "weather-cache.json"

    # ----------------------------------------------------------------- config
    @property
    def units(self) -> str:
        units = self._config.get("weather_units", "celsius")
        return units if units in ("celsius", "fahrenheit") else "celsius"

    @property
    def is_configured(self) -> bool:
        return self.city is not None and self.latitude is not None and self.longitude is not None

    def load_from_config(self) -> None:
        """Read the saved location from the config file."""
        self.city = self._config.get("weather_city")
        self.latitude = self._config.get("weather_latitude")
        self.longitude = self._config.get("weather_longitude")

    def _save_config(self) -> None:
        self._config.update(
            {
                "weather_city": self.city,
                "weather_latitude": self.latitude,
                "weather_longitude": self.longitude,
            }
        )
        self._config.save()

    # ------------------------------------------------------------------ cache
    def load_cached(self) -> bool:
        """Load the last payload from disk so the header is useful offline."""
        payload = storage.load_json(self.cache_file, default=None)
        if not isinstance(payload, dict):
            return False
        if payload.get("city") != self.city or payload.get("units") != self.units:
            return False

        data = payload.get("data")
        if not isinstance(data, dict):
            return False

        current = parse_current_weather(data)
        if current is None:
            return False

        self.current = current
        self.forecast = parse_hourly_forecast(data, hours=8, step=3)
        self.daily = parse_daily_forecast(data, days=3)
        stamp = payload.get("fetched_at")
        try:
            self.last_updated = datetime.fromisoformat(stamp) if isinstance(stamp, str) else None
        except ValueError:
            self.last_updated = None
        self._notify()
        return True

    def _store_cache(self, data: dict[str, Any]) -> None:
        storage.save_json_atomic(
            self.cache_file,
            {
                "city": self.city,
                "units": self.units,
                "fetched_at": datetime.now().isoformat(timespec="seconds"),
                "data": data,
            },
        )

    # ------------------------------------------------------------------ fetch
    async def set_city(self, city_name: str, *, force: bool = True) -> bool:
        """Geocode ``city_name``, store it and refresh the weather."""
        result = await geocode_city(city_name)
        if result is None:
            self.error = f"City not found: {city_name}"
            self.loading = False
            self._notify()
            return False

        self.city, self.latitude, self.longitude = result
        self._save_config()
        self.last_updated = None
        self.current = None
        self.forecast = []
        self.daily = []
        return await self.refresh(force=force)

    async def refresh(self, *, force: bool = False) -> bool:
        """Fetch current conditions + forecast for the configured location."""
        if not self.is_configured:
            self.error = "Weather is not configured yet"
            self._notify()
            return False

        assert self.latitude is not None and self.longitude is not None
        self.loading = True
        self.error = None
        self._notify()

        try:
            data = await fetch_weather(
                self.latitude, self.longitude, use_cache=not force, units=self.units
            )
        except Exception as e:  # pragma: no cover - defensive
            logger.exception("Unexpected error fetching weather")
            data = None
            self.error = str(e)

        if not isinstance(data, dict):
            self.loading = False
            self.error = self.error or "Could not reach Open-Meteo"
            self._notify()
            return False

        current = parse_current_weather(data)
        if current is None:
            self.loading = False
            self.error = "Could not read the weather response"
            self._notify()
            return False

        self.current = current
        self.forecast = parse_hourly_forecast(data, hours=8, step=3)
        self.daily = parse_daily_forecast(data, days=3)
        self.last_updated = datetime.now()
        self.loading = False
        self.error = None
        self._store_cache(data)
        self._notify()
        return True
