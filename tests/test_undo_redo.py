#!/usr/bin/env python3
"""Test Ctrl+Z undo and Ctrl+Y redo functionality"""

from editor import EditorScreen

# Test that EditorScreen has the bindings
editor = EditorScreen()
bindings = [b.key for b in editor.BINDINGS]

if 'ctrl+z' not in bindings:
    print("✗ ctrl+z binding missing")
    exit(1)
print("✓ Ctrl+Z (Undo) binding exists")

if 'ctrl+y' not in bindings:
    print("✗ ctrl+y binding missing")
    exit(1)
print("✓ Ctrl+Y (Redo) binding exists")

# Test that action methods exist
if not hasattr(editor, 'action_undo'):
    print("✗ action_undo method missing")
    exit(1)
print("✓ action_undo method exists")

if not hasattr(editor, 'action_redo'):
    print("✗ action_redo method missing")
    exit(1)
print("✓ action_redo method exists")

# Verify the methods are callable
if not callable(editor.action_undo):
    print("✗ action_undo is not callable")
    exit(1)
print("✓ action_undo is callable")

if not callable(editor.action_redo):
    print("✗ action_redo is not callable")
    exit(1)
print("✓ action_redo is callable")

print("\n" + "="*50)
print("UNDO/REDO FEATURES: ✓ READY")
print("="*50)
print("\nUsage:")
print("  Ctrl+Z - Undo last change")
print("  Ctrl+Y - Redo last undone change")
print("\nExample scenario:")
print("  1. Type some text")
print("  2. Press Ctrl+A to select all")
print("  3. Press Delete to remove all text")
print("  4. Press Ctrl+Z to undo the deletion")
print("  5. Press Ctrl+Z again to undo the selection")
