"""Weather-related dialog screens."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static

from constants import WidgetIDs
from utils.weather import CurrentWeather, HourlyForecast

logger = logging.getLogger(__name__)

#: Values returned by :class:`WeatherForecastDialog`.
ACTION_CHANGE_CITY = "change_city"
ACTION_REFRESH = "refresh"


class CityInputDialog(ModalScreen[str | None]):
    """Modal dialog for entering a city name for weather setup."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", priority=True),
    ]

    def compose(self) -> ComposeResult:
        """Create the city input dialog interface."""
        with Container(id=WidgetIDs.WEATHER_CITY_CONTAINER):
            yield Static("WEATHER SETUP", id=WidgetIDs.WEATHER_CITY_TITLE)
            yield Label("Enter your city name:", id=WidgetIDs.WEATHER_CITY_LABEL)
            yield Input(
                placeholder="e.g., London, New York, Tokyo", id=WidgetIDs.WEATHER_CITY_INPUT
            )
            yield Static("Press Enter to search, Escape to cancel", id=WidgetIDs.WEATHER_CITY_HINT)
            yield Static("", id=WidgetIDs.WEATHER_CITY_ERROR)

    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one(f"#{WidgetIDs.WEATHER_CITY_INPUT}", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        city_name = event.value.strip()
        if city_name:
            self.dismiss(city_name)
        else:
            self.show_error("Please enter a city name")

    def show_error(self, message: str) -> None:
        """Show error message."""
        self.query_one(f"#{WidgetIDs.WEATHER_CITY_ERROR}", Static).update(f"[red]{message}[/]")

    def action_cancel(self) -> None:
        """Cancel city input."""
        self.dismiss(None)


CityInputDialog.CSS = """
CityInputDialog {
    align: center middle;
}

#weather-city-container {
    border: double $primary;
    width: 60;
    height: auto;
    background: $surface;
    padding: 2;
}

#weather-city-title {
    text-align: center;
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}

#weather-city-label {
    color: $text;
    margin-bottom: 1;
}

#weather-city-input {
    margin-bottom: 1;
}

#weather-city-hint {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
}

#weather-city-error {
    text-align: center;
    color: $error;
    margin-top: 1;
    min-height: 1;
}
"""


class WeatherForecastDialog(ModalScreen[str | None]):
    """Modal dialog showing the current conditions and hourly forecast."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close", priority=True),
        Binding("enter", "dismiss", "Close", priority=True),
        Binding("c", "change_city", "Change City", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]

    def __init__(
        self,
        city_name: str,
        current: CurrentWeather | None,
        forecast: list[HourlyForecast],
        last_updated: datetime | None = None,
        error: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.city_name = city_name
        self.current = current
        self.forecast = forecast
        self.last_updated = last_updated
        self.error = error

    def compose(self) -> ComposeResult:
        """Create the forecast dialog interface."""
        with Container(id=WidgetIDs.WEATHER_FORECAST_CONTAINER):
            yield Static("WEATHER FORECAST", id=WidgetIDs.WEATHER_FORECAST_TITLE)
            yield Static(self._summary(), id=WidgetIDs.WEATHER_FORECAST_CURRENT)

            with Vertical(id=WidgetIDs.WEATHER_FORECAST_LIST):
                if self.forecast:
                    for entry in self.forecast:
                        yield Static(
                            f"{entry.time}  {entry.icon} {entry.temperature:.0f}{entry.unit}"
                            f"  {entry.description}",
                            classes="forecast-item",
                        )
                else:
                    yield Static("No forecast data available", classes="forecast-item")

            if self.last_updated is not None:
                yield Static(
                    f"Updated {self.last_updated.strftime('%H:%M')}",
                    id=WidgetIDs.WEATHER_FORECAST_UPDATED,
                )
            yield Static(
                "Press 'c' to change city, 'r' to refresh, Enter or Escape to close",
                id=WidgetIDs.WEATHER_FORECAST_HINT,
            )

    def _summary(self) -> str:
        if self.error and self.current is None:
            return f"[yellow]{self.error}[/]"
        if self.current is None:
            return "No weather data"

        current = self.current
        return (
            f"{self.city_name} - {current.icon} {current.temperature:.0f}{current.unit}"
            f"  [dim]{current.description}[/]"
        )

    async def action_dismiss(self, result: str | None = None) -> None:
        """Close the forecast dialog."""
        self.dismiss(None)

    def action_change_city(self) -> None:
        """Ask the app to show the city input dialog."""
        self.dismiss(ACTION_CHANGE_CITY)

    def action_refresh(self) -> None:
        """Ask the app to refresh the data."""
        self.dismiss(ACTION_REFRESH)


WeatherForecastDialog.CSS = """
WeatherForecastDialog {
    align: center middle;
}

#weather-forecast-container {
    border: double $secondary;
    width: 70;
    height: auto;
    max-height: 80%;
    background: $surface;
    padding: 2;
}

#weather-forecast-title {
    text-align: center;
    text-style: bold;
    color: $secondary;
    margin-bottom: 1;
}

#weather-forecast-current {
    text-align: center;
    color: $accent;
    text-style: bold;
    margin-bottom: 2;
}

#weather-forecast-list {
    height: auto;
    max-height: 30;
    overflow-y: auto;
    padding: 1;
}

.forecast-item {
    padding: 0 1;
    margin: 0;
    height: auto;
}

#weather-forecast-updated {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
}

#weather-forecast-hint {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
}
"""
