"""
Text/Markdown Editor - Distraction-free writing
"""

from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Header, Footer, TextArea, Static, DirectoryTree
from textual.containers import Container, Vertical
from textual.binding import Binding
from pathlib import Path
import os
import subprocess


class ClickablePath(Static, can_focus=True):
    """A clickable path that opens the folder."""
    
    def __init__(self, path: Path, **kwargs):
        super().__init__(**kwargs)
        self.path = path
    
    def render(self) -> str:
        """Render the path."""
        if self.has_focus:
            return f"Location: [bold cyan][link]{self.path}[/link][/] [dim](click to open)[/]"
        return f"Location: [link]{self.path}[/link] [dim](click to open)[/]"
    
    def on_click(self) -> None:
        """Open the folder when clicked."""
        try:
            # Use xdg-open on Linux to open the folder in file manager
            subprocess.Popen(['xdg-open', str(self.path)])
        except Exception:
            pass
    
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
            return f"[bold cyan]▸[/] {self.filename}"
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
        Binding("down,j", "focus_next", "Next", show=False),
        Binding("up,k", "focus_previous", "Previous", show=False),
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
            except:
                pass
        # Use set_timer for a slight delay to ensure rendering is complete
        self.set_timer(0.01, set_initial_focus)
    
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
        self._update_status("Ready")
    
    def action_insert_tab(self) -> None:
        """Insert a tab character."""
        text_area = self.query_one("#text-area", TextArea)
        text_area.insert("    ")  # Insert 4 spaces as tab
    
    def action_save(self) -> None:
        """Save the current document."""
        def handle_filename(filename):
            if filename:
                text_area = self.query_one("#text-area", TextArea)
                content = text_area.text
                
                # Ensure .md extension
                if not filename.endswith('.md'):
                    filename = f"{filename}.md"
                
                self.current_file = self.documents_dir / filename
                
                try:
                    self.current_file.write_text(content)
                    self._update_status(f"Saved: {self.current_file.name}")
                except Exception as e:
                    self._update_status(f"Error: {str(e)}")
        
        # If file already has a name, just save it
        if self.current_file is not None:
            text_area = self.query_one("#text-area", TextArea)
            content = text_area.text
            try:
                self.current_file.write_text(content)
                self._update_status(f"Saved: {self.current_file.name}")
            except Exception as e:
                self._update_status(f"Error: {str(e)}")
        else:
            # Prompt for filename
            self.app.push_screen(FilenamePrompt(), handle_filename)
    
    def action_open(self) -> None:
        """Open a file from the documents directory."""
        def handle_file_selection(selected_file):
            if selected_file:
                try:
                    self.current_file = selected_file
                    content = self.current_file.read_text()
                    text_area = self.query_one("#text-area", TextArea)
                    text_area.load_text(content)
                    self._update_status(f"Opened: {self.current_file.name}")
                except Exception as e:
                    self._update_status(f"Error: {str(e)}")
        
        self.app.push_screen(FileBrowser(self.documents_dir), handle_file_selection)
    
    def action_new(self) -> None:
        """Create a new document."""
        text_area = self.query_one("#text-area", TextArea)
        text_area.clear()
        self.current_file = None
        self._update_status("New document")
    
    def action_back(self) -> None:
        """Return to the main menu."""
        self.app.pop_screen()
    
    def _update_status(self, message: str) -> None:
        """Update the status message."""
        status = self.query_one("#editor-status", Static)
        status.update(f"  {message}")


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
