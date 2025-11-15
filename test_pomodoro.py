#!/usr/bin/env python3
"""Test Pomodoro implementation"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_pomodoro_imports():
    """Test Pomodoro-related imports"""
    print("Testing Pomodoro imports...")
    try:
        from dialogs.pomodoro_dialogs import PomodoroDialog
        from widgets.system_header import PomodoroWidget, SystemHeader
        from app import TerminallySimple
        print("✓ All Pomodoro imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_pomodoro_bindings():
    """Test Pomodoro bindings exist"""
    print("\nTesting Pomodoro bindings...")
    try:
        from app import TerminallySimple, MainMenu
        from textual.binding import Binding
        
        # Check app bindings
        app_has_pomodoro = False
        for binding in TerminallySimple.BINDINGS:
            if isinstance(binding, Binding) and binding.action == 'show_pomodoro':
                app_has_pomodoro = True
                print(f"✓ App Pomodoro binding found: key='{binding.key}'")
        
        # Check main menu bindings
        menu_has_pomodoro = False
        for binding in MainMenu.BINDINGS:
            if isinstance(binding, Binding) and 'pomodoro' in binding.action.lower():
                menu_has_pomodoro = True
                print(f"✓ Main menu Pomodoro binding found: key='{binding.key}'")
        
        return app_has_pomodoro and menu_has_pomodoro
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_pomodoro_widget():
    """Test PomodoroWidget functionality"""
    print("\nTesting PomodoroWidget...")
    try:
        from widgets.system_header import PomodoroWidget
        
        widget = PomodoroWidget()
        
        # Test initial state
        assert widget.time_remaining == 25 * 60, "Initial time should be 25 minutes"
        assert not widget.is_active, "Should not be active initially"
        assert not widget.is_paused_state, "Should not be paused initially"
        
        # Test rendering
        render_output = widget.render()
        assert render_output is not None, "Should render output"
        
        print("✓ PomodoroWidget works correctly")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_header_pomodoro():
    """Test SystemHeader has Pomodoro support"""
    print("\nTesting SystemHeader Pomodoro support...")
    try:
        from widgets.system_header import SystemHeader
        
        # Check if SystemHeader has Pomodoro methods
        methods = [
            '_handle_pomodoro_click',
            '_show_pomodoro_dialog',
            '_start_pomodoro',
            '_pause_pomodoro',
            '_reset_pomodoro',
            '_tick_pomodoro',
            '_pomodoro_complete'
        ]
        
        for method in methods:
            if not hasattr(SystemHeader, method):
                print(f"✗ Method {method} not found")
                return False
            print(f"✓ {method} exists")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Pomodoro Timer Implementation Test")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_pomodoro_imports()))
    results.append(("Bindings", test_pomodoro_bindings()))
    results.append(("PomodoroWidget", test_pomodoro_widget()))
    results.append(("SystemHeader", test_system_header_pomodoro()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20s}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! Pomodoro timer is ready.")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
