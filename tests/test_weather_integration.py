"""Optional network test for the Open-Meteo integration.

Skipped by default; run with ``RUN_NETWORK_TESTS=1 pytest -m integration``.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from config import Config
from services import WeatherService

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("RUN_NETWORK_TESTS") != "1",
        reason="set RUN_NETWORK_TESTS=1 to hit the real Open-Meteo API",
    ),
]


def _hours_apart(first: str, second: str) -> int:
    a = int(first.split(":")[0])
    b = int(second.split(":")[0])
    return (a - b) % 24


async def test_real_forecast_starts_at_the_citys_local_hour(tmp_path: Path) -> None:
    cfg = Config(tmp_path / "config.json")
    service = WeatherService(cfg, cache_file=tmp_path / "weather.json")

    assert await service.set_city("Tokyo") is True
    assert service.error is None
    assert service.current is not None
    assert service.forecast, "expected a non-empty hourly forecast"

    city_hour = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%H:%M")
    assert _hours_apart(service.forecast[0].time, city_hour) <= 1, (
        f"forecast starts at {service.forecast[0].time} but Tokyo time is {city_hour}"
    )
