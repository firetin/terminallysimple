#!/usr/bin/env python3
"""
Test script to verify weather keyboard shortcut implementation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    try:
        from app import TerminallySimple
        from dialogs.weather_dialogs import CityInputDialog, WeatherForecastDialog
        from utils.weather import geocode_city, fetch_weather, parse_current_weather
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_binding_exists():
    """Test that the weather binding exists in the app"""
    print("\nTesting weather binding...")
    try:
        from app import TerminallySimple
        app_class = TerminallySimple
        
        # Check if BINDINGS attribute exists
        if not hasattr(app_class, 'BINDINGS'):
            print("✗ No BINDINGS attribute found")
            return False
        
        # Check if weather binding exists
        from textual.binding import Binding
        bindings = app_class.BINDINGS
        weather_binding_found = False
        for binding in bindings:
            if isinstance(binding, Binding):
                # Extract action name from binding (remove 'action_' prefix if present)
                action_name = binding.action
                if action_name == 'show_weather':
                    weather_binding_found = True
                    print(f"✓ Weather binding found: key={binding.key}, action={action_name}")
                    break
        
        if not weather_binding_found:
            print("✗ Weather binding not found in BINDINGS")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error checking bindings: {e}")
        return False

def test_action_method_exists():
    """Test that action_show_weather method exists"""
    print("\nTesting action method...")
    try:
        from app import TerminallySimple
        
        if not hasattr(TerminallySimple, 'action_show_weather'):
            print("✗ action_show_weather method not found")
            return False
        
        print("✓ action_show_weather method exists")
        return True
    except Exception as e:
        print(f"✗ Error checking action method: {e}")
        return False

def test_helper_methods_exist():
    """Test that helper methods exist"""
    print("\nTesting helper methods...")
    try:
        from app import TerminallySimple
        
        methods_to_check = [
            '_show_weather_setup',
            '_setup_weather_async',
            '_refresh_and_show_weather'
        ]
        
        all_exist = True
        for method_name in methods_to_check:
            if not hasattr(TerminallySimple, method_name):
                print(f"✗ {method_name} method not found")
                all_exist = False
            else:
                print(f"✓ {method_name} method exists")
        
        return all_exist
    except Exception as e:
        print(f"✗ Error checking helper methods: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Weather Keyboard Shortcut Implementation Test")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Weather Binding", test_binding_exists()))
    results.append(("Action Method", test_action_method_exists()))
    results.append(("Helper Methods", test_helper_methods_exist()))
    
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
        print("\n✓ All tests passed! Weather keyboard shortcut is ready.")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
