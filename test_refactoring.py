#!/usr/bin/env python3
"""Quick test to verify refactoring worked"""

import sys

# Test imports
try:
    from app import TerminallySimple, MainMenu, MenuItem
    from editor import EditorScreen, FileBrowser
    from settings import SettingsScreen, SettingOption
    from config import Config
    from base_screen import NavigableScreen, NavigableMixin
    from constants import WidgetIDs
    from utils.validators import sanitize_filename
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test NavigableScreen inheritance
if not issubclass(MainMenu, NavigableScreen):
    print("✗ MainMenu doesn't inherit from NavigableScreen")
    sys.exit(1)
print("✓ MainMenu inherits from NavigableScreen")

if not issubclass(SettingsScreen, NavigableScreen):
    print("✗ SettingsScreen doesn't inherit from NavigableScreen")
    sys.exit(1)
print("✓ SettingsScreen inherits from NavigableScreen")

# Test FileBrowser has NavigableMixin
if not any(isinstance(base, type) and issubclass(base, NavigableMixin) for base in FileBrowser.__mro__):
    print("✗ FileBrowser doesn't use NavigableMixin")
    sys.exit(1)
print("✓ FileBrowser uses NavigableMixin")

# Test navigation methods exist
for cls in [MainMenu, SettingsScreen, FileBrowser]:
    if not hasattr(cls, 'get_focusable_items'):
        print(f"✗ {cls.__name__} missing get_focusable_items")
        sys.exit(1)
    if not hasattr(cls, 'action_cursor_down'):
        print(f"✗ {cls.__name__} missing action_cursor_down")
        sys.exit(1)
print("✓ All screens have navigation methods")

# Test Config
config = Config()
config.set("test_key", "test_value")
if config.get("test_key") != "test_value":
    print("✗ Config get/set failed")
    sys.exit(1)
print("✓ Config works correctly")

# Test sanitize_filename
try:
    sanitize_filename("valid_filename.md")
    print("✓ sanitize_filename accepts valid input")
except:
    print("✗ sanitize_filename rejected valid input")
    sys.exit(1)

try:
    sanitize_filename("../../etc/passwd")
    print("✗ sanitize_filename accepted path traversal")
    sys.exit(1)
except ValueError:
    print("✓ sanitize_filename rejects path traversal")

# Test WidgetIDs exist
if not hasattr(WidgetIDs, 'TEXT_AREA'):
    print("✗ WidgetIDs missing TEXT_AREA")
    sys.exit(1)
print("✓ WidgetIDs constants exist")

print("\n" + "="*50)
print("ALL TESTS PASSED ✓")
print("="*50)
