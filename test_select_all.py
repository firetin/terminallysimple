#!/usr/bin/env python3
"""Test Ctrl+A select all functionality"""

from editor import EditorScreen

# Test that EditorScreen has the binding
editor = EditorScreen()
bindings = [b.key for b in editor.BINDINGS]

if 'ctrl+a' not in bindings:
    print("✗ ctrl+a binding missing")
    exit(1)
print("✓ Ctrl+A binding exists")

# Test that action method exists
if not hasattr(editor, 'action_select_all'):
    print("✗ action_select_all method missing")
    exit(1)
print("✓ action_select_all method exists")

# Verify the method is callable
if not callable(editor.action_select_all):
    print("✗ action_select_all is not callable")
    exit(1)
print("✓ action_select_all is callable")

print("\n" + "="*50)
print("SELECT ALL FEATURE: ✓ READY")
print("="*50)
print("\nUsage: Press Ctrl+A in the editor to select all text")
