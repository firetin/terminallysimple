"""Settings interface for customizing the app."""

from __future__ import annotations

import logging
from typing import Any, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.events import Click
from textual.widget import Widget
from textual.widgets import Footer, Static

from base_screen import NavigableScreen
from config import config
from constants import FOCUS_COLOR, FOCUS_INDICATOR, SELECTED_MARKER, UNSELECTED_MARKER, WidgetIDs
from widgets.system_header import SystemHeader

logger = logging.getLogger(__name__)


class SettingOption(Static):
    """A selectable setting option."""

    def __init__(self, label: str, value: str, selected: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.value = value
        self.selected = selected
        self.can_focus = True

    def render(self) -> str:
        """Render the option."""
        marker = SELECTED_MARKER if self.selected else UNSELECTED_MARKER
        if self.has_focus:
            return f"[{FOCUS_COLOR}]{FOCUS_INDICATOR} {marker}[/] [bold]{self.label}[/]"
        return f"  {marker}  {self.label}"

    def on_focus(self) -> None:
        self.refresh()

    def on_blur(self) -> None:
        self.refresh()


class SettingsScreen(NavigableScreen):
    """Settings screen for theme and unit customization."""

    THEMES: list[tuple[str, str]] = [
        ("Dark", "textual-dark"),
        ("Light", "textual-light"),
        ("Nord", "nord"),
        ("Gruvbox", "gruvbox"),
        ("Catppuccin Mocha", "catppuccin-mocha"),
        ("Catppuccin Latte", "catppuccin-latte"),
        ("Dracula", "dracula"),
        ("Tokyo Night", "tokyo-night"),
        ("Monokai", "monokai"),
        ("Flexoki", "flexoki"),
        ("Solarized Light", "solarized-light"),
    ]

    UNITS: list[tuple[str, str]] = [
        ("Celsius (\u00b0C)", "celsius"),
        ("Fahrenheit (\u00b0F)", "fahrenheit"),
    ]

    BINDINGS = [
        Binding("escape", "back", "Back", priority=True),
        Binding("s", "save", "Save", show=True),
        Binding("r", "reset", "Reset", show=True),
        Binding("enter", "toggle", "Select", show=True),
        Binding("down,j", "cursor_down", "Next", show=False),
        Binding("up,k", "cursor_up", "Previous", show=False),
    ]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.saved_theme: str = config.get("theme", "textual-dark")
        self.saved_units: str = config.get("weather_units", "celsius")
        self.pending_theme: str = self.saved_theme
        self.pending_units: str = self.saved_units

    def compose(self) -> ComposeResult:
        """Create the settings interface."""
        yield SystemHeader(show_clock=True)
        yield Container(
            Static("SETTINGS", id=WidgetIDs.SETTINGS_TITLE),
            Static("Theme", id=WidgetIDs.SETTINGS_SUBTITLE),
            Static(
                "[dim]Tip: Ctrl+W opens the weather, Ctrl+P the Pomodoro timer, ? shows help[/]",
                id=WidgetIDs.SETTINGS_TIP,
            ),
            Vertical(
                *(
                    SettingOption(
                        label,
                        value,
                        selected=(value == self.pending_theme),
                        id=f"opt-{value}",
                    )
                    for label, value in self.THEMES
                ),
                id=WidgetIDs.THEME_LIST,
            ),
            Static("Temperature units", id=WidgetIDs.SETTINGS_UNITS_TITLE),
            Vertical(
                *(
                    SettingOption(
                        label,
                        value,
                        selected=(value == self.pending_units),
                        id=f"unit-{value}",
                        classes="unit-option",
                    )
                    for label, value in self.UNITS
                ),
                id=WidgetIDs.UNIT_LIST,
            ),
            Static("", id=WidgetIDs.SETTINGS_STATUS),
            id=WidgetIDs.SETTINGS_CONTAINER,
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus the currently selected theme."""
        try:
            self.query_one(f"#opt-{self.pending_theme}").focus()
        except Exception:  # pragma: no cover - unknown theme in config
            first = self.query(SettingOption).first()
            if first is not None:
                first.focus()

    def on_click(self, event: Click) -> None:
        """Handle clicks on options."""
        if isinstance(event.widget, SettingOption):
            self._toggle_option(event.widget)

    def action_toggle(self) -> None:
        """Toggle the focused option."""
        focused = self.focused
        if isinstance(focused, SettingOption):
            self._toggle_option(focused)

    def _toggle_option(self, option: SettingOption) -> None:
        """Select an option and preview it without persisting anything."""
        is_unit = "unit-" in (option.id or "")

        for other in self.query(SettingOption):
            other_is_unit = "unit-" in (other.id or "")
            if other_is_unit == is_unit and other.selected:
                other.selected = False
                other.refresh()

        option.selected = True
        option.refresh()

        if is_unit:
            self.pending_units = option.value
        else:
            self.pending_theme = option.value
            self.app.preview_theme(option.value)  # preview only; not persisted

        self._update_status("Preview - press 's' to save, Escape to cancel")

    def action_save(self) -> None:
        """Persist the selected settings and apply the theme."""
        config.set("weather_units", self.pending_units)
        config.set("theme", self.pending_theme)

        if not config.save():
            self._update_status("\u2717 Error saving settings")
            return

        self.saved_theme = self.pending_theme
        self.saved_units = self.pending_units
        self.app.save_theme(self.pending_theme)
        self._update_status("\u2713 Saved and applied!")

        weather = getattr(self.app, "weather", None)
        if weather is not None:
            weather.load_from_config()
            self.run_worker(weather.refresh(force=True), group="weather")

    def action_reset(self) -> None:
        """Restore the defaults for the values shown on this screen."""
        self.pending_theme = config.DEFAULT_CONFIG["theme"]
        self.pending_units = config.DEFAULT_CONFIG["weather_units"]

        for option in self.query(SettingOption):
            option.selected = "unit-" in (option.id or "") and option.value == self.pending_units
            if not ("unit-" in (option.id or "")):
                option.selected = option.value == self.pending_theme
            option.refresh()

        self.app.preview_theme(self.pending_theme)
        self._update_status("Reset to defaults - press 's' to save")

    def action_back(self) -> None:
        """Leave the screen, discarding the preview."""
        self.app.apply_theme_from_config()
        self.app.pop_screen()

    def get_focusable_items(self) -> list[Widget]:
        return list(self.query(SettingOption))

    def _update_status(self, message: str) -> None:
        try:
            self.query_one(f"#{WidgetIDs.SETTINGS_STATUS}", Static).update(message)
        except Exception:  # pragma: no cover - during teardown
            pass


SettingsScreen.CSS = """
#settings-container {
    border: solid $primary;
    width: 80%;
    max-width: 80;
    height: auto;
    align: center middle;
    padding: 2;
    background: $surface;
}

#settings-title {
    text-align: center;
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}

#settings-subtitle, #settings-units-title {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
    margin-bottom: 1;
}

#settings-tip {
    text-align: center;
    color: $text-muted;
    margin-bottom: 2;
}

#theme-list, #unit-list {
    height: auto;
    max-height: 12;
    overflow-y: auto;
}

SettingOption {
    height: auto;
    padding: 0 2;
    margin: 0;
}

SettingOption:focus {
    background: $boost;
}

#settings-status {
    text-align: center;
    color: $success;
    padding: 1;
    margin-top: 1;
    min-height: 1;
}
"""
