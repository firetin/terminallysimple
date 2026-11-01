"""Tests for the app-level services (Pomodoro clock and weather state)."""

from __future__ import annotations

from pathlib import Path

import pytest

import services
from config import Config
from services import PomodoroService, WeatherService


# --------------------------------------------------------------------- pomodoro
class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_pomodoro_counts_down_without_drift() -> None:
    clock = FakeClock()
    service = PomodoroService(work_seconds=100, clock=clock)
    service.start()

    clock.advance(40)

    assert service.remaining == 60
    assert service.formatted_remaining() == "01:00"
    assert service.is_running


def test_pomodoro_pause_and_resume() -> None:
    clock = FakeClock()
    service = PomodoroService(work_seconds=100, clock=clock)
    service.start()
    clock.advance(30)
    service.pause()

    clock.advance(500)  # time does not run while paused
    assert service.remaining == 70
    assert service.is_paused

    service.start()
    clock.advance(10)
    assert service.remaining == 60


def test_pomodoro_cycles_through_breaks() -> None:
    clock = FakeClock()
    service = PomodoroService(
        work_seconds=10,
        short_break_seconds=4,
        long_break_seconds=7,
        cycles_before_long_break=2,
        clock=clock,
    )

    service.start()
    clock.advance(10)
    assert service.tick() == PomodoroService.WORK
    assert service.session_type == PomodoroService.SHORT_BREAK
    assert service.remaining == 4
    assert service.work_count == 1

    service.start()
    clock.advance(4)
    assert service.tick() == PomodoroService.SHORT_BREAK
    assert service.session_type == PomodoroService.WORK

    service.start()
    clock.advance(10)
    assert service.tick() == PomodoroService.WORK
    assert service.session_type == PomodoroService.LONG_BREAK  # 2nd cycle
    assert service.remaining == 7


def test_pomodoro_reset() -> None:
    clock = FakeClock()
    service = PomodoroService(work_seconds=100, clock=clock)
    service.start()
    clock.advance(50)
    service.reset()

    assert service.is_idle
    assert service.remaining == 100
    assert service.work_count == 0
    assert service.session_type == PomodoroService.WORK


def test_pomodoro_listeners_are_notified() -> None:
    service = PomodoroService(work_seconds=10)
    calls: list[str] = []
    remove = service.add_listener(lambda: calls.append("tick"))

    service.start()
    remove()
    service.reset()

    assert calls == ["tick"]


# ---------------------------------------------------------------------- weather
TOKYO_PAYLOAD = {
    "timezone": "Asia/Tokyo",
    "current_units": {"temperature_2m": "\u00b0C"},
    "current": {"time": "2026-11-01T20:00", "temperature_2m": 19.4, "weather_code": 3},
    "hourly": {
        "time": [f"2026-11-01T{h:02d}:00" for h in range(18, 24)],
        "temperature_2m": [18.0, 18.5, 19.0, 19.4, 19.0, 18.2],
        "weather_code": [1, 2, 3, 3, 2, 1],
    },
}


def test_forecast_starts_at_city_local_time() -> None:
    from utils.weather import parse_hourly_forecast

    forecast = parse_hourly_forecast(TOKYO_PAYLOAD, hours=4)

    assert [entry.time for entry in forecast] == ["20:00", "21:00", "22:00", "23:00"]


def test_forecast_step() -> None:
    from utils.weather import parse_hourly_forecast

    forecast = parse_hourly_forecast(TOKYO_PAYLOAD, hours=3, step=2)

    assert [entry.time for entry in forecast] == ["20:00", "22:00"]


def test_current_weather_parsing() -> None:
    from utils.weather import parse_current_weather

    current = parse_current_weather(TOKYO_PAYLOAD)

    assert current is not None
    assert current.temperature == pytest.approx(19.4)
    assert current.unit == "\u00b0C"
    assert current.description == "Overcast"


def test_parse_rejects_garbage() -> None:
    from utils.weather import parse_current_weather, parse_hourly_forecast

    assert parse_current_weather({}) is None
    assert parse_hourly_forecast({}) == []


def test_weather_service_uses_disk_cache(tmp_path: Path) -> None:
    cfg = Config(tmp_path / "config.json")
    cfg.set("weather_city", "Tokyo, Japan")
    cfg.set("weather_latitude", 35.68)
    cfg.set("weather_longitude", 139.69)

    service = WeatherService(cfg, cache_file=tmp_path / "weather.json")
    assert service.is_configured
    assert service.load_cached() is False  # nothing cached yet

    service.current = None
    service._store_cache(TOKYO_PAYLOAD)

    reloaded = WeatherService(cfg, cache_file=tmp_path / "weather.json")
    assert reloaded.load_cached() is True
    assert reloaded.current is not None
    assert reloaded.forecast[0].time == "20:00"


async def test_weather_refresh_failure_sets_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = Config(tmp_path / "config.json")
    cfg.set("weather_city", "Nowhere")
    cfg.set("weather_latitude", 1.0)
    cfg.set("weather_longitude", 2.0)
    service = WeatherService(cfg, cache_file=tmp_path / "weather.json")

    async def fake_fetch(*args, **kwargs):
        return None

    monkeypatch.setattr(services, "fetch_weather", fake_fetch)

    assert await service.refresh(force=True) is False
    assert service.error is not None
    assert service.loading is False
