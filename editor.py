"""
Text/Markdown Editor - Distraction-free writing
"""

from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Header, Footer, TextArea, Static, Button
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from pathlib import Path
import os
import subprocess
import platform

from constants import (
    FOCUS_INDICATOR, FOCUS_COLOR, DIM_COLOR,
    TAB_SPACES, MAX_FILENAME_LENGTH, FOCUS_TIMER_DELAY
)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize and validate a filename to prevent security issues.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        A safe filename string
        
    Raises:
        ValueError: If the filename is invalid or dangerous
    """
    if not filename or not filename.strip():
        raise ValueError("Filename cannot be empty")
    
    filename = filename.strip()
    
    # Remove path separators to prevent directory traversal
    if '/' in filename or '\\' in filename:
        raise ValueError("Filename cannot contain path separators (/ or \\)")
    
    # Check for parent directory references
    if filename in ('.', '..') or filename.startswith('.'):
        raise ValueError("Filename cannot start with '.' or be a directory reference")
    
    # Remove dangerous characters and control characters
    dangerous_chars = '<>:"|?*\0'
    for char in dangerous_chars:
        if char in filename:
            raise ValueError(f"Filename cannot contain '{char}' character")
    
    # Check for non-printable characters
    if not all(c.isprintable() or c.isspace() for c in filename):
        raise ValueError("Filename contains invalid characters")
    
    # Check for Windows reserved names (case-insensitive)
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    name_without_ext = filename.rsplit('.', 1)[0].upper()
    if name_without_ext in reserved_names:
        raise ValueError(f"'{filename}' is a reserved system name")
    
    # Limit filename length (most filesystems support 255, but leave room for extension)
    if len(filename) > MAX_FILENAME_LENGTH:
        raise ValueError(f"Filename is too long (max {MAX_FILENAME_LENGTH} characters)")
    
    return filename


class ConfirmDialog(ModalScreen):
    """Modal dialog for confirming actions."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self.message = message
    
    def compose(self) -> ComposeResult:
        """Create the confirmation dialog interface."""
        with Container(id="confirm-container"):
            yield Static("CONFIRM", id="confirm-title")
            yield Static(self.message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button("Yes", variant="error", id="confirm-yes")
                yield Button("No", variant="primary", id="confirm-no")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "confirm-yes":
            self.dismiss(True)
        else:
            self.dismiss(False)
    
    def on_key(self, event) -> None:
        """Handle escape and enter keys."""
        if event.key == "escape":
            self.dismiss(False)
        elif event.key == "enter":
            # Default to No on enter
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

#confirm-buttons {
    height: auto;
    align: center middle;
}

#confirm-buttons Button {
    margin: 0 1;
}
"""


class ClickablePath(Static, can_focus=True):
    """A clickable path that opens the folder."""
    
    def __init__(self, path: Path, **kwargs):
        super().__init__(**kwargs)
        self.path = path
    
    def render(self) -> str:
        """Render the path."""
        if self.has_focus:
            return f"Location: [{FOCUS_COLOR}][link]{self.path}[/link][/] [{DIM_COLOR}](click to open)[/]"
        return f"Location: [link]{self.path}[/link] [{DIM_COLOR}](click to open)[/]"
    
    def on_click(self) -> None:
        """Open the folder when clicked in the system's file manager."""
        try:
            system = platform.system()
            path_str = str(self.path)
            
            if system == 'Darwin':  # macOS
                subprocess.Popen(['open', path_str])
            elif system == 'Windows':
                subprocess.Popen(['explorer', path_str])
            else:  # Linux and other Unix-like systems
                subprocess.Popen(['xdg-open', path_str])
        except FileNotFoundError:
            # File manager command not available
            pass
        except (OSError, subprocess.SubprocessError) as e:
            print(f"Warning: Could not open folder: {e}")
    
    def on_focus(self) -> None:
        """Refresh when focused."""
        self.refresh()
    
    def on_blur(self) -> None:
        """Refresh when focus lost."""
        self.refresh()


class FilenamePrompt(ModalScreen):
    """Modal screen for entering a filename."""
    
    def compose(self) -> ComposeResult:
        """Create the filename prompt interface."""
        from textual.widgets import Input, Label
        from textual.containers import Vertical
        
        with Container(id="prompt-container"):
            yield Static("SAVE FILE", id="prompt-title")
            yield Label("Enter filename (without .md):", id="prompt-label")
            yield Input(placeholder="my-note", id="filename-input")
            yield Static("Press Enter to save, Escape to cancel", id="prompt-hint")
            yield Static("Alphanumeric, spaces, hyphens, underscores only", id="prompt-rules")
    
    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one("#filename-input").focus()
    
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


class FileItem(Static, can_focus=True):
    """A clickable file item in the browser."""
    
    def __init__(self, filename: str, filepath: Path, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.filepath = filepath
    
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


class FileBrowser(ModalScreen):
    """Modal screen for browsing and selecting files."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
        Binding("enter", "select", "Open", show=False),
        Binding("down,j", "cursor_down", "Next", show=False),
        Binding("up,k", "cursor_up", "Previous", show=False),
    ]
    
    def __init__(self, documents_dir: Path):
        super().__init__()
        self.documents_dir = documents_dir
        self.selected_file = None
    
    def compose(self) -> ComposeResult:
        """Create the file browser interface."""
        from textual.widgets import Footer
        files = sorted(self.documents_dir.glob("*.md"), key=os.path.getmtime, reverse=True)
        
        yield Container(
            Static("OPEN FILE", id="browser-title"),
            ClickablePath(self.documents_dir, id="browser-path"),
            Static("", id="browser-spacer"),
            Vertical(
                *(FileItem(
                    f"{file.stem}  [dim]{self._format_time(os.path.getmtime(file))}[/]",
                    file
                ) for file in files) if files else [Static("No files found. Save a file first!", id="no-files")],
                id="file-list"
            ),
            id="browser-container"
        )
        yield Footer()
    
    def _format_time(self, timestamp: float) -> str:
        """Format timestamp for display."""
        from datetime import datetime
        mod_time = datetime.fromtimestamp(timestamp)
        return mod_time.strftime("%Y-%m-%d %H:%M")
    
    def on_mount(self) -> None:
        """Focus first file when mounted."""
        def set_initial_focus():
            try:
                first_item = self.query_one(FileItem)
                self.set_focus(first_item)
            except Exception:
                # No file items available, nothing to focus
                pass
        # Use set_timer for a slight delay to ensure rendering is complete
        self.set_timer(FOCUS_TIMER_DELAY, set_initial_focus)
    
    def on_click(self, event) -> None:
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
    
    def action_cursor_down(self) -> None:
        """Move to the next file item."""
        # Get all focusable items (FileItem and ClickablePath)
        file_items = list(self.query(FileItem))
        
        # Build focusable items list
        focusable = []
        try:
            clickable_path = self.query_one(ClickablePath)
            focusable.append(clickable_path)
        except Exception:
            # No ClickablePath widget found
            pass
        focusable.extend(file_items)
        
        if not focusable:
            return
        
        focused = self.focused
        if focused in focusable:
            current_index = focusable.index(focused)
            next_index = (current_index + 1) % len(focusable)
            focusable[next_index].focus()
        else:
            # If nothing focused, focus first
            focusable[0].focus()
    
    def action_cursor_up(self) -> None:
        """Move to the previous file item."""
        # Get all focusable items (FileItem and ClickablePath)
        file_items = list(self.query(FileItem))
        
        # Build focusable items list
        focusable = []
        try:
            clickable_path = self.query_one(ClickablePath)
            focusable.append(clickable_path)
        except Exception:
            # No ClickablePath widget found
            pass
        focusable.extend(file_items)
        
        if not focusable:
            return
        
        focused = self.focused
        if focused in focusable:
            current_index = focusable.index(focused)
            prev_index = (current_index - 1) % len(focusable)
            focusable[prev_index].focus()
        else:
            # If nothing focused, focus last
            focusable[-1].focus()


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
        Binding("escape", "back", "Back", priority=True),
        Binding("tab", "insert_tab", "Tab", show=False, priority=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.is_modified = False  # Track if content has been modified
        self.original_content = ""  # Store original content for comparison
        # Save to app directory instead of Documents
        self.documents_dir = Path(__file__).parent / "notes"
        self.documents_dir.mkdir(parents=True, exist_ok=True)
    
    def compose(self) -> ComposeResult:
        """Create the editor interface."""
        yield Header(show_clock=True)
        yield Container(
            Static("", id="editor-status"),
            TextArea(id="text-area", show_line_numbers=True),
            id="editor-container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the editor when mounted."""
        text_area = self.query_one("#text-area", TextArea)
        text_area.focus()
        self._update_status_with_file()
        
        # Watch for changes to track modified state
        text_area.watch_text = self._on_text_changed
    
    def _on_text_changed(self, new_text: str) -> None:
        """Called when text area content changes."""
        # Check if content differs from original
        self.is_modified = (new_text != self.original_content)
        self._update_status_with_file()
    
    def action_insert_tab(self) -> None:
        """Insert a tab character."""
        text_area = self.query_one("#text-area", TextArea)
        text_area.insert(TAB_SPACES)
    
    def action_save(self) -> None:
        """Save the current document."""
        def handle_filename(filename):
            if filename:
                text_area = self.query_one("#text-area", TextArea)
                content = text_area.text
                
                try:
                    # Sanitize the filename first
                    safe_filename = sanitize_filename(filename)
                    
                    # Ensure .md extension
                    if not safe_filename.endswith('.md'):
                        safe_filename = f"{safe_filename}.md"
                    
                    # Verify the final path is within the documents directory
                    self.current_file = self.documents_dir / safe_filename
                    
                    # Double-check the resolved path is still within documents_dir
                    try:
                        self.current_file.resolve().relative_to(self.documents_dir.resolve())
                    except ValueError:
                        self._update_status("Error: Invalid file path")
                        return
                    
                    self.current_file.write_text(content)
                    self.is_modified = False  # Reset modified flag
                    self.original_content = content  # Update original content
                    self._update_status_with_file()
                except ValueError as e:
                    # Validation error from sanitize_filename
                    self._update_status(f"Invalid filename: {e}")
                except (OSError, IOError) as e:
                    self._update_status(f"Error saving file: {e}")
                except Exception as e:
                    self._update_status(f"Unexpected error: {e}")
        
        # If file already has a name, just save it
        if self.current_file is not None:
            text_area = self.query_one("#text-area", TextArea)
            content = text_area.text
            try:
                self.current_file.write_text(content)
                self.is_modified = False  # Reset modified flag
                self.original_content = content  # Update original content
                self._update_status_with_file()
            except (OSError, IOError) as e:
                self._update_status(f"Error saving file: {e}")
            except Exception as e:
                self._update_status(f"Unexpected error: {e}")
        else:
            # Prompt for filename
            self.app.push_screen(FilenamePrompt(), handle_filename)
    
    def action_open(self) -> None:
        """Open a file from the documents directory."""
        def handle_file_selection(selected_file):
            if selected_file:
                try:
                    # Verify the selected file is within the documents directory
                    try:
                        selected_file.resolve().relative_to(self.documents_dir.resolve())
                    except ValueError:
                        self._update_status("Error: Invalid file path")
                        return
                    
                    self.current_file = selected_file
                    content = self.current_file.read_text()
                    text_area = self.query_one("#text-area", TextArea)
                    text_area.load_text(content)
                    self.is_modified = False  # Reset modified flag
                    self.original_content = content  # Store original content
                    self._update_status_with_file()
                except FileNotFoundError:
                    self._update_status(f"Error: File not found")
                except (OSError, IOError) as e:
                    self._update_status(f"Error reading file: {e}")
                except UnicodeDecodeError:
                    self._update_status(f"Error: File is not valid text")
                except Exception as e:
                    self._update_status(f"Unexpected error: {e}")
        
        self.app.push_screen(FileBrowser(self.documents_dir), handle_file_selection)
    
    def action_new(self) -> None:
        """Create a new document."""
        def confirm_new(confirmed: bool) -> None:
            if confirmed:
                text_area = self.query_one("#text-area", TextArea)
                text_area.clear()
                self.current_file = None
                self.is_modified = False
                self.original_content = ""
                self._update_status_with_file()
        
        # Check if there are unsaved changes
        if self.is_modified:
            self.app.push_screen(
                ConfirmDialog("You have unsaved changes. Create new document anyway?"),
                confirm_new
            )
        else:
            confirm_new(True)
    
    def action_back(self) -> None:
        """Return to the main menu."""
        def confirm_back(confirmed: bool) -> None:
            if confirmed:
                self.app.pop_screen()
        
        # Check if there are unsaved changes
        if self.is_modified:
            self.app.push_screen(
                ConfirmDialog("You have unsaved changes. Exit anyway?"),
                confirm_back
            )
        else:
            self.app.pop_screen()
    
    def _update_status(self, message: str) -> None:
        """Update the status message."""
        status = self.query_one("#editor-status", Static)
        status.update(f"  {message}")
    
    def _update_status_with_file(self) -> None:
        """Update status with current filename and modified indicator."""
        if self.current_file:
            filename = self.current_file.name
            modified_indicator = " [bold red]*[/]" if self.is_modified else ""
            self._update_status(f"{filename}{modified_indicator}")
        else:
            modified_indicator = " [bold red]*[/]" if self.is_modified else ""
            self._update_status(f"Untitled{modified_indicator}")


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
