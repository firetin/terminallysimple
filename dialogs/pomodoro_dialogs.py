"""
Pomodoro timer dialog screens
"""

import logging
from typing import Optional, Callable, Any

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from textual.binding import Binding

from constants import WidgetIDs

logger = logging.getLogger(__name__)


class PomodoroDialog(ModalScreen[Optional[str]]):
    """Modal dialog for Pomodoro timer control."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close", priority=True),
        Binding("s", "start", "Start", show=True),
        Binding("p", "pause", "Pause", show=True),
        Binding("r", "reset", "Reset", show=True),
    ]
    
    def __init__(
        self, 
        is_running: bool,
        is_paused: bool,
        current_time: int,
        session_type: str,
        on_start: Optional[Callable[[], None]] = None,
        on_pause: Optional[Callable[[], None]] = None,
        on_reset: Optional[Callable[[], None]] = None,
        get_current_state: Optional[Callable[[], tuple[int, bool, bool, str]]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self._is_running = is_running
        self._is_paused = is_paused
        self._current_time = current_time
        self._session_type = session_type
        self.on_start_callback = on_start
        self.on_pause_callback = on_pause
        self.on_reset_callback = on_reset
        self.get_current_state = get_current_state
        self.update_timer_ref = None
    
    def on_mount(self) -> None:
        """Start updating the dialog when mounted."""
        # Update every 100ms to keep dialog in sync
        self.update_timer_ref = self.set_interval(0.1, self._update_display)
    
    def on_unmount(self) -> None:
        """Stop updating when unmounted."""
        if self.update_timer_ref:
            self.update_timer_ref.stop()
    
    def _update_display(self) -> None:
        """Update the display with current state."""
        if self.get_current_state:
            time_remaining, is_running, is_paused, session_type = self.get_current_state()
            
            # Update the time display
            minutes = time_remaining // 60
            seconds = time_remaining % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            try:
                time_widget = self.query_one(f"#{WidgetIDs.POMODORO_TIME}", Static)
                time_widget.update(time_str)
                
                # Update status
                if is_running and not is_paused:
                    status = f"[green]● Running[/] - {session_type}"
                elif is_paused:
                    status = f"[yellow]⏸ Paused[/] - {session_type}"
                else:
                    status = "[dim]⏹ Stopped[/]"
                
                status_widget = self.query_one(f"#{WidgetIDs.POMODORO_STATUS}", Static)
                status_widget.update(status)
            except Exception:
                pass
    
    def compose(self) -> ComposeResult:
        """Create the Pomodoro dialog interface."""
        # Format time
        minutes = self._current_time // 60
        seconds = self._current_time % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Status message
        if self._is_running and not self._is_paused:
            status = f"[green]● Running[/] - {self._session_type}"
        elif self._is_paused:
            status = f"[yellow]⏸ Paused[/] - {self._session_type}"
        else:
            status = "[dim]⏹ Stopped[/]"
        
        with Container(id=WidgetIDs.POMODORO_CONTAINER):
            yield Static("POMODORO TIMER", id=WidgetIDs.POMODORO_TITLE)
            yield Static(time_str, id=WidgetIDs.POMODORO_TIME)
            yield Static(status, id=WidgetIDs.POMODORO_STATUS)
            
            yield Static(
                "\n[bold]Default Settings:[/]\n"
                "• Work: 25 minutes\n"
                "• Short Break: 5 minutes\n"
                "• Long Break: 15 minutes (every 4 cycles)\n",
                id=WidgetIDs.POMODORO_INFO
            )
            
            yield Static(
                "Press 's' to start, 'p' to pause, 'r' to reset, Escape to close",
                id=WidgetIDs.POMODORO_HINT
            )
    
    def on_key(self, event) -> None:
        """Handle escape key."""
        if event.key == "escape":
            self.dismiss(None)
    
    def action_start(self) -> None:
        """Start or resume timer."""
        if self.on_start_callback:
            self.on_start_callback()
        # Don't dismiss - keep dialog open
    
    def action_pause(self) -> None:
        """Pause the timer."""
        if self.on_pause_callback:
            self.on_pause_callback()
        # Don't dismiss - keep dialog open
    
    def action_reset(self) -> None:
        """Reset the timer."""
        if self.on_reset_callback:
            self.on_reset_callback()
        # Don't dismiss - keep dialog open


PomodoroDialog.CSS = """
PomodoroDialog {
    align: center middle;
}

#pomodoro-container {
    border: double $primary;
    width: 60;
    height: auto;
    background: $surface;
    padding: 2;
}

#pomodoro-title {
    text-align: center;
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}

#pomodoro-time {
    text-align: center;
    text-style: bold;
    color: $primary;
    margin-bottom: 1;
    height: 3;
    content-align: center middle;
}

#pomodoro-status {
    text-align: center;
    color: $text;
    margin-bottom: 2;
}

#pomodoro-info {
    color: $text;
    padding: 1;
    margin-bottom: 1;
}

#pomodoro-hint {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
}
"""
