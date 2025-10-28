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


class FileItem(Static):
    """A clickable file item in the browser."""
    
    def __init__(self, filename: str, filepath: Path, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.filepath = filepath
        self.can_focus = True
    
    def render(self) -> str:
        """Render the file item."""
        if self.has_focus:
            return f"[bold cyan]▸ 📄[/] [bold]{self.filename}[/]"
        return f"  📄  {self.filename}"
    
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
    ]
    
    def __init__(self, documents_dir: Path):
        super().__init__()
        self.documents_dir = documents_dir
        self.selected_file = None
    
    def compose(self) -> ComposeResult:
        """Create the file browser interface."""
        files = sorted(self.documents_dir.glob("*.md"), key=os.path.getmtime, reverse=True)
        
        with Container(id="browser-container"):
            yield Static("OPEN FILE", id="browser-title")
            yield Static(f"📁 {self.documents_dir}", id="browser-path")
            
            if not files:
                yield Static("No files found. Create your first note!", id="no-files")
            else:
                with Vertical(id="file-list"):
                    for file in files:
                        # Show relative time
                        mtime = os.path.getmtime(file)
                        from datetime import datetime
                        mod_time = datetime.fromtimestamp(mtime)
                        time_str = mod_time.strftime("%Y-%m-%d %H:%M")
                        filename = f"{file.name}  [dim]{time_str}[/]"
                        yield FileItem(filename, file)
    
    def on_mount(self) -> None:
        """Focus first file when mounted."""
        try:
            first_item = self.query_one(FileItem)
            first_item.focus()
        except:
            pass
    
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
    align: center middle;
}

#browser-container {
    border: double $primary;
    width: 70%;
    max-width: 80;
    height: auto;
    max-height: 70%;
    background: $surface;
    padding: 2;
}

#browser-title {
    text-align: center;
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}

#browser-path {
    text-align: center;
    color: $text-muted;
    margin-bottom: 2;
}

#file-list {
    height: auto;
    max-height: 25;
    overflow-y: auto;
    border: solid $primary-darken-2;
    padding: 1;
}

#no-files {
    text-align: center;
    color: $text-muted;
    padding: 2;
}

FileItem {
    height: auto;
    padding: 1 2;
    margin: 0;
}

FileItem:focus {
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
    
    def action_save(self) -> None:
        """Save the current document."""
        text_area = self.query_one("#text-area", TextArea)
        content = text_area.text
        
        if self.current_file is None:
            # Generate a filename based on timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"note_{timestamp}.md"
            self.current_file = self.documents_dir / filename
        
        try:
            self.current_file.write_text(content)
            self._update_status(f"Saved: {self.current_file.name}")
        except Exception as e:
            self._update_status(f"Error: {str(e)}")
    
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
