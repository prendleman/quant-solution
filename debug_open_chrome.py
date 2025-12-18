"""
Debug script to test open_chrome.py imports and basic functionality
This simulates running open_chrome.py directly
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

print("=" * 80)
print("DEBUG: Testing open_chrome.py imports")
print("=" * 80)
print()

# Simulate running from modules directory
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(current_dir, "modules")
open_chrome_path = os.path.join(modules_dir, "open_chrome.py")

print(f"Current directory: {current_dir}")
print(f"Modules directory: {modules_dir}")
print(f"open_chrome.py path: {open_chrome_path}")
print()

# Test 1: Check if path handling works
print("TEST 1: Testing path handling in open_chrome.py...")
try:
    # Read the file and check if path handling is present
    with open(open_chrome_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'sys.path.insert' in content:
            print("  ✓ Path handling code is present")
        else:
            print("  ✗ Path handling code is missing")
except Exception as e:
    print(f"  ✗ FAILED to read file: {e}")
print()

# Test 2: Try importing as if running from modules directory
print("TEST 2: Testing import when run from modules directory...")
original_cwd = os.getcwd()
try:
    # Change to modules directory to simulate running the script directly
    os.chdir(modules_dir)
    print(f"  Changed to: {os.getcwd()}")
    
    # Add parent to path (what the script should do)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Now try to import
    import importlib.util
    spec = importlib.util.spec_from_file_location("open_chrome", open_chrome_path)
    open_chrome_module = importlib.util.module_from_spec(spec)
    
    # Try to execute just the imports (not the driver creation)
    print("  Attempting to load module...")
    # We'll catch any import errors
    try:
        spec.loader.exec_module(open_chrome_module)
        print("  ✓ Module loaded successfully (imports worked)")
    except Exception as e:
        print(f"  ✗ FAILED during module load: {e}")
        import traceback
        traceback.print_exc()
        
finally:
    os.chdir(original_cwd)
    print(f"  Restored to: {os.getcwd()}")
print()

# Test 3: Test individual imports that open_chrome.py needs
print("TEST 3: Testing individual imports...")
try:
    from modules.helpers import make_directories, print_lg, find_default_profile_directory, critical_error_log
    print("  ✓ modules.helpers imported")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

try:
    from config.settings import run_in_background, stealth_mode, disable_extensions, safe_mode
    print("  ✓ config.settings imported")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

try:
    from config.questions import default_resume_path
    print("  ✓ config.questions imported")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

try:
    from modules.safe_pyautogui import alert
    print("  ✓ modules.safe_pyautogui imported")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
print()

print("=" * 80)
print("DEBUG COMPLETE")
print("=" * 80)
print()
print("Note: This test does NOT actually open Chrome.")
print("It only tests that the imports work correctly.")
print()

