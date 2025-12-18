'''
Safe PyAutoGUI wrappers for Windows compatibility

Author:     Sai Vignesh Golla (with encoding fixes)
License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html

This module provides Windows-safe wrappers for PyAutoGUI alert and confirm functions.
PyAutoGUI on Windows can only handle ASCII characters in dialogs, so we strip non-ASCII
characters before displaying them to prevent encoding errors.
'''

import pyautogui
import re


def _clean_for_dialog(text):
    """
    Clean text to be safe for PyAutoGUI dialogs on Windows.
    PyAutoGUI can only handle pure ASCII, so we aggressively clean the text.
    """
    if text is None:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    try:
        # First, replace common Unicode characters with ASCII equivalents
        replacements = {
            '\u2013': '-',      # en dash
            '\u2014': '--',     # em dash
            '\u2018': "'",      # left single quotation mark
            '\u2019': "'",      # right single quotation mark
            '\u201c': '"',      # left double quotation mark
            '\u201d': '"',      # right double quotation mark
            '\u2026': '...',    # horizontal ellipsis
            '\u00a0': ' ',      # non-breaking space
            '\u00b7': '*',      # middle dot
            '\u2022': '*',      # bullet
            '\u2012': '-',      # figure dash
            '\u2015': '--',     # horizontal bar
            '\u00ae': '(R)',    # registered trademark
            '\u00a9': '(C)',    # copyright
            '\u2122': '(TM)',   # trademark
            '\u00b0': ' deg',   # degree sign
            '\u00f7': '/',      # division sign
            '\u00d7': 'x',      # multiplication sign
            '\u2020': '+',      # dagger
            '\u2021': '++',     # double dagger
            '\u2030': '%',      # per mille
            '\u2032': "'",      # prime
            '\u2033': '"',      # double prime
            '\u2039': '<',      # single left-pointing angle quotation mark
            '\u203a': '>',      # single right-pointing angle quotation mark
            '\u2044': '/',      # fraction slash
            '\u20ac': 'EUR',    # euro sign
        }
        
        for unicode_char, replacement in replacements.items():
            text = text.replace(unicode_char, replacement)
        
        # Remove any remaining non-ASCII characters (keep only printable ASCII)
        # This regex keeps: space through tilde (printable ASCII), newlines, and tabs
        text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
        
        # Force encode to ASCII, ignoring any remaining problematic characters
        text = text.encode('ascii', errors='ignore').decode('ascii')
        
        # Clean up any double spaces that may have resulted
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    except Exception as e:
        # Ultimate fallback
        return "Message contains unsupported characters"


def alert(text='', title='', button='OK'):
    """
    Safe wrapper for pyautogui.alert that handles non-ASCII characters.
    
    Parameters:
    - text: The message to display
    - title: The title of the alert dialog
    - button: The button text
    
    Returns: The button text that was clicked
    """
    try:
        safe_text = _clean_for_dialog(text)
        safe_title = _clean_for_dialog(title)
        safe_button = _clean_for_dialog(button) if button else 'OK'
        
        return pyautogui.alert(safe_text, safe_title, safe_button)
    except Exception as e:
        # Last resort fallback
        try:
            return pyautogui.alert("An error occurred. Check console for details.", "Error", "OK")
        except:
            # Even the fallback failed, just print to console
            print(f"CRITICAL: Could not display alert dialog. Original message: {text}")
            return "OK"


def confirm(text='', title='', buttons=None):
    """
    Safe wrapper for pyautogui.confirm that handles non-ASCII characters.
    
    Parameters:
    - text: The message to display
    - title: The title of the confirm dialog
    - buttons: List of button texts (e.g., ["Yes", "No", "Cancel"])
    
    Returns: The text of the button that was clicked
    """
    try:
        safe_text = _clean_for_dialog(text)
        safe_title = _clean_for_dialog(title)
        safe_buttons = buttons if buttons else ["OK"]
        
        # Clean button text as well
        if isinstance(safe_buttons, list):
            safe_buttons = [_clean_for_dialog(btn) for btn in safe_buttons]
        
        return pyautogui.confirm(safe_text, safe_title, safe_buttons)
    except Exception as e:
        # Last resort fallback
        try:
            return pyautogui.confirm("An error occurred. Check console for details.", "Error", ["OK"])
        except:
            # Even the fallback failed, just print to console
            print(f"CRITICAL: Could not display confirm dialog. Original message: {text}")
            return "OK"


# For backwards compatibility, also expose the original function names
def pyautogui_alert(*args, **kwargs):
    """Alias for alert()"""
    return alert(*args, **kwargs)


def pyautogui_confirm(*args, **kwargs):
    """Alias for confirm()"""
    return confirm(*args, **kwargs)

