"""
Custom header with system resource monitoring and weather
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List

import psutil
from rich.text import Text
from textual.app import ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widgets import Static
from textual.widget import Widget
from textual.events import Resize, Click
from textual.worker import Worker, WorkerState

from config import config
from utils.weather import (
    geocode_city, fetch_weather, parse_current_weather, parse_hourly_forecast
)

logger = logging.getLogger(__name__)


class WeatherWidget(Static, can_focus=False):
    """Clickable weather widget that shows current weather."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.weather_data: Optional[Dict] = None
        self.city_name: str = ""
        self.temperature: Optional[float] = None
        self.weather_icon: str = "🌤️"
        self.is_configured: bool = False
    
    def render(self) -> str:
        """Render the weather widget."""
        if not self.is_configured:
            return "[dim]Weather[/]"
        elif self.temperature is not None:
            return f"{self.weather_icon} {self.temperature:.0f}°C"
        else:
            return "[dim]N/A[/]"
    
    def update_weather(self, city_name: str, temperature: float, icon: str, data: Dict) -> None:
        """Update weather display."""
        self.city_name = city_name
        self.temperature = temperature
        self.weather_icon = icon
        self.weather_data = data
        self.is_configured = True
        self.refresh()
    
    def clear_weather(self) -> None:
        """Clear weather data."""
        self.temperature = None
        self.weather_icon = "🌤️"
        self.is_configured = False
        self.refresh()


class SystemHeader(Widget):
    """Header widget with CPU, RAM usage, and weather display."""
    
    DEFAULT_CSS = """
    SystemHeader {
        dock: top;
        width: 100%;
        height: 1;
        background: $panel;
        color: $text;
    }
    
    SystemHeader > Static {
        width: 100%;
        height: 1;
        padding: 0 1;
        background: $panel;
        color: $text;
    }
    
    WeatherWidget {
        width: auto;
        height: 1;
        background: $panel;
        color: $text;
    }
    
    WeatherWidget:hover {
        text-style: bold;
        color: $accent;
    }
    """
    
    cpu_usage: reactive[float] = reactive(0.0)
    ram_usage: reactive[float] = reactive(0.0)
    
    def __init__(self, show_clock: bool = True, show_weather: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        self.show_clock = show_clock
        self.show_weather = show_weather
        self._update_timer: Optional[object] = None
        self._weather_timer: Optional[object] = None
        self.weather_widget: Optional[WeatherWidget] = None
    
    def compose(self) -> ComposeResult:
        """Compose the header with a Static widget for content."""
        yield Static(id="header-content")
        if self.show_weather:
            self.weather_widget = WeatherWidget(id="weather-widget")
    
    def on_mount(self) -> None:
        """Start the resource monitoring when mounted."""
        # Initial update
        self._update_display()
        # Update system stats every second
        self._update_timer = self.set_interval(1.0, self._update_system_stats, pause=False)
        
        # Initialize and update weather if configured
        if self.show_weather:
            self._load_weather_from_config()
            # Update weather every 30 minutes
            self._weather_timer = self.set_interval(1800.0, self._refresh_weather, pause=False)
    
    def on_unmount(self) -> None:
        """Stop the resource monitoring when unmounted."""
        if self._update_timer:
            self._update_timer.stop()
        if self._weather_timer:
            self._weather_timer.stop()
    
    def on_resize(self, event: Resize) -> None:
        """Handle resize events to ensure proper layout."""
        self._update_display()
    
    def _update_system_stats(self) -> None:
        """Update CPU and RAM usage statistics."""
        try:
            # Get CPU usage (non-blocking, interval=None uses previous call)
            self.cpu_usage = psutil.cpu_percent(interval=None)
            
            # Get RAM usage
            memory = psutil.virtual_memory()
            self.ram_usage = memory.percent
            
            # Update the display
            self._update_display()
        except Exception as e:
            logger.debug(f"Failed to update system stats: {e}")
    
    def _update_display(self) -> None:
        """Update the header display content."""
        try:
            static_widget = self.query_one("#header-content", Static)
            
            # Get screen title
            title = self.screen.title if (self.screen and self.screen.title) else "Terminally Simple"
            
            # Format CPU and RAM with color coding
            cpu_color = "green" if self.cpu_usage < 70 else ("yellow" if self.cpu_usage < 90 else "red")
            ram_color = "green" if self.ram_usage < 70 else ("yellow" if self.ram_usage < 90 else "red")
            
            # Build the left side (CPU and RAM)
            left_text = f"CPU: {self.cpu_usage:3.0f}%  RAM: {self.ram_usage:3.0f}%"
            left_length = len(left_text)
            
            # Build the right side (weather + clock)
            weather_str = ""
            if self.show_weather and self.weather_widget:
                weather_str = self.weather_widget.render()
                # Strip markup for length calculation
                import re
                weather_length = len(re.sub(r'\[.*?\]', '', weather_str))
            else:
                weather_length = 0
            
            time_str = datetime.now().strftime("%X") if self.show_clock else ""
            
            # Calculate right side total length
            right_length = weather_length + (3 if weather_length > 0 else 0) + len(time_str)
            
            # Calculate center position for title
            title_str = str(title)
            title_length = len(title_str)
            
            # Calculate total width - ensure we have a valid size
            total_width = self.size.width
            
            # If size is not yet available (0), skip the update
            if total_width == 0:
                return
            
            # To center the title in the entire width, we need to position it at:
            # (total_width / 2) - (title_length / 2)
            # But we already have left_text taking up space, so:
            # padding_needed = center_position - left_length
            center_position = (total_width - title_length) // 2
            left_padding = max(1, center_position - left_length)
            
            # Right padding to fill remaining space before weather/clock
            right_padding = max(1, total_width - left_length - left_padding - title_length - right_length)
            
            # Build the complete header text
            header_text = Text()
            
            # Left side: CPU and RAM
            header_text.append(f"CPU: {self.cpu_usage:3.0f}%", style=cpu_color)
            header_text.append("  ")
            header_text.append(f"RAM: {self.ram_usage:3.0f}%", style=ram_color)
            
            # Padding to center
            header_text.append(" " * left_padding)
            
            # Centered title
            header_text.append(title_str)
            
            # Padding before weather/clock
            header_text.append(" " * right_padding)
            
            # Right side: Weather (if enabled)
            if self.show_weather and weather_str:
                from rich.markup import render
                header_text.append_text(render(weather_str))
                header_text.append("  ")
            
            # Clock
            if self.show_clock:
                header_text.append(time_str)
            
            static_widget.update(header_text)
        except Exception as e:
            logger.debug(f"Failed to update display: {e}")
    
    def on_click(self, event: Click) -> None:
        """Handle clicks on the header."""
        # Check if the click is in the right area (weather widget area)
        if self.show_weather and event.widget.id == "header-content":
            # Weather is on the right side - check if click is in the right third
            click_x = event.screen_x
            widget_width = event.widget.size.width
            
            # Weather is in the right portion of the header
            if click_x > widget_width * 2 // 3:
                self._handle_weather_click()
    
    def _handle_weather_click(self) -> None:
        """Handle click on weather widget."""
        if not self.weather_widget:
            return
        
        if not self.weather_widget.is_configured:
            # Show city input dialog
            self._show_city_input()
        else:
            # Show forecast dialog
            self._show_forecast()
    
    def _show_city_input(self) -> None:
        """Show dialog to input city name."""
        from dialogs.weather_dialogs import CityInputDialog
        
        def handle_city_input(city_name: Optional[str]) -> None:
            if city_name:
                # Start geocoding and weather fetch
                self._setup_weather(city_name)
        
        self.app.push_screen(CityInputDialog(), handle_city_input)
    
    def _setup_weather(self, city_name: str) -> None:
        """Setup weather for a city (geocode and fetch)."""
        # Use a worker to avoid blocking the UI
        self.run_worker(self._setup_weather_async(city_name), exclusive=True)
    
    async def _setup_weather_async(self, city_name: str) -> None:
        """Async worker to setup weather."""
        try:
            # Geocode the city
            result = await geocode_city(city_name)
            if not result:
                logger.error(f"Could not find city: {city_name}")
                return
            
            full_name, latitude, longitude = result
            
            # Save to config
            config.set("weather_city", full_name)
            config.set("weather_latitude", latitude)
            config.set("weather_longitude", longitude)
            config.save()
            
            # Fetch weather (force refresh, no cache)
            await self._fetch_and_update_weather(latitude, longitude, full_name, use_cache=False)
            
            # After weather is updated, show the forecast automatically
            self.call_after_refresh(self._show_forecast)
            
        except Exception as e:
            logger.error(f"Error setting up weather: {e}")
    
    def _load_weather_from_config(self) -> None:
        """Load weather configuration and fetch current weather."""
        city = config.get("weather_city")
        latitude = config.get("weather_latitude")
        longitude = config.get("weather_longitude")
        
        if city and latitude is not None and longitude is not None:
            # Start fetching weather (correct order: latitude, longitude)
            self.run_worker(
                self._fetch_and_update_weather(latitude, longitude, city),
                exclusive=True
            )
    
    def _refresh_weather(self) -> None:
        """Refresh weather data (called by timer)."""
        city = config.get("weather_city")
        latitude = config.get("weather_latitude")
        longitude = config.get("weather_longitude")
        
        if city and latitude is not None and longitude is not None:
            # Correct order: latitude, longitude
            self.run_worker(
                self._fetch_and_update_weather(latitude, longitude, city),
                exclusive=True
            )
    
    async def _fetch_and_update_weather(self, latitude: float, longitude: float, city_name: str, use_cache: bool = True) -> None:
        """Fetch weather and update the widget."""
        try:
            # Fetch weather data
            data = await fetch_weather(latitude, longitude, use_cache=use_cache)
            if not data:
                logger.error("Failed to fetch weather data")
                if self.weather_widget:
                    self.weather_widget.clear_weather()
                return
            
            # Parse current weather
            current = parse_current_weather(data)
            if not current:
                logger.error("Failed to parse weather data")
                if self.weather_widget:
                    self.weather_widget.clear_weather()
                return
            
            temperature, weather_code, icon = current
            
            # Update the weather widget
            if self.weather_widget:
                self.weather_widget.update_weather(city_name, temperature, icon, data)
            
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            if self.weather_widget:
                self.weather_widget.clear_weather()
    
    def _refresh_and_reopen_forecast(self) -> None:
        """Refresh weather data and reopen forecast."""
        city = config.get("weather_city")
        latitude = config.get("weather_latitude")
        longitude = config.get("weather_longitude")
        
        if city and latitude is not None and longitude is not None:
            # Refresh weather with no cache, then show forecast
            async def refresh_and_show():
                await self._fetch_and_update_weather(latitude, longitude, city, use_cache=False)
                # After refresh, show the forecast again
                self.call_after_refresh(self._show_forecast)
            
            self.run_worker(refresh_and_show(), exclusive=True)
    
    def _show_forecast(self) -> None:
        """Show detailed weather forecast."""
        if not self.weather_widget or not self.weather_widget.weather_data:
            return
        
        from dialogs.weather_dialogs import WeatherForecastDialog
        
        # Parse hourly forecast - get all available hours
        forecast = parse_hourly_forecast(self.weather_widget.weather_data, hours=24)
        
        # Filter to show every 4th entry for cleaner display
        filtered_forecast = []
        if len(forecast) > 0:
            # Take every 4th hour starting from the first available
            for i in range(0, len(forecast), 4):
                if i < len(forecast):
                    filtered_forecast.append(forecast[i])
        else:
            filtered_forecast = forecast
        
        # Callback for when user wants to change city
        def handle_change_city() -> None:
            self._show_city_input()
        
        # Callback for when user wants to refresh
        def handle_refresh() -> None:
            self._refresh_and_reopen_forecast()
        
        # Show forecast dialog
        self.app.push_screen(WeatherForecastDialog(
            city_name=self.weather_widget.city_name,
            current_temp=self.weather_widget.temperature,
            current_icon=self.weather_widget.weather_icon,
            forecast=filtered_forecast,
            on_change_city=handle_change_city,
            on_refresh=handle_refresh
        ))
