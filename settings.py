"""
Settings interface for customizing the app
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.containers import Container
from textual.binding import Binding

from config import config


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
        marker = "●" if self.selected else "○"
        if self.has_focus:
            return f"[bold cyan]▸ {marker}[/] [bold]{self.label}[/]"
        return f"  {marker}  {self.label}"
    
    def on_focus(self) -> None:
        """Refresh when focused."""
        self.refresh()
    
    def on_blur(self) -> None:
        """Refresh when focus lost."""
        self.refresh()


class SettingsScreen(Screen):
    """Settings screen for theme and appearance customization."""
    
    BINDINGS = [
        Binding("escape", "back", "Back", priority=True),
        Binding("s", "save", "Save", show=True),
        Binding("r", "reset", "Reset", show=True),
        Binding("enter", "toggle", "Select", show=False),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the settings interface."""
        yield Header(show_clock=True)
        yield Container(
            Static("SETTINGS", id="settings-title"),
            Static("Customize your experience", id="settings-subtitle"),
            
            Static("[bold]Theme Mode[/]", classes="section-title"),
            SettingOption("Dark Mode", "dark", config.get("theme") == "dark", id="opt-dark"),
            SettingOption("Light Mode", "light", config.get("theme") == "light", id="opt-light"),
            
            Static("", classes="spacer"),
            Static("[bold]Accent Color[/]", classes="section-title"),
            SettingOption("Cyan", "cyan", config.get("accent_color") == "cyan", id="opt-cyan"),
            SettingOption("Green", "green", config.get("accent_color") == "green", id="opt-green"),
            SettingOption("Blue", "blue", config.get("accent_color") == "blue", id="opt-blue"),
            SettingOption("Magenta", "magenta", config.get("accent_color") == "magenta", id="opt-magenta"),
            SettingOption("Yellow", "yellow", config.get("accent_color") == "yellow", id="opt-yellow"),
            
            Static("", id="settings-status"),
            id="settings-container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Focus first option when mounted."""
        try:
            self.query_one("#opt-dark").focus()
        except:
            pass
    
    def on_click(self, event) -> None:
        """Handle clicks on options."""
        if isinstance(event.widget, SettingOption):
            self._toggle_option(event.widget)
    
    def action_toggle(self) -> None:
        """Toggle the focused option."""
        focused = self.focused
        if isinstance(focused, SettingOption):
            self._toggle_option(focused)
    
    def _toggle_option(self, option: SettingOption) -> None:
        """Toggle a setting option."""
        # Determine which group this option belongs to
        if option.id in ["opt-dark", "opt-light"]:
            # Theme group
            for opt in [self.query_one("#opt-dark"), self.query_one("#opt-light")]:
                opt.selected = (opt.id == option.id)
                opt.refresh()
        elif option.id.startswith("opt-"):
            # Color group
            for opt in self.query(SettingOption):
                if opt.id in ["opt-cyan", "opt-green", "opt-blue", "opt-magenta", "opt-yellow"]:
                    opt.selected = (opt.id == option.id)
                    opt.refresh()
    
    def action_save(self) -> None:
        """Save the current settings."""
        # Get selected theme
        if self.query_one("#opt-dark").selected:
            config.set("theme", "dark")
        else:
            config.set("theme", "light")
        
        # Get selected color
        for color in ["cyan", "green", "blue", "magenta", "yellow"]:
            opt = self.query_one(f"#opt-{color}")
            if opt.selected:
                config.set("accent_color", color)
                break
        
        # Save to file
        if config.save():
            self._update_status("✓ Saved! Restart the app to apply changes.")
        else:
            self._update_status("✗ Error saving settings")
    
    def action_reset(self) -> None:
        """Reset settings to defaults."""
        config.reset()
        self.app.pop_screen()
        self.app.push_screen(SettingsScreen())
    
    def action_back(self) -> None:
        """Return to the main menu."""
        self.app.pop_screen()
    
    def _update_status(self, message: str) -> None:
        """Update the status message."""
        status = self.query_one("#settings-status", Static)
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

.section-title {
    color: $text;
    margin-top: 1;
    margin-bottom: 1;
    padding-left: 2;
}

.spacer {
    height: 1;
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
    min-height: 1;
}
"""
