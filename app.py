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
from config import config


class MenuItem(Static):
    """A clickable menu item."""
    
    def __init__(self, label: str, key: str, description: str = "", **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.key = key
        self.description = description
        self.can_focus = True
    
    def render(self) -> str:
        """Render the menu item."""
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
        Binding("q", "quit", "Quit"),
        Binding("enter", "activate", "Select", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the menu."""
        yield Header(show_clock=True)
        yield Container(
            Static("TERMINALLY SIMPLE", id="title"),
            Static("One app. All your tools. Zero distractions.", id="subtitle"),
            MenuItem("Text Editor", "1", "Distraction-free writing", id="item-editor"),
            MenuItem("Exit", "q", "Quit application", id="item-exit"),
            id="menu-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus first item when mounted."""
        try:
            self.query_one("#item-editor").focus()
        except:
            pass

    def on_click(self, event) -> None:
        """Handle clicks on menu items."""
        if isinstance(event.widget, MenuItem):
            self._activate_item(event.widget.id)

    def on_key(self, event) -> None:
        """Handle key presses for menu items."""
        if event.key == "enter":
            focused = self.focused
            if isinstance(focused, MenuItem):
                self._activate_item(focused.id)

    def _activate_item(self, item_id: str) -> None:
        """Activate a menu item."""
        if item_id == "item-editor":
            self.action_select_editor()
        elif item_id == "item-exit":
            self.app.exit()

    def action_select_editor(self) -> None:
        """Open the editor."""
        self.app.push_screen(EditorScreen())
    
    def action_activate(self) -> None:
        """Activate focused item."""
        focused = self.focused
        if isinstance(focused, MenuItem):
            self._activate_item(focused.id)


class TerminallySimple(App):
    """Main application class."""
    
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
    
    MenuItem {
        height: auto;
        padding: 0 2;
        margin: 0;
    }
    
    MenuItem:focus {
        background: $boost;
    }
    """
    
    TITLE = "Terminally Simple"
    
    def on_mount(self) -> None:
        """Called when app starts."""
        # Apply theme from config
        theme = config.get("theme", "dark")
        if theme == "light":
            self.theme = "textual-light"
        else:
            self.theme = "textual-dark"
        
        self.push_screen(MainMenu())


def main():
    """Entry point for the application."""
    app = TerminallySimple()
    app.run()


if __name__ == "__main__":
    main()
