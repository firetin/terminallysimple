"""
Weather-related dialog screens
"""

import logging
from typing import List, Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static
from textual.binding import Binding

from constants import WidgetIDs

logger = logging.getLogger(__name__)


class CityInputDialog(ModalScreen):
    """Modal dialog for entering a city name for weather setup."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the city input dialog interface."""
        with Container(id=WidgetIDs.WEATHER_CITY_CONTAINER):
            yield Static("WEATHER SETUP", id=WidgetIDs.WEATHER_CITY_TITLE)
            yield Label("Enter your city name:", id=WidgetIDs.WEATHER_CITY_LABEL)
            yield Input(placeholder="e.g., London, New York, Tokyo", id=WidgetIDs.WEATHER_CITY_INPUT)
            yield Static("Press Enter to search, Escape to cancel", id=WidgetIDs.WEATHER_CITY_HINT)
            yield Static("", id=WidgetIDs.WEATHER_CITY_ERROR)
    
    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one(f"#{WidgetIDs.WEATHER_CITY_INPUT}").focus()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        city_name = event.value.strip()
        if city_name:
            self.dismiss(city_name)
        else:
            self.show_error("Please enter a city name")
    
    def show_error(self, message: str) -> None:
        """Show error message."""
        error_widget = self.query_one(f"#{WidgetIDs.WEATHER_CITY_ERROR}", Static)
        error_widget.update(f"[red]{message}[/]")
    
    def action_dismiss(self) -> None:
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


class WeatherForecastDialog(ModalScreen):
    """Modal dialog showing detailed weather forecast."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close", priority=True),
        Binding("enter", "dismiss", "Close", priority=True),
        Binding("c", "change_city", "Change City", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]
    
    def __init__(self, city_name: str, current_temp: float, current_icon: str, 
                 forecast: List[dict], on_change_city=None, on_refresh=None, **kwargs):
        super().__init__(**kwargs)
        self.city_name = city_name
        self.current_temp = current_temp
        self.current_icon = current_icon
        self.forecast = forecast
        self.on_change_city = on_change_city
        self.on_refresh = on_refresh
    
    def compose(self) -> ComposeResult:
        """Create the forecast dialog interface."""
        with Container(id=WidgetIDs.WEATHER_FORECAST_CONTAINER):
            yield Static("WEATHER FORECAST", id=WidgetIDs.WEATHER_FORECAST_TITLE)
            yield Static(
                f"{self.city_name} - {self.current_icon} {self.current_temp:.0f}°C",
                id=WidgetIDs.WEATHER_FORECAST_CURRENT
            )
            
            with Vertical(id=WidgetIDs.WEATHER_FORECAST_LIST):
                if self.forecast:
                    # Show forecast (every 4 hours)
                    for hour in self.forecast:
                        time_str = hour["time"]
                        temp = hour["temperature"]
                        icon = hour["icon"]
                        desc = hour["description"]
                        
                        yield Static(
                            f"{time_str}  {icon} {temp:.0f}°C  {desc}",
                            classes="forecast-item"
                        )
                else:
                    yield Static("No forecast data available", classes="forecast-item")
            
            yield Static("Press 'c' to change city, 'r' to refresh, Enter or Escape to close", id=WidgetIDs.WEATHER_FORECAST_HINT)
    
    def action_dismiss(self) -> None:
        """Close the forecast dialog."""
        self.dismiss()
    
    def action_change_city(self) -> None:
        """Handle change city action."""
        self.dismiss()  # Close forecast dialog
        if self.on_change_city:
            self.on_change_city()  # Trigger city input dialog
    
    def action_refresh(self) -> None:
        """Handle refresh action."""
        self.dismiss()  # Close forecast dialog
        if self.on_refresh:
            self.on_refresh()  # Trigger refresh and reopen


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

#weather-forecast-hint {
    text-align: center;
    color: $text-muted;
    margin-top: 2;
}
"""
