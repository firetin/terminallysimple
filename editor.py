"""
Text/Markdown Editor - Distraction-free writing
"""

from __future__ import annotations

import logging
import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

from textual.app import ComposeResult
from textual.css.query import NoMatches
from textual.events import Click
from textual.screen import Screen, ModalScreen
from textual.widgets import Footer, TextArea, Static, Button, Input, Label
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from textual.widget import Widget
from textual.timer import Timer

from base_screen import NavigableMixin
from config import config
from constants import (
    AUTOSAVE_INTERVAL,
    FOCUS_INDICATOR,
    FOCUS_COLOR,
    DIM_COLOR,
    TAB_SPACES,
    FOCUS_TIMER_DELAY,
    WidgetIDs,
)
from utils import paths, storage
from utils.validators import sanitize_filename
from widgets.system_header import SystemHeader

logger = logging.getLogger(__name__)


class ConfirmDialog(ModalScreen[bool]):
    """Modal dialog for confirming actions."""
    
    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.message: str = message
    
    def compose(self) -> ComposeResult:
        """Create the confirmation dialog interface."""
        with Container(id=WidgetIDs.CONFIRM_CONTAINER):
            yield Static("CONFIRM", id=WidgetIDs.CONFIRM_TITLE)
            yield Static(self.message, id=WidgetIDs.CONFIRM_MESSAGE)
            yield Static("Press 'y' to confirm, 'n' or Escape to cancel", id=WidgetIDs.CONFIRM_HINT)
    
    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "y":
            self.dismiss(True)
        elif event.key in ("n", "escape"):
            self.dismiss(False)


class ConfirmDeleteFileDialog(ModalScreen[bool]):
    """Modal dialog for confirming file deletion."""
    
    def __init__(self, filename: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.filename: str = filename
    
    def compose(self) -> ComposeResult:
        """Create the confirmation dialog interface."""
        with Container(id="confirm-delete-file-container"):
            yield Static("DELETE FILE", id="confirm-delete-file-title")
            yield Static(f"Delete '{self.filename}'?", id="confirm-delete-file-message")
            yield Static("Press 'y' to delete, 'n' or Escape to cancel", id="confirm-delete-file-hint")
    
    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "y":
            self.dismiss(True)
        elif event.key in ("n", "escape"):
            self.dismiss(False)


ConfirmDialog.CSS = """
ConfirmDialog {
    align: center middle;
}

#confirm-container {
    border: double $error;
    width: 60;
    height: auto;
    background: $surface;
    padding: 2;
}

#confirm-title {
    text-align: center;
    text-style: bold;
    color: $error;
    margin-bottom: 1;
}

#confirm-message {
    text-align: center;
    color: $text;
    margin-bottom: 2;
}

#confirm-hint {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
}
"""


ConfirmDeleteFileDialog.CSS = """
ConfirmDeleteFileDialog {
    align: center middle;
}

#confirm-delete-file-container {
    border: double $error;
    width: 60;
    height: auto;
    background: $surface;
    padding: 2;
}

#confirm-delete-file-title {
    text-align: center;
    text-style: bold;
    color: $error;
    margin-bottom: 1;
}

#confirm-delete-file-message {
    text-align: center;
    color: $text;
    margin-bottom: 2;
}

#confirm-delete-file-hint {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
}
"""


class ClickablePath(Static, can_focus=True):
    """A clickable path that opens the folder."""
    
    def __init__(self, path: Path, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.path: Path = path
    
    def render(self) -> str:
        """Render the path."""
        if self.has_focus:
            return f"Location: [{FOCUS_COLOR}][link]{self.path}[/link][/] [{DIM_COLOR}](click to open)[/]"
        return f"Location: [link]{self.path}[/link] [{DIM_COLOR}](click to open)[/]"
    
    def on_click(self) -> None:
        """Open the folder when clicked in the system's file manager."""
        try:
            # Validate path exists and is a directory
            if not self.path.exists() or not self.path.is_dir():
                logger.warning(f"Path does not exist or is not a directory: {self.path}")
                return
            
            system = platform.system()
            path_str = str(self.path.resolve())  # Use resolved absolute path
            
            if system == 'Darwin':  # macOS
                subprocess.run(['open', path_str], check=False)
            elif system == 'Windows':
                subprocess.run(['explorer', path_str], check=False)
            else:  # Linux and other Unix-like systems
                subprocess.run(['xdg-open', path_str], check=False)
        except FileNotFoundError:
            # File manager command not available
            logger.debug("File manager command not available")
        except (OSError, subprocess.SubprocessError) as e:
            logger.warning(f"Could not open folder: {e}")
    
    def on_focus(self) -> None:
        """Refresh when focused."""
        self.refresh()
    
    def on_blur(self) -> None:
        """Refresh when focus lost."""
        self.refresh()


class FilenamePrompt(ModalScreen[Optional[str]]):
    """Modal screen for entering a filename."""
    
    def compose(self) -> ComposeResult:
        """Create the filename prompt interface."""
        from textual.widgets import Input, Label
        from textual.containers import Vertical
        
        with Container(id=WidgetIDs.PROMPT_CONTAINER):
            yield Static("SAVE FILE", id=WidgetIDs.PROMPT_TITLE)
            yield Label("Enter filename:", id=WidgetIDs.PROMPT_LABEL)
            yield Input(placeholder="my-note", id=WidgetIDs.FILENAME_INPUT)
            yield Static("Press Enter to save, Escape to cancel", id=WidgetIDs.PROMPT_HINT)
            yield Static("Alphanumeric, spaces, hyphens, underscores only", id=WidgetIDs.PROMPT_RULES)
    
    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one(f"#{WidgetIDs.FILENAME_INPUT}").focus()
    
    def on_input_submitted(self, event) -> None:
        """Handle Enter key in input."""
        filename = event.value.strip()
        self.dismiss(filename if filename else None)
    
    def on_key(self, event) -> None:
        """Handle escape key."""
        if event.key == "escape":
            self.dismiss(None)


FilenamePrompt.CSS = """
FilenamePrompt {
    align: center middle;
}

#prompt-container {
    border: double $primary;
    width: 60;
    height: auto;
    background: $surface;
    padding: 2;
}

#prompt-title {
    text-align: center;
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}

#prompt-label {
    color: $text;
    margin-bottom: 1;
}

#filename-input {
    margin-bottom: 1;
}

#prompt-hint {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
}

#prompt-rules {
    text-align: center;
    color: $text-muted;
    text-style: dim;
}
"""


class RenamePrompt(ModalScreen[Optional[str]]):
    """Modal screen for renaming a file."""
    
    def __init__(self, current_filename: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.current_filename: str = current_filename
    
    def compose(self) -> ComposeResult:
        """Create the rename prompt interface."""
        from textual.widgets import Input, Label
        from textual.containers import Vertical
        
        # Remove extension for display
        display_name = self.current_filename.rsplit('.', 1)[0] if '.' in self.current_filename else self.current_filename
        
        with Container(id=WidgetIDs.RENAME_CONTAINER):
            yield Static("RENAME FILE", id=WidgetIDs.RENAME_TITLE)
            yield Label("Enter new filename (without extension):", id=WidgetIDs.RENAME_LABEL)
            yield Input(value=display_name, placeholder="my-note", id=WidgetIDs.RENAME_INPUT)
            yield Static("Press Enter to rename, Escape to cancel", id=WidgetIDs.RENAME_HINT)
            yield Static("Alphanumeric, spaces, hyphens, underscores only", id=WidgetIDs.RENAME_RULES)
    
    def on_mount(self) -> None:
        """Focus the input when mounted and select all text."""
        input_widget = self.query_one(f"#{WidgetIDs.RENAME_INPUT}", Input)
        input_widget.focus()
        input_widget.action_select_all()
    
    def on_input_submitted(self, event) -> None:
        """Handle Enter key in input."""
        filename = event.value.strip()
        self.dismiss(filename if filename else None)
    
    def on_key(self, event) -> None:
        """Handle escape key."""
        if event.key == "escape":
            self.dismiss(None)


RenamePrompt.CSS = """
RenamePrompt {
    align: center middle;
}

#rename-container {
    border: double $secondary;
    width: 60;
    height: auto;
    background: $surface;
    padding: 2;
}

#rename-title {
    text-align: center;
    text-style: bold;
    color: $secondary;
    margin-bottom: 1;
}

#rename-label {
    color: $text;
    margin-bottom: 1;
}

#rename-input {
    margin-bottom: 1;
}

#rename-hint {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
}

#rename-rules {
    text-align: center;
    color: $text-muted;
    text-style: dim;
}
"""


class FileItem(Static, can_focus=True):
    """A clickable file item in the browser."""
    
    def __init__(self, filename: str, filepath: Path, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.filename: str = filename
        self.filepath: Path = filepath
    
    def render(self) -> str:
        """Render the file item - always show focus state."""
        if self.has_focus:
            return f"[{FOCUS_COLOR}]{FOCUS_INDICATOR}[/] {self.filename}"
        return f"  {self.filename}"
    
    def on_focus(self) -> None:
        """Refresh when focused."""
        self.refresh()
    
    def on_blur(self) -> None:
        """Refresh when focus lost."""
        self.refresh()


class FileBrowser(NavigableMixin, ModalScreen[Optional[Path]]):
    """Modal screen for browsing and selecting files."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
        Binding("enter", "select", "Open", show=False),
        Binding("ctrl+d", "delete_file", "Delete", show=True),
        Binding("down,j", "cursor_down", "Next", show=False),
        Binding("up,k", "cursor_up", "Previous", show=False),
    ]
    
    def __init__(self, documents_dir: Path) -> None:
        super().__init__()
        self.documents_dir: Path = documents_dir
        self.selected_file: Optional[Path] = None
        self.focused: Optional[Widget] = None
    
    def compose(self) -> ComposeResult:
        """Create the file browser interface."""
        from textual.widgets import Footer
        # Support multiple text file extensions
        all_files = []
        for ext in ['*.md', '*.txt', '*.text']:
            all_files.extend(self.documents_dir.glob(ext))
        files = sorted(all_files, key=os.path.getmtime, reverse=True)
        
        yield Container(
            Static("OPEN FILE", id=WidgetIDs.BROWSER_TITLE),
            ClickablePath(self.documents_dir, id=WidgetIDs.BROWSER_PATH),
            Static("", id=WidgetIDs.BROWSER_SPACER),
            Vertical(
                *(FileItem(
                    f"{file.stem}  [dim]{self._format_time(os.path.getmtime(file))}[/]",
                    file
                ) for file in files) if files else [Static("No files found. Save a file first!", id=WidgetIDs.NO_FILES)],
                id=WidgetIDs.FILE_LIST
            ),
            id=WidgetIDs.BROWSER_CONTAINER
        )
        yield Footer()
    
    def _format_time(self, timestamp: float) -> str:
        """Format timestamp for display."""
        mod_time = datetime.fromtimestamp(timestamp)
        return mod_time.strftime("%Y-%m-%d %H:%M")
    
    def on_mount(self) -> None:
        """Focus first file when mounted."""
        def set_initial_focus() -> None:
            try:
                first_item = self.query_one(FileItem)
                self.set_focus(first_item)
            except Exception:
                # No file items available, nothing to focus
                pass
        # Use set_timer for a slight delay to ensure rendering is complete
        self.set_timer(FOCUS_TIMER_DELAY, set_initial_focus)
    
    def on_click(self, event: Click) -> None:
        """Handle clicks on file items."""
        if isinstance(event.widget, FileItem):
            self.selected_file = event.widget.filepath
            self.dismiss(self.selected_file)
    
    def action_select(self) -> None:
        """Select the focused file."""
        focused = self.focused
        if isinstance(focused, FileItem):
            self.selected_file = focused.filepath
            self.dismiss(self.selected_file)
    
    def action_dismiss(self) -> None:
        """Cancel file selection."""
        self.dismiss(None)
    
    def action_delete_file(self) -> None:
        """Delete the focused file with confirmation."""
        focused = self.focused
        if not isinstance(focused, FileItem):
            return
        
        file_to_delete = focused.filepath
        
        def handle_confirm(confirmed: Optional[bool]) -> None:
            if confirmed:
                try:
                    file_to_delete.unlink()
                    logger.info(f"Deleted file: {file_to_delete.name}")
                    # Refresh the file list
                    self._refresh_file_list()
                except (OSError, IOError) as e:
                    logger.error(f"Failed to delete file: {e}")
        
        self.app.push_screen(
            ConfirmDeleteFileDialog(file_to_delete.stem),
            handle_confirm
        )
    
    def _refresh_file_list(self) -> None:
        """Refresh the file list after deletion."""
        # Clear existing file items
        file_list = self.query_one(f"#{WidgetIDs.FILE_LIST}", Vertical)
        file_list.remove_children()
        
        # Reload files - support multiple text file extensions
        all_files = []
        for ext in ['*.md', '*.txt', '*.text']:
            all_files.extend(self.documents_dir.glob(ext))
        files = sorted(all_files, key=os.path.getmtime, reverse=True)
        
        if files:
            for file in files:
                file_list.mount(FileItem(
                    f"{file.stem}  [dim]{self._format_time(os.path.getmtime(file))}[/]",
                    file
                ))
            # Focus first item
            def set_focus() -> None:
                try:
                    first_item = self.query_one(FileItem)
                    self.set_focus(first_item)
                except Exception:
                    pass
            self.set_timer(FOCUS_TIMER_DELAY, set_focus)
        else:
            # Show no files message
            file_list.mount(Static("No files found. Save a file first!", id=WidgetIDs.NO_FILES))
    
    def get_focusable_items(self) -> list[Widget]:
        """Return focusable items for navigation (ClickablePath and FileItems)."""
        focusable: list[Widget] = []
        try:
            clickable_path = self.query_one(ClickablePath)
            focusable.append(clickable_path)
        except Exception:
            # No ClickablePath widget found
            pass
        focusable.extend(list(self.query(FileItem)))
        return focusable


FileBrowser.CSS = """
FileBrowser {
    border: double $primary;
}

#browser-container {
    width: 100%;
    height: 100%;
    background: $surface;
    padding: 2 4;
}

#browser-title {
    text-align: left;
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}

#browser-path {
    text-align: left;
    color: $text-muted;
    margin-bottom: 1;
}

ClickablePath {
    height: auto;
    padding: 0;
}

ClickablePath:focus {
    background: $boost;
}

ClickablePath:focus-within {
    background: $boost;
}

#browser-spacer {
    height: 1;
}

#file-list {
    height: auto;
    overflow-y: auto;
}

#no-files {
    color: $text-muted;
    padding: 2 0;
}

FileItem {
    height: auto;
    padding: 0 2;
    margin: 0;
}

FileItem:focus {
    background: $boost;
}

FileItem:focus-within {
    background: $boost;
}
"""


class EditorScreen(Screen):
    """A minimalist text editor for distraction-free writing."""

    BINDINGS = [
        Binding("ctrl+s", "save", "Save", priority=True),
        Binding("ctrl+o", "open", "Open", priority=True),
        Binding("ctrl+n", "new", "New", priority=True),
        Binding("ctrl+r", "rename", "Rename", priority=True),
        Binding("ctrl+a", "select_all", "Select All", show=False, priority=True),
        Binding("ctrl+z", "undo", "Undo", show=False, priority=True),
        Binding("ctrl+y", "redo", "Redo", show=False, priority=True),
        Binding("escape", "back", "Back", priority=True),
        Binding("tab", "insert_tab", "Tab", show=False, priority=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.current_file: Optional[Path] = None
        self.is_modified: bool = False  # Track if content has been modified
        self.original_content: str = ""  # Store original content for comparison
        self.autosave_timer: Optional[Timer] = None  # Timer for autosaving
        self.autosave_enabled: bool = True
        self.autosave_interval: float = float(config.get("autosave_interval", AUTOSAVE_INTERVAL))

        # Notes and snapshots live in the user's documents/data folders, never
        # inside the installed package.
        configured_dir = config.get("notes_dir")
        if configured_dir:
            self.documents_dir: Path = Path(configured_dir).expanduser()
        else:
            self.documents_dir = paths.notes_dir()
        self.autosave_dir: Path = paths.data_dir() / "autosave"
        self._ensure_directories()

        # Cache of the buffer, so snapshots keep working after the DOM is gone
        # (Textual detaches widgets before dispatching ``on_unmount``).
        self._text_area: Optional[TextArea] = None
        self._cached_text: str = ""

    # ------------------------------------------------------------------ setup
    def _ensure_directories(self) -> None:
        if not config.get("notes_dir"):
            paths.migrate_legacy_notes(self.documents_dir)
        for directory in (self.documents_dir, self.autosave_dir):
            try:
                paths.ensure_dir(directory)
            except OSError as e:
                logger.error("Could not create %s: %s", directory, e)

    @property
    def autosave_file(self) -> Path:
        """Snapshot file for a document that has not been named yet."""
        return self.autosave_dir / "untitled-autosave.md"

    def compose(self) -> ComposeResult:
        """Create the editor interface."""
        yield SystemHeader(show_clock=True)
        yield Container(
            Static("", id=WidgetIDs.EDITOR_STATUS),
            TextArea(id=WidgetIDs.TEXT_AREA, show_line_numbers=True),
            id=WidgetIDs.EDITOR_CONTAINER,
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the editor when mounted."""
        self._text_area = self.query_one(f"#{WidgetIDs.TEXT_AREA}", TextArea)
        self._text_area.focus()
        self._cached_text = self._text_area.text

        self._update_status_with_file()
        self._start_autosave_timer()
        self._offer_autosave_recovery()

    def on_unmount(self) -> None:
        """Persist the buffer while the content is still known."""
        self.save_snapshot()
        if self.autosave_timer:
            self.autosave_timer.stop()
            self.autosave_timer = None

    def on_screen_suspend(self) -> None:
        """Save when another screen (e.g. a dialog) is pushed on top."""
        self.save_snapshot()

    # --------------------------------------------------------------- autosave
    def _start_autosave_timer(self) -> None:
        if self.autosave_enabled and self.autosave_interval > 0:
            self.autosave_timer = self.set_interval(self.autosave_interval, self._autosave)

    def _autosave(self) -> None:
        """Timer callback: snapshot the buffer if it has content."""
        if self.save_snapshot() and self.current_file:
            self.is_modified = False

    def save_snapshot(self) -> bool:
        """
        Persist the current buffer without touching the widget tree.

        Safe to call from ``on_unmount``/``on_shutdown`` and therefore the
        reason unsaved work can no longer be lost when the app quits.
        """
        text = self._cached_text
        if not text.strip():
            return False

        if self.current_file:
            return storage.write_text_atomic(self.current_file, text)

        try:
            paths.ensure_dir(self.autosave_dir)
        except OSError as e:
            logger.error("Could not create autosave directory: %s", e)
            return False
        return storage.write_text_atomic(self.autosave_file, text)

    def _offer_autosave_recovery(self) -> None:
        """Ask the user whether to restore the previous session's buffer."""
        snapshot = self.autosave_file
        if not snapshot.exists():
            return

        content = storage.read_text(snapshot)
        if not content.strip():
            snapshot.unlink(missing_ok=True)
            return

        def handle_recovery(confirmed: Optional[bool]) -> None:
            if confirmed:
                self._load_content(content, self.current_file)
                self.is_modified = True
                self._update_status_with_file()
                self.notify("Recovered unsaved note", timeout=3)
            else:
                snapshot.unlink(missing_ok=True)

        self.app.push_screen(
            ConfirmDialog("Recover the unsaved note from your last session?"),
            handle_recovery,
        )

    # ------------------------------------------------------------- text events
    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Track the buffer and modification state."""
        self._cached_text = event.text_area.text
        self.is_modified = self._cached_text != self.original_content
        self._update_status_with_file()

    def _load_content(self, content: str, file: Optional[Path]) -> None:
        """Put ``content`` in the buffer and reset the modified bookkeeping."""
        self._cached_text = content
        self.original_content = content
        self.current_file = file
        self.is_modified = False
        if self._text_area is not None:
            self._text_area.load_text(content)

    # ------------------------------------------------------------------ actions
    def action_insert_tab(self) -> None:
        """Insert a tab character."""
        self._require_text_area().insert(TAB_SPACES)

    def action_select_all(self) -> None:
        """Select all text in the editor."""
        self._require_text_area().select_all()

    def action_undo(self) -> None:
        """Undo the last change in the editor."""
        self._require_text_area().undo()

    def action_redo(self) -> None:
        """Redo the last undone change in the editor."""
        self._require_text_area().redo()

    def _require_text_area(self) -> TextArea:
        if self._text_area is None:
            self._text_area = self.query_one(f"#{WidgetIDs.TEXT_AREA}", TextArea)
        return self._text_area

    def action_save(self) -> None:
        """Save the current document."""
        if self.current_file is not None:
            self._write_document(self.current_file)
            return

        def handle_filename(filename: Optional[str]) -> None:
            if filename:
                self._save_as(filename)

        self.app.push_screen(FilenamePrompt(), handle_filename)

    def _save_as(self, filename: str) -> None:
        """Resolve a user-supplied filename and save, confirming overwrites."""
        try:
            safe_filename = sanitize_filename(filename)
        except ValueError as e:
            self._update_status(f"Invalid filename: {e}")
            return

        stem = safe_filename.rsplit(".", 1)[0] if "." in safe_filename else safe_filename
        target = self.documents_dir / f"{stem}.md"

        try:
            target.resolve().relative_to(self.documents_dir.resolve())
        except ValueError:
            self._update_status("Error: Invalid file path")
            return

        if target.exists() and target != self.current_file:
            def handle_overwrite(confirmed: Optional[bool]) -> None:
                if confirmed:
                    self._write_document(target)

            self.app.push_screen(
                ConfirmDialog(f"'{target.name}' already exists. Overwrite it?"),
                handle_overwrite,
            )
            return

        self._write_document(target)

    def _write_document(self, target: Path) -> None:
        """Write the buffer to ``target`` atomically and update the UI."""
        if not storage.write_text_atomic(target, self._cached_text):
            self._update_status(f"Error saving file: {target.name}")
            return

        self.current_file = target
        self.original_content = self._cached_text
        self.is_modified = False

        if self.autosave_file.exists():
            self.autosave_file.unlink(missing_ok=True)

        self._update_status_with_file()
        logger.info("Saved %s", target)

    def action_open(self) -> None:
        """Open a file from the notes directory."""
        def handle_file_selection(selected_file: Optional[Path]) -> None:
            if not selected_file:
                return

            resolved = selected_file.resolve()
            try:
                resolved.relative_to(self.documents_dir.resolve())
            except ValueError:
                self._update_status("Error: Invalid file path")
                return

            content = storage.read_text(resolved)
            if content == "" and not resolved.exists():
                self._update_status("Error: File no longer exists")
                return

            self._load_content(content, resolved)
            self._update_status_with_file()

        self.app.push_screen(FileBrowser(self.documents_dir), handle_file_selection)

    def action_new(self) -> None:
        """Create a new document."""
        def confirm_new(confirmed: Optional[bool]) -> None:
            if confirmed:
                if self.is_modified:
                    self.save_snapshot()
                self._load_content("", None)
                self._update_status_with_file()

        if self.is_modified:
            self.app.push_screen(
                ConfirmDialog("You have unsaved changes. Create a new document anyway?"),
                confirm_new,
            )
        else:
            confirm_new(True)

    def action_rename(self) -> None:
        """Rename the current file."""
        if not self.current_file:
            self._update_status("Cannot rename: No file is currently open")
            return

        def handle_rename(filename: Optional[str]) -> None:
            if not filename or self.current_file is None:
                return

            try:
                safe_filename = sanitize_filename(filename)
            except ValueError as e:
                self._update_status(f"Invalid filename: {e}")
                return

            stem = safe_filename.rsplit(".", 1)[0] if "." in safe_filename else safe_filename
            new_path = self.documents_dir / f"{stem}.md"

            try:
                new_path.resolve().relative_to(self.documents_dir.resolve())
            except ValueError:
                self._update_status("Error: Invalid file path")
                return

            if new_path == self.current_file:
                self._update_status("File name unchanged")
                return

            if new_path.exists():
                self._update_status(f"Error: File '{new_path.name}' already exists")
                return

            old_path = self.current_file
            try:
                old_path.rename(new_path)
            except FileNotFoundError:
                self._update_status("Error: Original file not found")
                return
            except OSError as e:
                self._update_status(f"Error renaming file: {e}")
                return

            self.current_file = new_path
            self._update_status_with_file()
            logger.info("Renamed %s -> %s", old_path.name, new_path.name)

        self.app.push_screen(RenamePrompt(self.current_file.name), handle_rename)

    def action_back(self) -> None:
        """Return to the main menu."""
        def confirm_back(confirmed: Optional[bool]) -> None:
            if confirmed:
                self.app.pop_screen()

        if self.is_modified:
            self.save_snapshot()
            self.app.push_screen(
                ConfirmDialog("You have unsaved changes. Leave the editor anyway?"),
                confirm_back,
            )
        else:
            self.app.pop_screen()

    # -------------------------------------------------------------------- status
    def _update_status(self, message: str) -> None:
        """Update the status message."""
        try:
            status = self.query_one(f"#{WidgetIDs.EDITOR_STATUS}", Static)
            status.update(f"  {message}")
        except NoMatches:
            # Status widget not available (e.g. during teardown)
            pass

    def _update_status_with_file(self) -> None:
        """Update status with current filename and modified indicator."""
        name = self.current_file.name if self.current_file else "Untitled"
        modified = " [bold red]*[/]" if self.is_modified else ""
        self._update_status(f"{name}{modified}")


# Custom CSS for the editor
EditorScreen.CSS = """
EditorScreen {
    border: double $primary;
}

#editor-container {
    width: 100%;
    height: 100%;
    padding: 0;
    background: $surface;
}

#editor-status {
    color: $text-muted;
    padding: 0 2;
    background: $surface;
    height: 1;
}

#text-area {
    height: 1fr;
    border: none;
    background: $surface;
    padding: 0 1;
}
"""
