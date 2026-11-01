#!/usr/bin/env python3
"""
Terminally Simple - A minimalist terminal application
One app. Essential tools. Zero distractions.
"""

from __future__ import annotations

import argparse
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.events import Click
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Footer, Static

from base_screen import NavigableScreen
from config import config
from constants import DIM_COLOR, FOCUS_COLOR, FOCUS_INDICATOR, FOCUS_TIMER_DELAY, WidgetIDs
from dialogs.pomodoro_dialogs import PomodoroDialog
from dialogs.weather_dialogs import (
    ACTION_CHANGE_CITY,
    ACTION_REFRESH,
    CityInputDialog,
    WeatherForecastDialog,
)
from editor import ConfirmDialog, EditorScreen
from services import PomodoroService, WeatherService
from settings import SettingsScreen
from tasks import TaskManagerScreen
from utils import paths
from widgets.system_header import SystemHeader

logger = logging.getLogger(__name__)

POMODORO_MESSAGES = {
    PomodoroService.WORK: "Work session complete! Time for a break.",
    PomodoroService.SHORT_BREAK: "Break over - back to work when you are ready.",
    PomodoroService.LONG_BREAK: "Long break over - back to work when you are ready.",
}


class MenuItem(Static, can_focus=True):
    """A clickable menu item."""

    DEFAULT_CSS = """
    MenuItem {
        height: auto;
        padding: 0 2;
        margin: 0;
    }

    MenuItem:focus {
        background: $boost;
    }
    """

    def __init__(self, label: str, key: str, description: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.key = key
        self.description = description

    def render(self) -> str:
        """Render the menu item, always showing the focus indicator."""
        if self.has_focus:
            return (
                f"[{FOCUS_COLOR}]{FOCUS_INDICATOR} {self.key}[/] [bold]{self.label}[/]"
                f"  [{DIM_COLOR}]{self.description}[/]"
            )
        return f"  {self.key}  {self.label}  [{DIM_COLOR}]{self.description}[/]"

    def on_focus(self) -> None:
        self.refresh()

    def on_blur(self) -> None:
        self.refresh()


class HelpScreen(ModalScreen[None]):
    """A generated list of the active key bindings."""

    BINDINGS = [
        Binding("escape,question_mark,f1,q", "dismiss", "Close", priority=True),
    ]

    def __init__(self, bindings: list[tuple[str, str]], context: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.bindings = bindings
        self.context = context

    def compose(self) -> ComposeResult:
        with Container(id=WidgetIDs.HELP_CONTAINER):
            yield Static(f"HELP{(' - ' + self.context) if self.context else ''}", id=WidgetIDs.HELP_TITLE)
            with Vertical(id=WidgetIDs.HELP_LIST):
                for key, description in self.bindings:
                    yield Static(f"[bold cyan]{key:<14}[/] {description}")
            yield Static("Press Escape or ? to close", id=WidgetIDs.HELP_HINT)

    def action_dismiss(self) -> None:  # type: ignore[override]
        self.dismiss(None)


HelpScreen.CSS = """
HelpScreen {
    align: center middle;
}

#help-container {
    border: double $accent;
    width: 70;
    max-width: 90%;
    height: auto;
    max-height: 80%;
    background: $surface;
    padding: 2;
}

#help-title {
    text-align: center;
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}

#help-list {
    height: auto;
    max-height: 30;
    overflow-y: auto;
}

#help-hint {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
}
"""


class MainMenu(NavigableScreen):
    """Main menu screen with tool selection."""

    BINDINGS = [
        Binding("1", "select_editor", "Editor", show=False),
        Binding("2", "select_tasks", "Tasks", show=False),
        Binding("3", "select_settings", "Settings", show=False),
        Binding("w", "app.show_weather", "Weather", show=True),
        Binding("p", "app.show_pomodoro", "Pomodoro", show=True),
        Binding("q", "app.quit", "Quit"),
        Binding("enter", "activate", "Select", show=True),
        Binding("down,j", "cursor_down", "Next", show=False),
        Binding("up,k", "cursor_up", "Previous", show=False),
    ]

    focused: Optional[Widget]

    def compose(self) -> ComposeResult:
        """Create child widgets for the menu."""
        yield SystemHeader(show_clock=True)
        yield Container(
            Static("TERMINALLY SIMPLE", id=WidgetIDs.TITLE),
            Static("One app. Essential tools. Zero distractions.", id=WidgetIDs.SUBTITLE),
            MenuItem("Text Editor", "1", "Distraction-free writing", id=WidgetIDs.ITEM_EDITOR),
            MenuItem("Task Manager", "2", "Simple to-do list", id=WidgetIDs.ITEM_TASKS),
            MenuItem("Settings", "3", "Customize theme and appearance", id=WidgetIDs.ITEM_SETTINGS),
            MenuItem("Help", "?", "Show all keyboard shortcuts", id=WidgetIDs.ITEM_HELP),
            MenuItem("Exit", "q", "Quit application", id=WidgetIDs.ITEM_EXIT),
            id=WidgetIDs.MENU_CONTAINER,
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus the first item once the screen is rendered."""
        self.call_after_refresh(self._focus_first_item)

    def _focus_first_item(self) -> None:
        try:
            self.set_focus(self.query_one(f"#{WidgetIDs.ITEM_EDITOR}"))
        except Exception:  # pragma: no cover - defensive
            logger.debug("Could not focus the first menu item")

    def on_click(self, event: Click) -> None:
        """Handle clicks on menu items."""
        if isinstance(event.widget, MenuItem) and event.widget.id:
            self._activate_item(event.widget.id)

    def _activate_item(self, item_id: str) -> None:
        if item_id == WidgetIDs.ITEM_EDITOR:
            self.action_select_editor()
        elif item_id == WidgetIDs.ITEM_TASKS:
            self.action_select_tasks()
        elif item_id == WidgetIDs.ITEM_SETTINGS:
            self.action_select_settings()
        elif item_id == WidgetIDs.ITEM_HELP:
            self.app.action_show_help()
        elif item_id == WidgetIDs.ITEM_EXIT:
            self.app.action_quit()

    def action_select_editor(self) -> None:
        self.app.push_screen(EditorScreen())

    def action_select_tasks(self) -> None:
        self.app.push_screen(TaskManagerScreen())

    def action_select_settings(self) -> None:
        self.app.push_screen(SettingsScreen())

    def action_activate(self) -> None:
        focused = self.focused
        if isinstance(focused, MenuItem) and focused.id:
            self._activate_item(focused.id)

    def get_focusable_items(self) -> list[Widget]:
        return list(self.query(MenuItem))


class TerminallySimple(App):
    """Main application class."""

    ENABLE_COMMAND_PALETTE = False
    TITLE = "Terminally Simple"

    BINDINGS = [
        # Priority bindings work even while a TextArea/Input has focus, which is
        # what makes "press it anywhere" true.
        Binding("ctrl+w", "show_weather", "Weather", show=True, priority=True),
        Binding("ctrl+p", "show_pomodoro", "Pomodoro", show=True, priority=True),
        Binding("question_mark,f1", "show_help", "Help", show=True, priority=True),
        Binding("ctrl+q", "quit", "Quit", show=True, priority=True),
    ]

    CSS = f"""
    Screen {{
        border: double $primary;
        background: $surface;
    }}

    #{WidgetIDs.MENU_CONTAINER} {{
        width: 100%;
        height: 100%;
        padding: 2 4;
        background: $surface;
    }}

    #{WidgetIDs.TITLE} {{
        text-align: left;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }}

    #{WidgetIDs.SUBTITLE} {{
        text-align: left;
        color: $text-muted;
        margin-bottom: 2;
    }}
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.pomodoro = PomodoroService()
        self.weather = WeatherService()
        self._persist_theme = True

    # ------------------------------------------------------------------ startup
    def on_mount(self) -> None:
        """Apply the saved theme, start services and show the menu."""
        paths.ensure_app_dirs()
        self.apply_theme_from_config()
        self.push_screen(MainMenu())

        self.set_interval(0.5, self._poll_pomodoro)
        self._bootstrap_weather()

    def _bootstrap_weather(self) -> None:
        """Show cached weather immediately, then refresh in the background."""
        self.weather.load_cached()
        if self.weather.is_configured:
            self.run_worker(self._refresh_weather(), group="weather")

    async def _refresh_weather(self) -> None:
        await self.weather.refresh()

    # ------------------------------------------------------------------- themes
    def apply_theme_from_config(self) -> None:
        """Apply the saved theme without persisting it again."""
        theme = config.get("theme", "textual-dark")
        if theme not in self.available_themes:
            logger.warning("Unknown theme %r, falling back to textual-dark", theme)
            theme = "textual-dark"
        previous = self._persist_theme
        self._persist_theme = False
        try:
            self.theme = theme
        finally:
            self._persist_theme = previous

    def watch_theme(self, theme: str) -> None:
        """Persist explicit theme changes (previews opt out via ``_persist_theme``)."""
        if not self._persist_theme:
            return
        config.set("theme", theme)
        config.save()

    def save_theme(self, theme: str) -> None:
        """Apply ``theme`` and make it the persistent choice."""
        config.set("theme", theme)
        config.save()
        self._apply_theme(theme)

    def preview_theme(self, theme: str) -> None:
        """Apply ``theme`` for a look-and-feel preview without persisting it."""
        self._apply_theme(theme)

    def _apply_theme(self, theme: str) -> None:
        previous = self._persist_theme
        self._persist_theme = False
        try:
            self.theme = theme
        finally:
            self._persist_theme = previous

    # --------------------------------------------------------------- pomodoro
    def _poll_pomodoro(self) -> None:
        finished = self.pomodoro.tick()
        if finished is None:
            return

        message = POMODORO_MESSAGES.get(finished, "Session complete")
        self.notify(message, title="Pomodoro", timeout=10, severity="information")
        try:
            self.bell()
        except Exception:  # pragma: no cover - not all terminals support BEL
            logger.debug("Bell not supported")

    def action_show_pomodoro(self) -> None:
        """Open the Pomodoro dialog (works from any screen)."""
        self.push_screen(PomodoroDialog(self.pomodoro))

    # ---------------------------------------------------------------- weather
    def action_show_weather(self) -> None:
        """Open the forecast, or the city dialog when nothing is configured yet."""
        if not self.weather.is_configured:
            self._prompt_for_city()
            return
        self.run_worker(self._ensure_weather_and_show(), group="weather")

    async def _ensure_weather_and_show(self) -> None:
        if self.weather.current is None:
            await self.weather.refresh()
        self._show_forecast()

    def _show_forecast(self) -> None:
        if not self.weather.is_configured:
            self._prompt_for_city()
            return

        self.push_screen(
            WeatherForecastDialog(
                city_name=self.weather.city or "",
                current=self.weather.current,
                forecast=self.weather.forecast,
                last_updated=self.weather.last_updated,
                error=self.weather.error,
            ),
            self._handle_forecast_action,
        )

    def _handle_forecast_action(self, action: Optional[str]) -> None:
        if action == ACTION_CHANGE_CITY:
            self._prompt_for_city()
        elif action == ACTION_REFRESH:
            self.run_worker(self._refresh_and_reopen(), group="weather")

    async def _refresh_and_reopen(self) -> None:
        if await self.weather.refresh(force=True):
            self._show_forecast()
        else:
            self.notify(self.weather.error or "Weather refresh failed", severity="error", timeout=5)

    def _prompt_for_city(self) -> None:
        self.push_screen(CityInputDialog(), self._handle_city_input)

    def _handle_city_input(self, city_name: Optional[str]) -> None:
        if city_name:
            self.run_worker(self._set_city(city_name), group="weather")

    async def _set_city(self, city_name: str) -> None:
        if await self.weather.set_city(city_name):
            self._show_forecast()
        else:
            self.notify(self.weather.error or f"City not found: {city_name}", severity="error", timeout=5)

    # ------------------------------------------------------------------- help
    def action_show_help(self) -> None:
        """Show the key bindings for the current screen and the app."""
        bindings: list[tuple[str, str]] = []
        seen: set[str] = set()

        for source in (self.screen, self):
            for binding in getattr(source, "BINDINGS", []):
                if not isinstance(binding, Binding):
                    continue
                if not binding.show and binding.action in ("cursor_down", "cursor_up"):
                    continue
                if binding.action in seen:
                    continue
                seen.add(binding.action)
                bindings.append((binding.key.replace(",", ", "), binding.description))

        context = getattr(self.screen, "TITLE", "") or type(self.screen).__name__
        self.push_screen(HelpScreen(bindings, context=context))

    # ------------------------------------------------------------------- quit
    def _editors(self) -> list[EditorScreen]:
        return [screen for screen in self.screen_stack if isinstance(screen, EditorScreen)]

    def _save_all_editors(self) -> None:
        for editor in self._editors():
            editor.save_snapshot()

    def action_quit(self) -> None:
        """Quit, but never drop unsaved editor content without asking."""
        editors = self._editors()
        dirty = [editor for editor in editors if editor.is_modified]

        if dirty:
            def handle_quit(confirmed: Optional[bool]) -> None:
                if confirmed:
                    self._save_all_editors()
                    self.exit()

            self.push_screen(
                ConfirmDialog("You have unsaved changes. Quit anyway?"), handle_quit
            )
            return

        self._save_all_editors()
        self.exit()

    def on_shutdown(self) -> None:
        """Last-chance snapshot: covers Ctrl+C and terminal closure."""
        self._save_all_editors()


def _configure_logging(level: str = "INFO") -> None:
    """Configure rotating file logging (never the terminal)."""
    paths.ensure_app_dirs()
    handler = RotatingFileHandler(
        paths.log_file(), maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), handlers=[handler])

    for noisy in ("httpx", "httpcore", "hpack"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def build_parser() -> argparse.ArgumentParser:
    """Command line interface."""
    parser = argparse.ArgumentParser(
        prog="terminallysimple",
        description="One terminal app. Essential tools. Zero distractions.",
    )
    parser.add_argument("--version", action="version", version="terminallysimple 0.2.0")
    parser.add_argument(
        "--notes-dir",
        type=Path,
        default=None,
        help="Directory used by the editor (default: your Documents folder)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log verbosity written to the log file",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    """Entry point for the application."""
    args = build_parser().parse_args(argv)
    _configure_logging(args.log_level)

    if args.notes_dir is not None:
        target = Path(args.notes_dir).expanduser()
        paths.ensure_dir(target)
        config.set("notes_dir", str(target))
        config.save()

    logger.info("Starting Terminally Simple")
    TerminallySimple().run()


if __name__ == "__main__":
    main()
