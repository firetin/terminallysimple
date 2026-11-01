"""Pomodoro timer dialog."""

from __future__ import annotations

import logging
from typing import Any, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static

from constants import WidgetIDs
from services import PomodoroService

logger = logging.getLogger(__name__)


class PomodoroDialog(ModalScreen[None]):
    """Modal dialog to control the (app-wide) Pomodoro timer."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close", priority=True),
        Binding("s", "start", "Start", show=True),
        Binding("p", "pause", "Pause", show=True),
        Binding("r", "reset", "Reset", show=True),
    ]

    def __init__(self, service: PomodoroService, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = service
        self._dialog_timer: Optional[Any] = None

    def compose(self) -> ComposeResult:
        """Create the Pomodoro dialog interface."""
        with Container(id=WidgetIDs.POMODORO_CONTAINER):
            yield Static("POMODORO TIMER", id=WidgetIDs.POMODORO_TITLE)
            yield Static(self.service.formatted_remaining(), id=WidgetIDs.POMODORO_TIME)
            yield Static(self._status_text(), id=WidgetIDs.POMODORO_STATUS)
            yield Static(
                "\n[bold]Settings:[/]\n"
                f"• Work: {self.service.work_seconds // 60} minutes\n"
                f"• Short Break: {self.service.short_break_seconds // 60} minutes\n"
                f"• Long Break: {self.service.long_break_seconds // 60} minutes "
                f"(every {self.service.cycles_before_long_break} cycles)\n"
                f"• Completed work sessions today: {self.service.work_count}\n",
                id=WidgetIDs.POMODORO_INFO,
            )
            yield Static(
                "s = start/resume · p = pause · r = reset · Esc = close",
                id=WidgetIDs.POMODORO_HINT,
            )

    def on_mount(self) -> None:
        """Keep the dialog in sync with the service."""
        self._dialog_timer = self.set_interval(0.25, self._update_display)

    def on_unmount(self) -> None:
        if self._dialog_timer is not None:
            self._dialog_timer.stop()
            self._dialog_timer = None

    def _status_text(self) -> str:
        service = self.service
        if service.is_running:
            return f"[green]● Running[/] - {service.session_type}"
        if service.is_paused:
            return f"[yellow]⏸ Paused[/] - {service.session_type}"
        return f"[dim]⏹ Stopped[/] - {service.session_type}"

    def _update_display(self) -> None:
        """Refresh the time and status labels."""
        try:
            self.query_one(f"#{WidgetIDs.POMODORO_TIME}", Static).update(
                self.service.formatted_remaining()
            )
            self.query_one(f"#{WidgetIDs.POMODORO_STATUS}", Static).update(self._status_text())
        except Exception:  # pragma: no cover - during teardown
            pass

    def action_start(self) -> None:
        """Start or resume the timer."""
        self.service.start()
        self._update_display()

    def action_pause(self) -> None:
        """Pause the timer."""
        self.service.pause()
        self._update_display()

    def action_reset(self) -> None:
        """Reset the timer."""
        self.service.reset()
        self._update_display()

    def action_dismiss(self) -> None:  # type: ignore[override]
        """Close the dialog."""
        self.dismiss(None)


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
