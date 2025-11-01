#!/usr/bin/env python3
"""
Terminally Simple - A minimalist terminal application
One app. Essential tools. Zero distractions.
"""

import logging
from pathlib import Path
from typing import Optional, Any

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.events import Click
from textual.widgets import Footer, Static
from textual.binding import Binding
from textual.screen import Screen
from textual.widget import Widget

from base_screen import NavigableScreen
from editor import EditorScreen
from tasks import TaskManagerScreen
from settings import SettingsScreen
from config import config
from constants import FOCUS_INDICATOR, FOCUS_COLOR, DIM_COLOR, FOCUS_TIMER_DELAY, WidgetIDs
from widgets.system_header import SystemHeader

logger = logging.getLogger(__name__)


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
    
    MenuItem:focus-within {
        background: $boost;
    }
    """
    
    def __init__(self, label: str, key: str, description: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.label: str = label
        self.key: str = key
        self.description: str = description
    
    def render(self) -> str:
        """Render the menu item - always show focus state."""
        if self.has_focus:
            return f"[{FOCUS_COLOR}]{FOCUS_INDICATOR} {self.key}[/] [bold]{self.label}[/]  [{DIM_COLOR}]{self.description}[/]"
        return f"  {self.key}  {self.label}  [{DIM_COLOR}]{self.description}[/]"
    
    def on_focus(self) -> None:
        """Refresh when focused."""
        self.refresh()
    
    def on_blur(self) -> None:
        """Refresh when focus lost."""
        self.refresh()


class MainMenu(NavigableScreen):
    """Main menu screen with tool selection."""
    
    BINDINGS = [
        Binding("1", "select_editor", "Editor", show=False),
        Binding("2", "select_tasks", "Tasks", show=False),
        Binding("3", "select_settings", "Settings", show=False),
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
            MenuItem("Exit", "q", "Quit application", id=WidgetIDs.ITEM_EXIT),
            id=WidgetIDs.MENU_CONTAINER
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus first item when mounted."""
        def set_initial_focus() -> None:
            self.set_focus(self.query_one(f"#{WidgetIDs.ITEM_EDITOR}"))
        # Use set_timer for a slight delay to ensure rendering is complete
        self.set_timer(FOCUS_TIMER_DELAY, set_initial_focus)

    def on_click(self, event: Click) -> None:
        """Handle clicks on menu items."""
        if isinstance(event.widget, MenuItem) and event.widget.id:
            self._activate_item(event.widget.id)

    def _activate_item(self, item_id: str) -> None:
        """Activate a menu item."""
        if item_id == WidgetIDs.ITEM_EDITOR:
            self.action_select_editor()
        elif item_id == WidgetIDs.ITEM_TASKS:
            self.action_select_tasks()
        elif item_id == WidgetIDs.ITEM_SETTINGS:
            self.action_select_settings()
        elif item_id == WidgetIDs.ITEM_EXIT:
            self.app.exit()

    def action_select_editor(self) -> None:
        """Open the editor."""
        self.app.push_screen(EditorScreen())
    
    def action_select_tasks(self) -> None:
        """Open the task manager."""
        self.app.push_screen(TaskManagerScreen())
    
    def action_select_settings(self) -> None:
        """Open the settings screen."""
        self.app.push_screen(SettingsScreen())
    
    def action_activate(self) -> None:
        """Activate focused item."""
        focused = self.focused
        if isinstance(focused, MenuItem) and focused.id:
            self._activate_item(focused.id)
    
    def get_focusable_items(self) -> list[Widget]:
        """Return menu items for navigation."""
        return list(self.query(MenuItem))


class TerminallySimple(App):
    """Main application class."""
    
    # Disable the command palette
    ENABLE_COMMAND_PALETTE = False
    
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
    
    TITLE = "Terminally Simple"
    
    def on_mount(self) -> None:
        """Called when app starts."""
        # Apply theme from config without triggering watch_theme
        self.apply_theme_from_config()
        self.push_screen(MainMenu())
    
    def apply_theme_from_config(self) -> None:
        """Apply theme from config without triggering auto-save."""
        theme = config.get("theme", "textual-dark")
        try:
            self.theme = theme
        except Exception:
            # If theme doesn't exist, fall back to textual-dark
            self.theme = "textual-dark"
    
    def watch_theme(self, theme: str) -> None:
        """Watch for theme changes and save them to config.
        
        Note: This is called automatically when self.theme changes.
        It does NOT get called during initialization because we set
        the theme in on_mount before any screens are loaded.
        """
        # Save the theme preference when it changes
        config.set("theme", theme)
        config.save()


def main() -> None:
    """Entry point for the application."""
    # Configure logging
    log_dir = Path.home() / ".config" / "terminallysimple"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"
    
    # Configure logging to only write to file, not console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file)
        ]
    )
    
    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("hpack").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Terminally Simple")
    
    app = TerminallySimple()
    app.run()


if __name__ == "__main__":
    main()
