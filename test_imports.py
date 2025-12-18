"""
Test script to verify all imports work correctly
This helps debug ModuleNotFoundError issues
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
print("IMPORT TEST - Checking all module imports")
print("=" * 80)
print()

# Test 1: Basic path setup
print("TEST 1: Checking Python path...")
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"  Current directory: {current_dir}")
print(f"  Python path includes:")
for i, path in enumerate(sys.path[:5], 1):
    print(f"    {i}. {path}")
print()

# Test 2: Config imports
print("TEST 2: Testing config imports...")
try:
    from config.settings import *
    print("  ✓ config.settings imported successfully")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

try:
    from config.questions import *
    print("  ✓ config.questions imported successfully")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

try:
    from config.secrets import *
    print("  ✓ config.secrets imported successfully")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 3: Module imports
print("TEST 3: Testing module imports...")
try:
    from modules.helpers import print_lg, make_directories
    print("  ✓ modules.helpers imported successfully")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

try:
    from modules.safe_pyautogui import alert, confirm
    print("  ✓ modules.safe_pyautogui imported successfully")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

try:
    from modules.clickers_and_finders import *
    print("  ✓ modules.clickers_and_finders imported successfully")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 4: AI module imports (if AI is enabled)
print("TEST 4: Testing AI module imports...")
try:
    from modules.ai.openaiConnections import ai_create_openai_client, ai_generate_coverletter
    print("  ✓ modules.ai.openaiConnections imported successfully")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

try:
    from modules.ai.prompts import generate_cover_letter_prompt
    print("  ✓ modules.ai.prompts imported successfully")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 5: Direct module file imports (testing relative imports)
print("TEST 5: Testing direct module file imports...")
try:
    # This simulates what happens when a module file is run directly
    import importlib.util
    helpers_path = os.path.join(current_dir, "modules", "helpers.py")
    spec = importlib.util.spec_from_file_location("helpers", helpers_path)
    helpers_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers_module)
    print("  ✓ helpers.py can be loaded directly")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

try:
    open_chrome_path = os.path.join(current_dir, "modules", "open_chrome.py")
    spec = importlib.util.spec_from_file_location("open_chrome", open_chrome_path)
    open_chrome_module = importlib.util.module_from_spec(spec)
    # Don't execute it fully as it will try to open Chrome
    print("  ✓ open_chrome.py can be loaded (not executed)")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 6: Main script import
print("TEST 6: Testing main script structure...")
try:
    runAiBot_path = os.path.join(current_dir, "runAiBot.py")
    if os.path.exists(runAiBot_path):
        print(f"  ✓ runAiBot.py exists at: {runAiBot_path}")
        # Just check if we can read the first few lines
        with open(runAiBot_path, 'r', encoding='utf-8') as f:
            first_lines = [f.readline() for _ in range(5)]
        print("  ✓ runAiBot.py is readable")
    else:
        print(f"  ✗ runAiBot.py not found")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
print()

print("=" * 80)
print("IMPORT TEST COMPLETE")
print("=" * 80)
print()
print("If any tests failed, check:")
print("  1. You're running from the Auto_job_applier_linkedIn directory")
print("  2. All required packages are installed (pip install -r requirements.txt)")
print("  3. Python path is set correctly")
print()

