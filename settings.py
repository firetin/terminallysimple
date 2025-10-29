"""
Settings interface for customizing the app
"""

import logging
from typing import Any, List, Optional, Tuple

from textual.app import ComposeResult
from textual.events import Click
from textual.widgets import Footer, Static
from textual.containers import Container, Vertical
from textual.binding import Binding
from textual.widget import Widget

from base_screen import NavigableScreen
from config import config
from constants import SELECTED_MARKER, UNSELECTED_MARKER, FOCUS_INDICATOR, FOCUS_COLOR, WidgetIDs
from widgets.system_header import SystemHeader

logger = logging.getLogger(__name__)


class SettingOption(Static):
    """A selectable setting option."""
    
    def __init__(self, label: str, value: str, selected: bool = False, **kwargs):
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
        """Refresh when focused."""
        self.refresh()
    
    def on_blur(self) -> None:
        """Refresh when focus lost."""
        self.refresh()


class SettingsScreen(NavigableScreen):
    """Settings screen for theme customization."""
    
    # Available Textual themes
    THEMES: List[Tuple[str, str]] = [
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
    
    BINDINGS = [
        Binding("escape", "back", "Back", priority=True),
        Binding("s", "save", "Save", show=True),
        Binding("r", "reset", "Reset", show=True),
        Binding("enter", "toggle", "Select", show=True),
        Binding("down,j", "cursor_down", "Next", show=False),
        Binding("up,k", "cursor_up", "Previous", show=False),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the settings interface."""
        # Get current theme from config
        current_theme = config.get("theme", "textual-dark")
        
        yield SystemHeader(show_clock=True)
        yield Container(
            Static("SETTINGS", id=WidgetIDs.SETTINGS_TITLE),
            Static("Select your theme", id=WidgetIDs.SETTINGS_SUBTITLE),
            
            Vertical(
                *(SettingOption(
                    label, 
                    value, 
                    selected=(value == current_theme),
                    id=f"opt-{value}"
                ) for label, value in self.THEMES),
                id=WidgetIDs.THEME_LIST
            ),
            
            Static("", id=WidgetIDs.SETTINGS_STATUS),
            id=WidgetIDs.SETTINGS_CONTAINER
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Focus first option when mounted."""
        try:
            # Focus the currently selected theme
            current_theme = config.get("theme", "textual-dark")
            self.query_one(f"#opt-{current_theme}").focus()
        except Exception:
            # If not found, focus first option
            try:
                first_option = self.query(SettingOption).first()
                first_option.focus()
            except Exception:
                pass
    
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
        """Toggle a setting option and apply theme preview."""
        # Deselect all options
        for opt in self.query(SettingOption):
            opt.selected = False
            opt.refresh()
        
        # Select this option
        option.selected = True
        option.refresh()
        
        # Apply theme preview immediately
        try:
            self.app.theme = option.value
            self._update_status(f"Preview: {option.label} (press 's' to save)")
        except Exception as e:
            self._update_status(f"Theme not available: {option.label}")
    
    def action_save(self) -> None:
        """Save the current settings and apply them immediately."""
        # Find selected theme
        selected_theme = None
        for opt in self.query(SettingOption):
            if opt.selected:
                selected_theme = opt.value
                break
        
        if selected_theme:
            config.set("theme", selected_theme)
            
            # Save to file
            if config.save():
                # Apply theme
                self.app.theme = selected_theme
                self._update_status("✓ Saved and applied!")
            else:
                self._update_status("✗ Error saving settings")
        else:
            self._update_status("✗ No theme selected")
    
    def action_reset(self) -> None:
        """Reset settings to defaults."""
        config.reset()
        self.app.apply_theme_from_config()
        self.app.pop_screen()
        self.app.push_screen(SettingsScreen())
    
    def action_back(self) -> None:
        """Return to the main menu and restore original theme if not saved."""
        # Restore the theme from config in case user didn't save
        self.app.apply_theme_from_config()
        self.app.pop_screen()
    
    def get_focusable_items(self) -> List[Widget]:
        """Return setting options for navigation."""
        return list(self.query(SettingOption))
    
    def _update_status(self, message: str) -> None:
        """Update the status message."""
        status = self.query_one(f"#{WidgetIDs.SETTINGS_STATUS}", Static)
        status.update(message)


# Custom CSS for settings
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

#settings-subtitle {
    text-align: center;
    color: $text-muted;
    margin-bottom: 2;
}

#theme-list {
    height: auto;
    overflow-y: auto;
    max-height: 30;
}

SettingOption {
    height: auto;
    padding: 1 2;
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
