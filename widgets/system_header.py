"""
System header: CPU/RAM, screen title, Pomodoro timer, weather and a clock.

The header is a pure view. State lives in :mod:`services` (owned by the app),
so navigating between screens no longer resets the timer or refetches the
weather, and every element is a real, mounted widget laid out by CSS instead of
hand-padded strings.
"""

from __future__ import annotations

import contextlib
import logging
from datetime import datetime
from typing import Any

import psutil
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Static

logger = logging.getLogger(__name__)

#: Below these widths optional parts of the header are hidden so it never
#: overflows a narrow terminal.
HIDE_CLOCK_BELOW = 70
HIDE_WEATHER_BELOW = 52
HIDE_POMODORO_BELOW = 36


class PomodoroWidget(Static):
    """Compact Pomodoro status; click to open the control dialog."""

    can_focus = False

    def on_mount(self) -> None:
        self._remove_listener: Any | None = None
        service = getattr(self.app, "pomodoro", None)
        if service is not None:
            self._remove_listener = service.add_listener(self.refresh)

    def on_unmount(self) -> None:
        if self._remove_listener is not None:
            self._remove_listener()
            self._remove_listener = None

    def render(self) -> Text:
        service = getattr(self.app, "pomodoro", None)
        if service is None:
            return Text("⏹ 25:00", style="dim")

        if service.is_running:
            icon = "🍅"
            style = "bold"
        elif service.is_paused:
            icon = "⏸"
            style = "yellow"
        else:
            icon = "⏹"
            style = "dim"

        return Text(f"{icon} {service.formatted_remaining()}", style=style)

    def on_click(self) -> None:
        action = getattr(self.app, "action_show_pomodoro", None)
        if callable(action):
            action()


class WeatherWidget(Static):
    """Compact current weather; click to open the forecast."""

    can_focus = False

    def on_mount(self) -> None:
        self._remove_listener: Any | None = None
        service = getattr(self.app, "weather", None)
        if service is not None:
            self._remove_listener = service.add_listener(self.refresh)

    def on_unmount(self) -> None:
        if self._remove_listener is not None:
            self._remove_listener()
            self._remove_listener = None

    def render(self) -> Text:
        service = getattr(self.app, "weather", None)
        if service is None or not service.is_configured:
            return Text("Weather", style="dim")
        if service.loading and service.current is None:
            return Text("…", style="dim")
        if service.current is None:
            message = "Weather!" if service.error else "Weather"
            return Text(message, style="yellow" if service.error else "dim")

        current = service.current
        return Text(f"{current.icon} {current.temperature:.0f}{current.unit}")

    def on_click(self) -> None:
        action = getattr(self.app, "action_show_weather", None)
        if callable(action):
            action()


class SystemHeader(Widget):
    """Header widget with CPU/RAM usage, title, Pomodoro, weather and clock."""

    DEFAULT_CSS = """
    SystemHeader {
        dock: top;
        width: 100%;
        height: 1;
        background: $panel;
        color: $text;
        layout: horizontal;
    }

    SystemHeader > Static {
        height: 1;
        background: $panel;
        color: $text;
    }

    #header-left {
        width: auto;
        padding: 0 1;
    }

    #header-title {
        width: 1fr;
        text-align: center;
        text-style: bold;
        color: $text-muted;
    }

    #header-right {
        width: auto;
        height: 1;
        background: $panel;
    }

    #header-clock {
        width: auto;
        padding: 0 1;
        color: $text-muted;
    }

    PomodoroWidget, WeatherWidget {
        width: auto;
        height: 1;
        padding: 0 1;
        background: $panel;
    }

    PomodoroWidget:hover, WeatherWidget:hover {
        background: $boost;
        text-style: bold;
    }
    """

    def __init__(
        self,
        show_clock: bool = True,
        show_weather: bool = True,
        show_pomodoro: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.show_clock = show_clock
        self.show_weather = show_weather
        self.show_pomodoro = show_pomodoro
        self._header_timer: Any | None = None

    def compose(self) -> ComposeResult:
        """Compose the three header regions."""
        yield Static(id="header-left")
        yield Static(id="header-title")
        with Horizontal(id="header-right"):
            if self.show_pomodoro:
                yield PomodoroWidget(id="pomodoro-widget")
            if self.show_weather:
                yield WeatherWidget(id="weather-widget")
            if self.show_clock:
                yield Static(id="header-clock")

    def on_mount(self) -> None:
        """Start the one-second refresh and paint immediately."""
        self._refresh_header()
        self._header_timer = self.set_interval(1.0, self._refresh_header)

    def on_unmount(self) -> None:
        if self._header_timer is not None:
            self._header_timer.stop()
            self._header_timer = None

    def on_resize(self) -> None:
        self._refresh_header()

    # ------------------------------------------------------------------ render
    def _refresh_header(self) -> None:
        """Update the header regions from the services and system stats."""
        width = self.size.width
        if width <= 0:
            return

        self._apply_responsive_layout(width)

        try:
            left = self.query_one("#header-left", Static)
            title = self.query_one("#header-title", Static)
        except Exception:  # pragma: no cover - during teardown
            return

        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        left.update(
            Text.assemble(
                (f"CPU {cpu:3.0f}%", self._usage_style(cpu)),
                ("  ", ""),
                (f"RAM {ram:3.0f}%", self._usage_style(ram)),
            )
        )

        screen_title = getattr(self.screen, "title", "") or "Terminally Simple"
        title.update(Text(str(screen_title), overflow="ellipsis", no_wrap=True))

        if self.show_clock:
            with contextlib.suppress(Exception):  # hidden/removed during teardown
                self.query_one("#header-clock", Static).update(datetime.now().strftime("%X"))

    def _apply_responsive_layout(self, width: int) -> None:
        """Hide optional elements that would not fit in ``width`` columns."""
        self._set_visible("#header-clock", self.show_clock and width >= HIDE_CLOCK_BELOW)
        self._set_visible("#weather-widget", self.show_weather and width >= HIDE_WEATHER_BELOW)
        self._set_visible("#pomodoro-widget", self.show_pomodoro and width >= HIDE_POMODORO_BELOW)

    def _set_visible(self, selector: str, visible: bool) -> None:
        try:
            widget = self.query_one(selector)
        except Exception:  # pragma: no cover - widget not composed
            return
        if widget.display != visible:
            widget.display = visible

    @staticmethod
    def _usage_style(percent: float) -> str:
        if percent < 70:
            return "green"
        if percent < 90:
            return "yellow"
        return "red"
