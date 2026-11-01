"""Tests for the newer user-facing features."""

from __future__ import annotations

from textual.widgets import Input, TextArea

from app import TerminallySimple
from dialogs.weather_dialogs import WeatherForecastDialog
from editor import EditorScreen
from utils import paths
from utils.weather import parse_current_weather, parse_daily_forecast, parse_hourly_forecast

PAYLOAD = {
    "timezone": "Asia/Tokyo",
    "current_units": {"temperature_2m": "\u00b0C"},
    "current": {"time": "2026-11-01T20:00", "temperature_2m": 19.4, "weather_code": 3},
    "hourly": {
        "time": [f"2026-11-01T{h:02d}:00" for h in range(20, 24)],
        "temperature_2m": [19.0, 18.5, 18.0, 17.5],
        "weather_code": [3, 2, 1, 0],
    },
    "daily": {
        "time": ["2026-11-01", "2026-11-02", "2026-11-03"],
        "temperature_2m_max": [21.0, 19.0, 18.0],
        "temperature_2m_min": [12.0, 11.0, 10.0],
        "weather_code": [3, 61, 0],
    },
}


# ------------------------------------------------------------------- daily
def test_daily_forecast_parsing() -> None:
    daily = parse_daily_forecast(PAYLOAD, days=3)

    assert [day.weekday for day in daily] == ["Sun", "Mon", "Tue"]
    assert daily[0].temperature_max == 21.0
    assert daily[1].description == "Light rain"
    assert daily[0].unit == "\u00b0C"


def test_daily_forecast_limited_by_days() -> None:
    assert len(parse_daily_forecast(PAYLOAD, days=2)) == 2


def test_daily_forecast_missing_block() -> None:
    assert parse_daily_forecast({}) == []


async def test_forecast_dialog_renders_daily_and_hourly_rows() -> None:
    current = parse_current_weather(PAYLOAD)
    hourly = parse_hourly_forecast(PAYLOAD, hours=4)
    daily = parse_daily_forecast(PAYLOAD, days=3)

    app = TerminallySimple()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.push_screen(
            WeatherForecastDialog(
                city_name="Tokyo, Japan", current=current, forecast=hourly, daily=daily
            )
        )
        await pilot.pause()

        rows = app.screen.query(".forecast-item")
        assert len(rows) == len(daily) + len(hourly)
        text = " ".join(str(row.render()) for row in rows)
        assert "Sun" in text and "Light rain" in text


# ------------------------------------------------------------- last note
async def test_last_note_is_reopened_on_start() -> None:
    paths.ensure_dir(paths.notes_dir())
    note = paths.notes_dir() / "yesterday.md"
    note.write_text("what I was writing", encoding="utf-8")

    from config import config

    config.set("last_file", str(note))
    config.save()

    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.press("1")
        await pilot.pause()

        editor = app.screen
        assert isinstance(editor, EditorScreen)
        assert editor.query_one(TextArea).text == "what I was writing"
        assert editor.current_file == note


async def test_status_bar_counts_words() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.press("1")
        await pilot.pause()
        app.screen.query_one(TextArea).load_text("one two three")
        await pilot.pause()

        status = app.screen.query_one("#editor-status")
        assert "3 words" in str(status.render())


# ------------------------------------------------------------------- undo
async def test_task_delete_can_be_undone() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await pilot.press("2")
        await pilot.pause()

        await pilot.press("a")
        await pilot.pause()
        app.screen.query_one("#task-input-field", Input).value = "keep me"
        await pilot.press("enter")
        await pilot.pause()

        await pilot.press("d")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()
        assert list(app.screen.query("TaskItem")) == []

        await pilot.press("ctrl+z")
        await pilot.pause()
        assert len(app.screen.query("TaskItem")) == 1

        reloaded = app.screen.storage.load_tasks()
        assert [t.text for t in reloaded] == ["keep me"]
