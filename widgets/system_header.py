"""
Custom header with system resource monitoring
"""

import logging
from datetime import datetime
from typing import Optional

import psutil
from rich.text import Text
from textual.app import ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widgets import Static
from textual.widget import Widget

logger = logging.getLogger(__name__)


class SystemHeader(Widget):
    """Header widget with CPU and RAM usage display."""
    
    DEFAULT_CSS = """
    SystemHeader {
        dock: top;
        width: 100%;
        height: 1;
        background: $panel;
        color: $text;
    }
    
    SystemHeader > Static {
        width: 100%;
        height: 1;
        padding: 0 1;
        background: $panel;
        color: $text;
    }
    """
    
    cpu_usage: reactive[float] = reactive(0.0)
    ram_usage: reactive[float] = reactive(0.0)
    
    def __init__(self, show_clock: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        self.show_clock = show_clock
        self._update_timer: Optional[object] = None
    
    def compose(self) -> ComposeResult:
        """Compose the header with a Static widget for content."""
        yield Static(id="header-content")
    
    def on_mount(self) -> None:
        """Start the resource monitoring when mounted."""
        # Initial update
        self._update_display()
        # Update system stats every second
        self._update_timer = self.set_interval(1.0, self._update_system_stats, pause=False)
    
    def on_unmount(self) -> None:
        """Stop the resource monitoring when unmounted."""
        if self._update_timer:
            self._update_timer.stop()
    
    def _update_system_stats(self) -> None:
        """Update CPU and RAM usage statistics."""
        try:
            # Get CPU usage (non-blocking, interval=None uses previous call)
            self.cpu_usage = psutil.cpu_percent(interval=None)
            
            # Get RAM usage
            memory = psutil.virtual_memory()
            self.ram_usage = memory.percent
            
            # Update the display
            self._update_display()
        except Exception as e:
            logger.debug(f"Failed to update system stats: {e}")
    
    def _update_display(self) -> None:
        """Update the header display content."""
        try:
            static_widget = self.query_one("#header-content", Static)
            
            # Get screen title
            title = self.screen.title if (self.screen and self.screen.title) else "Terminally Simple"
            
            # Format CPU and RAM with color coding
            cpu_color = "green" if self.cpu_usage < 70 else ("yellow" if self.cpu_usage < 90 else "red")
            ram_color = "green" if self.ram_usage < 70 else ("yellow" if self.ram_usage < 90 else "red")
            
            # Build the left side (CPU and RAM)
            left_text = f"CPU: {self.cpu_usage:3.0f}%  RAM: {self.ram_usage:3.0f}%"
            left_length = len(left_text)
            
            # Build the right side (clock)
            time_str = datetime.now().strftime("%X") if self.show_clock else ""
            right_length = len(time_str)
            
            # Calculate center position for title
            title_str = str(title)
            title_length = len(title_str)
            
            # Calculate total width
            total_width = self.size.width
            
            # To center the title in the entire width, we need to position it at:
            # (total_width / 2) - (title_length / 2)
            # But we already have left_text taking up space, so:
            # padding_needed = center_position - left_length
            center_position = (total_width - title_length) // 2
            left_padding = max(1, center_position - left_length)
            
            # Right padding to fill remaining space before clock
            right_padding = max(1, total_width - left_length - left_padding - title_length - right_length)
            
            # Build the complete header text
            header_text = Text()
            
            # Left side: CPU and RAM
            header_text.append(f"CPU: {self.cpu_usage:3.0f}%", style=cpu_color)
            header_text.append("  ")
            header_text.append(f"RAM: {self.ram_usage:3.0f}%", style=ram_color)
            
            # Padding to center
            header_text.append(" " * left_padding)
            
            # Centered title
            header_text.append(title_str)
            
            # Padding before clock
            if self.show_clock:
                header_text.append(" " * right_padding)
                header_text.append(time_str)
            
            static_widget.update(header_text)
        except Exception as e:
            logger.debug(f"Failed to update display: {e}")
