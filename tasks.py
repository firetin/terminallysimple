"""
Task Manager - Simple to-do list
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Footer, Static, Button, Input, Label
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.binding import Binding
from textual.widget import Widget

from base_screen import NavigableMixin
from constants import FOCUS_INDICATOR, FOCUS_COLOR, DIM_COLOR, FOCUS_TIMER_DELAY, WidgetIDs
from widgets.system_header import SystemHeader

logger = logging.getLogger(__name__)


class Task:
    """Represents a single task."""
    
    def __init__(self, text: str, completed: bool = False, task_id: Optional[int] = None) -> None:
        self.text: str = text
        self.completed: bool = completed
        self.id: int = task_id if task_id is not None else id(self)
        self.created_at: datetime = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary for storage."""
        return {
            "id": self.id,
            "text": self.text,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        task = cls(data["text"], data["completed"], data["id"])
        try:
            task.created_at = datetime.fromisoformat(data["created_at"])
        except (KeyError, ValueError):
            task.created_at = datetime.now()
        return task


class TaskStorage:
    """Manages task persistence."""
    
    def __init__(self) -> None:
        self.data_dir: Path = Path.home() / ".config" / "terminallysimple"
        self.tasks_file: Path = self.data_dir / "tasks.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_tasks(self) -> list[Task]:
        """Load tasks from file."""
        if not self.tasks_file.exists():
            return []
        
        try:
            with open(self.tasks_file, 'r') as f:
                data = json.load(f)
                return [Task.from_dict(t) for t in data]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error loading tasks: {e}")
            return []
        except (OSError, IOError) as e:
            logger.error(f"Could not read tasks file: {e}")
            return []
    
    def save_tasks(self, tasks: list[Task]) -> bool:
        """Save tasks to file."""
        try:
            with open(self.tasks_file, 'w') as f:
                json.dump([t.to_dict() for t in tasks], f, indent=2)
            return True
        except (OSError, IOError) as e:
            logger.error(f"Could not save tasks: {e}")
            return False


class TaskInput(ModalScreen[Optional[str]]):
    """Modal screen for adding or editing a task."""
    
    def __init__(self, initial_text: str = "", title: str = "ADD TASK", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.initial_text: str = initial_text
        self.title_text: str = title
    
    def compose(self) -> ComposeResult:
        """Create the task input interface."""
        with Container(id="task-input-container"):
            yield Static(self.title_text, id="task-input-title")
            yield Label("Enter task description:", id="task-input-label")
            yield Input(value=self.initial_text, placeholder="What needs to be done?", id="task-input-field")
            yield Static("Press Enter to save, Escape to cancel", id="task-input-hint")
    
    def on_mount(self) -> None:
        """Focus the input when mounted."""
        input_widget = self.query_one("#task-input-field", Input)
        input_widget.focus()
        if self.initial_text:
            input_widget.action_end()
    
    def on_input_submitted(self, event) -> None:
        """Handle Enter key in input."""
        text = event.value.strip()
        self.dismiss(text if text else None)
    
    def on_key(self, event) -> None:
        """Handle escape key."""
        if event.key == "escape":
            self.dismiss(None)


TaskInput.CSS = """
TaskInput {
    align: center middle;
}

#task-input-container {
    border: double $primary;
    width: 70;
    height: auto;
    background: $surface;
    padding: 2;
}

#task-input-title {
    text-align: center;
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}

#task-input-label {
    color: $text;
    margin-bottom: 1;
}

#task-input-field {
    margin-bottom: 1;
}

#task-input-hint {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
}
"""


class ConfirmDeleteDialog(ModalScreen[bool]):
    """Modal dialog for confirming task deletion."""
    
    def __init__(self, task_text: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.task_text: str = task_text
    
    def compose(self) -> ComposeResult:
        """Create the confirmation dialog interface."""
        with Container(id="confirm-delete-container"):
            yield Static("DELETE TASK", id="confirm-delete-title")
            yield Static(f"Delete this task?\n\n{self.task_text}", id="confirm-delete-message")
            yield Static("Press 'y' to delete, 'n' to cancel", id="confirm-delete-hint")
    
    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "y":
            self.dismiss(True)
        elif event.key in ("n", "escape"):
            self.dismiss(False)


ConfirmDeleteDialog.CSS = """
ConfirmDeleteDialog {
    align: center middle;
}

#confirm-delete-container {
    border: double $error;
    width: 60;
    height: auto;
    background: $surface;
    padding: 2;
}

#confirm-delete-title {
    text-align: center;
    text-style: bold;
    color: $error;
    margin-bottom: 1;
}

#confirm-delete-message {
    text-align: center;
    color: $text;
    margin-bottom: 2;
}

#confirm-delete-hint {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
}
"""


class TaskItem(Static, can_focus=True):
    """A single task item in the list."""
    
    def __init__(self, task: Task, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.task_data: Task = task
    
    def render(self) -> str:
        """Render the task item."""
        checkbox = "☑" if self.task_data.completed else "☐"
        
        if self.task_data.completed:
            text = f"[dim strikethrough]{self.task_data.text}[/]"
        else:
            text = self.task_data.text
        
        if self.has_focus:
            return f"[{FOCUS_COLOR}]{FOCUS_INDICATOR}[/] {checkbox} {text}"
        return f"  {checkbox} {text}"
    
    def on_focus(self) -> None:
        """Refresh when focused."""
        self.refresh()
    
    def on_blur(self) -> None:
        """Refresh when focus lost."""
        self.refresh()
    
    def on_click(self) -> None:
        """Toggle task completion on click."""
        # Get the parent screen and call its toggle method
        screen = self.screen
        if isinstance(screen, TaskManagerScreen):
            screen.toggle_task_by_id(self.task_data.id)


class TaskManagerScreen(NavigableMixin, Screen):
    """Task manager screen with to-do list."""
    
    BINDINGS = [
        Binding("a", "add_task", "Add", show=True),
        Binding("d", "delete_task", "Delete", show=True),
        Binding("e", "edit_task", "Edit", show=True),
        Binding("space", "toggle_task", "Toggle", show=True),
        Binding("c", "clear_completed", "Clear Done", show=True),
        Binding("escape", "back", "Back", priority=True),
        Binding("enter", "toggle_task", "Toggle", show=False),
        Binding("down,j", "cursor_down", "Next", show=False),
        Binding("up,k", "cursor_up", "Previous", show=False),
        Binding("shift+up", "move_task_up", "Move Up", show=True, priority=True),
        Binding("shift+down", "move_task_down", "Move Down", show=True, priority=True),
    ]
    
    def __init__(self) -> None:
        super().__init__()
        self.storage: TaskStorage = TaskStorage()
        self.tasks: list[Task] = []
        self.next_id: int = 1
        self.focused: Optional[Widget] = None
    
    def compose(self) -> ComposeResult:
        """Create the task manager interface."""
        yield SystemHeader(show_clock=True)
        yield Container(
            Static("TASK MANAGER", id="tasks-title"),
            Static("No tasks yet. Press 'a' to add one!", id="tasks-empty"),
            ScrollableContainer(id="tasks-list"),
            id="tasks-container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the task manager when mounted."""
        self.tasks = self.storage.load_tasks()
        if self.tasks:
            self.next_id = max(t.id for t in self.tasks) + 1
        self._refresh_task_list()
    
    def _refresh_task_list(self) -> None:
        """Refresh the task list display."""
        task_list = self.query_one("#tasks-list", ScrollableContainer)
        empty_msg = self.query_one("#tasks-empty", Static)
        
        # Clear existing task items
        task_list.remove_children()
        
        if not self.tasks:
            empty_msg.display = True
            return
        
        empty_msg.display = False
        
        # Add task items
        for task in self.tasks:
            task_list.mount(TaskItem(task))
        
        # Focus first task if available
        def set_initial_focus() -> None:
            try:
                first_item = self.query_one(TaskItem)
                self.set_focus(first_item)
            except Exception:
                pass
        
        self.set_timer(FOCUS_TIMER_DELAY, set_initial_focus)
    
    def _save_tasks(self) -> None:
        """Save tasks to storage."""
        self.storage.save_tasks(self.tasks)
    
    def action_add_task(self) -> None:
        """Add a new task."""
        def handle_task_input(text: Optional[str]) -> None:
            if text:
                new_task = Task(text, task_id=self.next_id)
                self.next_id += 1
                self.tasks.append(new_task)
                self._save_tasks()
                self._refresh_task_list()
        
        self.app.push_screen(TaskInput(), handle_task_input)
    
    def action_delete_task(self) -> None:
        """Delete the focused task."""
        focused = self.focused
        if not isinstance(focused, TaskItem):
            return
        
        task_to_delete = focused.task_data
        
        def handle_confirm(confirmed: bool) -> None:
            if confirmed:
                self.tasks = [t for t in self.tasks if t.id != task_to_delete.id]
                self._save_tasks()
                self._refresh_task_list()
        
        self.app.push_screen(
            ConfirmDeleteDialog(task_to_delete.text),
            handle_confirm
        )
    
    def action_edit_task(self) -> None:
        """Edit the focused task."""
        focused = self.focused
        if not isinstance(focused, TaskItem):
            return
        
        task_to_edit = focused.task_data
        
        def handle_task_input(text: Optional[str]) -> None:
            if text:
                task_to_edit.text = text
                self._save_tasks()
                self._refresh_task_list()
        
        self.app.push_screen(
            TaskInput(initial_text=task_to_edit.text, title="EDIT TASK"),
            handle_task_input
        )
    
    def action_toggle_task(self) -> None:
        """Toggle the completed status of the focused task."""
        focused = self.focused
        if not isinstance(focused, TaskItem):
            return
        
        task = focused.task_data
        task.completed = not task.completed
        self._save_tasks()
        focused.refresh()
    
    def action_clear_completed(self) -> None:
        """Remove all completed tasks."""
        completed_count = sum(1 for t in self.tasks if t.completed)
        if completed_count == 0:
            return
        
        def handle_confirm(confirmed: bool) -> None:
            if confirmed:
                self.tasks = [t for t in self.tasks if not t.completed]
                self._save_tasks()
                self._refresh_task_list()
        
        self.app.push_screen(
            ConfirmDeleteDialog(f"Clear {completed_count} completed task(s)?"),
            handle_confirm
        )
    
    def action_back(self) -> None:
        """Return to the main menu."""
        self.app.pop_screen()
    
    def action_move_task_up(self) -> None:
        """Move the focused task up in the list."""
        focused = self.focused
        if not isinstance(focused, TaskItem):
            return
        
        task = focused.task_data
        task_index = next((i for i, t in enumerate(self.tasks) if t.id == task.id), None)
        
        if task_index is not None and task_index > 0:
            # Swap with previous task
            self.tasks[task_index], self.tasks[task_index - 1] = self.tasks[task_index - 1], self.tasks[task_index]
            self._save_tasks()
            self._refresh_task_list()
            
            # Refocus the task that was moved
            def refocus_task() -> None:
                for item in self.query(TaskItem):
                    if item.task_data.id == task.id:
                        self.set_focus(item)
                        break
            self.set_timer(FOCUS_TIMER_DELAY, refocus_task)
    
    def action_move_task_down(self) -> None:
        """Move the focused task down in the list."""
        focused = self.focused
        if not isinstance(focused, TaskItem):
            return
        
        task = focused.task_data
        task_index = next((i for i, t in enumerate(self.tasks) if t.id == task.id), None)
        
        if task_index is not None and task_index < len(self.tasks) - 1:
            # Swap with next task
            self.tasks[task_index], self.tasks[task_index + 1] = self.tasks[task_index + 1], self.tasks[task_index]
            self._save_tasks()
            self._refresh_task_list()
            
            # Refocus the task that was moved
            def refocus_task() -> None:
                for item in self.query(TaskItem):
                    if item.task_data.id == task.id:
                        self.set_focus(item)
                        break
            self.set_timer(FOCUS_TIMER_DELAY, refocus_task)
    
    def toggle_task_by_id(self, task_id: int) -> None:
        """Toggle task completion by task ID (called from TaskItem click)."""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task:
            task.completed = not task.completed
            self._save_tasks()
            # Refresh the specific task item
            for item in self.query(TaskItem):
                if item.task_data.id == task_id:
                    item.refresh()
                    break
    
    def get_focusable_items(self) -> list[Widget]:
        """Return task items for navigation."""
        return list(self.query(TaskItem))


# Custom CSS for the task manager
TaskManagerScreen.CSS = """
TaskManagerScreen {
    border: double $primary;
}

#tasks-container {
    width: 100%;
    height: 100%;
    padding: 2 4;
    background: $surface;
}

#tasks-title {
    text-align: left;
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}

#tasks-empty {
    text-align: left;
    color: $text-muted;
    margin-bottom: 2;
}

#tasks-list {
    height: 1fr;
    overflow-y: auto;
}

TaskItem {
    height: auto;
    padding: 0 2;
    margin: 0;
}

TaskItem:focus {
    background: $boost;
}

TaskItem:focus-within {
    background: $boost;
}
"""
