#!/usr/bin/env python3
"""
Terminally Simple - A minimalist terminal application
One app. All your essential tools. Zero distractions.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static
from textual.binding import Binding
from textual.screen import Screen

from editor import EditorScreen
from settings import SettingsScreen
from config import config


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
    
    def __init__(self, label: str, key: str, description: str = "", **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.key = key
        self.description = description
    
    def render(self) -> str:
        """Render the menu item - always show focus state."""
        if self.has_focus:
            return f"[bold cyan]▸ {self.key}[/] [bold]{self.label}[/]  [dim]{self.description}[/]"
        return f"  {self.key}  {self.label}  [dim]{self.description}[/]"
    
    def on_focus(self) -> None:
        """Refresh when focused."""
        self.refresh()
    
    def on_blur(self) -> None:
        """Refresh when focus lost."""
        self.refresh()


class MainMenu(Screen):
    """Main menu screen with tool selection."""
    
    BINDINGS = [
        Binding("1", "select_editor", "Editor", show=False),
        Binding("2", "select_settings", "Settings", show=False),
        Binding("q", "app.quit", "Quit"),
        Binding("enter", "activate", "Select", show=True),
        Binding("down,j", "cursor_down", "Next", show=False),
        Binding("up,k", "cursor_up", "Previous", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the menu."""
        yield Header(show_clock=True)
        yield Container(
            Static("TERMINALLY SIMPLE", id="title"),
            Static("One app. All your tools. Zero distractions.", id="subtitle"),
            MenuItem("Text Editor", "1", "Distraction-free writing", id="item-editor"),
            MenuItem("Settings", "2", "Customize theme and appearance", id="item-settings"),
            MenuItem("Exit", "q", "Quit application", id="item-exit"),
            id="menu-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus first item when mounted."""
        def set_initial_focus():
            self.set_focus(self.query_one("#item-editor"))
        # Use set_timer for a slight delay to ensure rendering is complete
        self.set_timer(0.01, set_initial_focus)

    def on_click(self, event) -> None:
        """Handle clicks on menu items."""
        if isinstance(event.widget, MenuItem):
            self._activate_item(event.widget.id)

    def _activate_item(self, item_id: str) -> None:
        """Activate a menu item."""
        if item_id == "item-editor":
            self.action_select_editor()
        elif item_id == "item-settings":
            self.action_select_settings()
        elif item_id == "item-exit":
            self.app.exit()

    def action_select_editor(self) -> None:
        """Open the editor."""
        self.app.push_screen(EditorScreen())
    
    def action_select_settings(self) -> None:
        """Open the settings screen."""
        self.app.push_screen(SettingsScreen())
    
    def action_activate(self) -> None:
        """Activate focused item."""
        focused = self.focused
        if isinstance(focused, MenuItem):
            self._activate_item(focused.id)
    
    def action_cursor_down(self) -> None:
        """Move to the next menu item."""
        menu_items = list(self.query(MenuItem))
        if not menu_items:
            return
        
        focused = self.focused
        if focused in menu_items:
            current_index = menu_items.index(focused)
            next_index = (current_index + 1) % len(menu_items)
            menu_items[next_index].focus()
        else:
            # If nothing focused or focused widget is not a menu item, focus first
            menu_items[0].focus()
    
    def action_cursor_up(self) -> None:
        """Move to the previous menu item."""
        menu_items = list(self.query(MenuItem))
        if not menu_items:
            return
        
        focused = self.focused
        if focused in menu_items:
            current_index = menu_items.index(focused)
            prev_index = (current_index - 1) % len(menu_items)
            menu_items[prev_index].focus()
        else:
            # If nothing focused or focused widget is not a menu item, focus last
            menu_items[-1].focus()


class TerminallySimple(App):
    """Main application class."""
    
    # Disable the command palette
    ENABLE_COMMAND_PALETTE = False
    
    CSS = """
    Screen {
        border: double $primary;
        background: $surface;
    }
    
    #menu-container {
        width: 100%;
        height: 100%;
        padding: 2 4;
        background: $surface;
    }
    
    #title {
        text-align: left;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    #subtitle {
        text-align: left;
        color: $text-muted;
        margin-bottom: 2;
    }
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


def main():
    """Entry point for the application."""
    app = TerminallySimple()
    app.run()


if __name__ == "__main__":
    main()
