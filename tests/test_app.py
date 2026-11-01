"""Application-level behaviour: navigation, shortcuts, header and settings."""

from __future__ import annotations

from config import Config
from app import HelpScreen, MainMenu, TerminallySimple
from dialogs.pomodoro_dialogs import PomodoroDialog
from dialogs.weather_dialogs import CityInputDialog
from editor import EditorScreen
from settings import SettingsScreen
from tasks import TaskManagerScreen
from widgets.system_header import PomodoroWidget, SystemHeader, WeatherWidget


async def test_all_screens_are_reachable_by_keyboard() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert isinstance(app.screen, MainMenu)

        await pilot.press("2")
        await pilot.pause()
        assert isinstance(app.screen, TaskManagerScreen)

        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("3")
        await pilot.pause()
        assert isinstance(app.screen, SettingsScreen)

        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("1")
        await pilot.pause()
        assert isinstance(app.screen, EditorScreen)


async def test_shortcuts_work_while_typing_in_the_editor() -> None:
    """Regression test: 'w'/'p' used to be swallowed by the TextArea."""
    app = TerminallySimple()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("1")
        await pilot.pause()
        editor = app.screen

        await pilot.press("ctrl+p")
        await pilot.pause()
        assert isinstance(app.screen, PomodoroDialog)
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("ctrl+w")
        await pilot.pause()
        assert isinstance(app.screen, CityInputDialog)  # nothing configured yet
        await pilot.press("escape")
        await pilot.pause()

        # Plain letters still type into the buffer.
        await pilot.press("w", "p")
        await pilot.pause()
        assert editor.query_one("#text-area").text == "wp"


async def test_help_lists_bindings() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.press("f1")
        await pilot.pause()

        assert isinstance(app.screen, HelpScreen)
        assert app.screen.bindings
        keys = " ".join(key for key, _ in app.screen.bindings)
        assert "ctrl+w" in keys


async def test_pomodoro_keeps_running_across_screens() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.pomodoro.start()
        await pilot.pause()

        await pilot.press("1")
        await pilot.pause()
        assert app.pomodoro.is_running

        await pilot.press("escape")
        await pilot.pause()
        assert app.pomodoro.is_running


async def test_header_mounts_real_widgets() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        header = app.screen.query_one(SystemHeader)

        assert header.query_one("#pomodoro-widget", PomodoroWidget) is not None
        assert header.query_one("#weather-widget", WeatherWidget) is not None


async def test_header_hides_optional_parts_on_narrow_terminals() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(40, 20)) as pilot:
        await pilot.pause()
        header = app.screen.query_one(SystemHeader)

        assert header.query_one("#header-clock").display is False
        assert header.query_one("#weather-widget").display is False


async def test_header_fits_inside_the_terminal_width() -> None:
    from rich.cells import cell_len

    app = TerminallySimple()
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        header = app.screen.query_one(SystemHeader)
        rendered = header.query_one("#header-left").render()
        plain = rendered.plain if hasattr(rendered, "plain") else str(rendered)

        assert cell_len(plain) <= 80


async def test_theme_preview_is_not_persisted_until_saved() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.press("3")
        await pilot.pause()

        screen = app.screen
        screen.set_focus(screen.query_one("#opt-nord"))
        await pilot.press("enter")
        await pilot.pause()

        assert app.theme == "nord"                 # preview applied
        assert Config().get("theme") == "textual-dark"  # but not saved

        await pilot.press("escape")
        await pilot.pause()
        assert app.theme == "textual-dark"         # preview reverted


async def test_theme_is_saved_explicitly() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.press("3")
        await pilot.pause()
        screen = app.screen
        screen.set_focus(screen.query_one("#opt-dracula"))
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("s")
        await pilot.pause()

        assert Config().get("theme") == "dracula"

        await pilot.press("escape")
        await pilot.pause()
        assert app.theme == "dracula"


async def test_settings_reset_restores_defaults() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.press("3")
        await pilot.pause()
        screen = app.screen
        screen.set_focus(screen.query_one("#opt-monokai"))
        await pilot.press("enter", "s")
        await pilot.pause()
        assert Config().get("theme") == "monokai"

        await pilot.press("r", "s")
        await pilot.pause()
        assert Config().get("theme") == "textual-dark"
