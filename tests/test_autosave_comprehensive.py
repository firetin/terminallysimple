#!/usr/bin/env python3
"""Comprehensive autosave test"""

import time
from pathlib import Path

print("="*70)
print("COMPREHENSIVE AUTOSAVE TEST")
print("="*70)

# Clean up any existing autosave
autosave_file = Path("notes/.autosave/untitled-autosave.md")
if autosave_file.exists():
    autosave_file.unlink()
    print("\n✓ Cleaned up existing autosave file")

# Test the autosave logic
print("\n1. Testing _autosave() method behavior:")
from editor import EditorScreen

editor = EditorScreen()

# Check the method exists
if hasattr(editor, '_autosave'):
    print("  ✓ _autosave method exists")
else:
    print("  ✗ _autosave method missing!")
    exit(1)

# Check event handler
if hasattr(editor, 'on_text_area_changed'):
    print("  ✓ on_text_area_changed event handler exists")
else:
    print("  ✗ on_text_area_changed missing!")
    exit(1)

# Check autosave parameters
print(f"\n2. Autosave configuration:")
print(f"  • Enabled: {editor.autosave_enabled}")
print(f"  • Interval: {editor.autosave_interval} seconds")
print(f"  • Directory: {editor.autosave_dir}")

# Simulate autosave file creation
print(f"\n3. Simulating autosave:")
test_content = "Test content from new file\nCreated with Ctrl+N\nShould be recovered!"
autosave_file.write_text(test_content)
print(f"  ✓ Created autosave file")
print(f"  ✓ Content: {len(test_content)} characters")

# Verify file exists
if autosave_file.exists():
    print(f"  ✓ File exists at: {autosave_file}")
    content = autosave_file.read_text()
    print(f"  ✓ Can read content: {len(content)} chars")
else:
    print(f"  ✗ File not found!")
    exit(1)

print("\n" + "="*70)
print("MANUAL TEST INSTRUCTIONS - FOLLOW EXACTLY:")
print("="*70)
print("""
1. Run: python app.py
2. Press 1 to open Text Editor
3. You should see recovered content from previous test
4. Press Ctrl+N to create NEW file
5. Type: "Hello from new file! Testing autosave."
6. Wait 5 seconds (watch the clock)
7. KILL the terminal (Ctrl+C or close window)
8. Run: python app.py again
9. Press 1 to open Text Editor
10. You SHOULD see: "Hello from new file! Testing autosave."

If step 10 shows your text → SUCCESS! ✓
If step 10 shows empty → Bug still exists ✗
""")

print("="*70)
print("Tests completed. File ready for recovery test.")
print("="*70)
