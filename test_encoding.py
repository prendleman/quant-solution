"""
Test script to validate all encoding fixes for Windows compatibility
This script tests that all error handling paths properly handle non-ASCII characters
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 >nul 2>&1')
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Test strings with various problematic characters
test_strings = [
    "Normal ASCII text",
    "Text with smart quotes: 'single' and \"double\"",
    "Text with em dash — and en dash –",
    "Text with bullets • and ellipsis …",
    "Text with copyright © and trademark ™",
    "Text with non-breaking spaces and special chars",
    "Mixed: 'quotes' — dashes • bullets … ellipsis",
    "Error: 'ascii' codec can't encode characters in position 7-8",
    "Unicode test: 你好世界 🌍 ñoño café résumé",
]

print("=" * 80)
print("ENCODING FIX VALIDATION TEST")
print("=" * 80)
print()

# Test 1: Safe PyAutoGUI wrapper
print("TEST 1: Testing safe_pyautogui module...")
try:
    from modules.safe_pyautogui import alert, confirm
    
    print("✓ safe_pyautogui module imported successfully")
    
    # Test the cleaning function
    for test_str in test_strings:
        try:
            # This should not crash
            cleaned = alert(test_str, "Test", "OK")
            print(f"  ✓ Handled: {test_str[:50]}...")
        except Exception as e:
            print(f"  ✗ FAILED on: {test_str[:50]}... Error: {e}")
            break
    else:
        print("  ✓ All test strings handled successfully")
except Exception as e:
    print(f"  ✗ FAILED: Could not import or test safe_pyautogui: {e}")
    sys.exit(1)

print()

# Test 2: AI error alert function
print("TEST 2: Testing AI error alert function...")
try:
    from modules.ai.openaiConnections import ai_error_alert, _safe_str
    
    print("✓ AI error alert functions imported successfully")
    
    # Test _safe_str function
    test_exceptions = [
        Exception("Normal error"),
        Exception("Error with 'quotes'"),
        Exception("Error with — dash"),
        Exception("Error with • bullet"),
        ValueError("Error: 'ascii' codec can't encode"),
    ]
    
    for exc in test_exceptions:
        try:
            safe = _safe_str(exc)
            print(f"  ✓ Cleaned exception: {type(exc).__name__} -> {safe[:50]}...")
        except Exception as e:
            print(f"  ✗ FAILED on exception: {e}")
            break
    else:
        print("  ✓ All exceptions cleaned successfully")
        
    # Test ai_error_alert (but don't actually show dialog)
    print("  ✓ ai_error_alert function available")
    
except Exception as e:
    print(f"  ✗ FAILED: Could not test AI error functions: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Critical error log
print("TEST 3: Testing critical_error_log function...")
try:
    from modules.helpers import critical_error_log
    
    print("✓ critical_error_log function imported successfully")
    
    # Test with various exceptions
    test_exceptions = [
        Exception("Normal error"),
        Exception("Error with special chars: 'quotes' — dash"),
    ]
    
    for exc in test_exceptions:
        try:
            # This should not crash
            critical_error_log("Test error", exc)
            print(f"  ✓ Logged exception: {type(exc).__name__}")
        except Exception as e:
            print(f"  ✗ FAILED on exception: {e}")
            break
    else:
        print("  ✓ All exceptions logged successfully")
        
except Exception as e:
    print(f"  ✗ FAILED: Could not test critical_error_log: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Print_lg function
print("TEST 4: Testing print_lg function...")
try:
    from modules.helpers import print_lg
    
    print("✓ print_lg function imported successfully")
    
    # Test with various strings
    for test_str in test_strings[:5]:  # Test first 5 to avoid too much output
        try:
            print_lg(f"Test: {test_str}")
            print(f"  ✓ Logged: {test_str[:50]}...")
        except Exception as e:
            print(f"  ✗ FAILED on: {test_str[:50]}... Error: {e}")
            break
    else:
        print("  ✓ All strings logged successfully")
        
except Exception as e:
    print(f"  ✗ FAILED: Could not test print_lg: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 5: Console encoding
print("TEST 5: Testing console encoding...")
try:
    # Test that we can print Unicode
    test_unicode = "Test: ñoño café résumé 你好"
    print(f"  Testing Unicode output: {test_unicode}")
    print(f"  ✓ Console encoding working")
except Exception as e:
    print(f"  ✗ FAILED: Console encoding issue: {e}")

print()

# Test 6: Exception handling in try/except blocks
print("TEST 6: Testing exception handling with non-ASCII...")
try:
    # Simulate what happens in ai_extract_skills
    def test_exception_handling():
        try:
            # Simulate an error with non-ASCII
            raise ValueError("Error: 'ascii' codec can't encode characters in position 7-8: ordinal not in range(128)")
        except Exception as e:
            # This is what our code does now
            from modules.ai.openaiConnections import _safe_str
            safe_e = _safe_str(e)
            return safe_e
    
    result = test_exception_handling()
    print(f"  ✓ Exception handled: {result[:80]}...")
    if "'ascii' codec" in result or "can't encode" in result:
        print("  ✓ Error message preserved (ASCII-safe)")
    
except Exception as e:
    print(f"  ✗ FAILED: Exception handling test: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("All critical encoding paths have been tested.")
print("If all tests passed, the bot should handle encoding errors correctly.")
print("=" * 80)










