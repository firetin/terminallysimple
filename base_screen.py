"""
Base classes and mixins for common screen functionality
"""

from typing import Optional, TYPE_CHECKING
from textual.screen import Screen
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import ComposeResult


class NavigableMixin:
    """Mixin providing keyboard navigation for focusable items in a screen."""
    
    focused: Optional[Widget]
    
    def get_focusable_items(self) -> list[Widget]:
        """
        Override this method to define which widgets should be navigable.
        By default, returns all focusable widgets.
        
        Returns:
            List of widgets that can receive focus via navigation
        """
        return []
    
    def action_cursor_down(self) -> None:
        """Move focus to the next item in the focusable items list."""
        focusable = self.get_focusable_items()
        if not focusable:
            return
        
        focused = self.focused
        if focused in focusable:
            current_index = focusable.index(focused)
            next_index = (current_index + 1) % len(focusable)
            focusable[next_index].focus()
        else:
            # If nothing focused, focus first item
            focusable[0].focus()
    
    def action_cursor_up(self) -> None:
        """Move focus to the previous item in the focusable items list."""
        focusable = self.get_focusable_items()
        if not focusable:
            return
        
        focused = self.focused
        if focused in focusable:
            current_index = focusable.index(focused)
            prev_index = (current_index - 1) % len(focusable)
            focusable[prev_index].focus()
        else:
            # If nothing focused, focus last item
            focusable[-1].focus()


class NavigableScreen(NavigableMixin, Screen):
    """Base screen class with navigation capabilities."""
    pass
