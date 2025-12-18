'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''


# Imports

import os
import json
import sys

# Add parent directory to path if needed for imports
if __name__ == '__main__' or not __package__:
    # If running as script or not as package, ensure parent directory is in path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

from time import sleep
from random import randint
from datetime import datetime, timedelta
try:
    from .safe_pyautogui import alert
except ImportError:
    # Fallback for when running as a script or if relative import fails
    from modules.safe_pyautogui import alert
from pprint import pprint

from config.settings import logs_folder_path



#### Common functions ####

#< Directories related
def make_directories(paths: list[str]) -> None:
    '''
    Function to create missing directories
    '''
    for path in paths:
        path = os.path.expanduser(path) # Expands ~ to user's home directory
        path = path.replace("//","/")
        
        # If path looks like a file path, get the directory part
        if '.' in os.path.basename(path):
            path = os.path.dirname(path)

        if not path: # Handle cases where path is empty after dirname
            continue

        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True) # exist_ok=True avoids race condition
        except Exception as e:
            print(f'Error while creating directory "{path}": ', e)


def find_default_profile_directory() -> str | None:
    '''
    Function to search for Chrome Profiles within default locations
    '''
    default_locations = [
        r"%LOCALAPPDATA%\Google\Chrome\User Data",
        r"%USERPROFILE%\AppData\Local\Google\Chrome\User Data",
        r"%USERPROFILE%\Local Settings\Application Data\Google\Chrome\User Data"
    ]
    for location in default_locations:
        profile_dir = os.path.expandvars(location)
        if os.path.exists(profile_dir):
            return profile_dir
    return None
#>


#< Logging related
def critical_error_log(possible_reason: str, stack_trace: Exception) -> None:
    '''
    Function to log and print critical errors along with datetime stamp
    '''
    try:
        # Convert exception to string safely before logging
        safe_stack_trace = str(stack_trace) if stack_trace else "No stack trace"
        print_lg(possible_reason, safe_stack_trace, datetime.now(), from_critical=True)
    except Exception as e:
        # If even critical logging fails, just print to console to avoid infinite loops
        try:
            safe_reason = str(possible_reason).encode('ascii', errors='ignore').decode('ascii')
            safe_trace = str(stack_trace).encode('ascii', errors='ignore').decode('ascii') if stack_trace else "No stack trace"
            print(f"CRITICAL ERROR - Could not log to file: {safe_reason} | {safe_trace} | {datetime.now()}")
            print(f"Logging system error: {str(e).encode('ascii', errors='ignore').decode('ascii')}")
        except:
            print("CRITICAL ERROR - Could not log error due to encoding issues")


def get_log_path():
    '''
    Function to replace '//' with '/' for logs path
    '''
    try:
        path = logs_folder_path+"/log.txt"
        return path.replace("//","/")
    except Exception as e:
        critical_error_log("Failed getting log path! So assigning default logs path: './logs/log.txt'", e)
        return "logs/log.txt"


def safe_log_cleanup():
    '''
    Function to safely clean up log file if it's too large or locked
    '''
    try:
        import os
        import shutil
        from datetime import datetime
        
        log_path = get_log_path()
        
        # Check if log file exists and is too large (> 10MB)
        if os.path.exists(log_path):
            file_size = os.path.getsize(log_path)
            max_size = 10 * 1024 * 1024  # 10MB
            
            if file_size > max_size:
                # Create backup with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{log_path}.backup_{timestamp}"
                shutil.move(log_path, backup_path)
                print(f"Log file was {file_size/1024/1024:.1f}MB, created backup: {backup_path}")
                
                # Create new empty log file
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write(f"Log file rotated at {datetime.now()}\n")
                    
    except Exception as e:
        print(f"Could not clean up log file: {e}")


def force_close_log_handles():
    '''
    Function to try to force close any open log file handles
    '''
    try:
        import gc
        import sys
        
        # Force garbage collection to close any open file handles
        gc.collect()
        
        # Try to close any open files in the current process
        for obj in gc.get_objects():
            if hasattr(obj, 'close') and hasattr(obj, 'name'):
                if hasattr(obj, 'name') and 'log.txt' in str(obj.name):
                    try:
                        obj.close()
                    except:
                        pass
                        
    except Exception as e:
        print(f"Could not force close log handles: {e}")


__logs_file_path = get_log_path()


def print_lg(*msgs: str | dict, end: str = "\n", pretty: bool = False, flush: bool = False, from_critical: bool = False) -> None:
    '''
    Function to log and print. **Note that, `end` and `flush` parameters are ignored if `pretty = True`**
    '''
    import time
    import random
    
    def safe_encode_message(msg):
        """
        Safely encode a message to handle Unicode characters
        """
        try:
            if isinstance(msg, (dict, list)):
                import json
                msg = json.dumps(msg, ensure_ascii=True, indent=2 if pretty else None)
            else:
                msg = str(msg)
            
            # Replace problematic Unicode characters
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
                '\u2020': '+',      # dagger
                '\u2021': '++',     # double dagger
                '\u2030': '%',      # per mille
                '\u2032': "'",      # prime
                '\u2033': '"',      # double prime
                '\u2039': '<',      # single left-pointing angle quotation mark
                '\u203a': '>',      # single right-pointing angle quotation mark
                '\u2044': '/',      # fraction slash
                '\u2045': '[',      # left square bracket with quill
                '\u2046': ']',      # right square bracket with quill
                '\u20ac': 'EUR',    # euro sign
                '\u2117': '(P)',    # sound recording copyright
                '\u211e': 'Rx',     # prescription take
                '\u2120': '(SM)',   # service mark
                '\u2126': 'Ohm',    # ohm sign
                '\u212a': 'K',      # kelvin sign
                '\u212b': 'A',      # angstrom sign
                '\u2132': 'F',      # turned capital F
                '\u2133': 'M',      # script capital M
                '\u2134': 'O',      # script capital O
                '\u2135': 'Alef',   # alef symbol
                '\u2136': 'Bet',    # bet symbol
                '\u2137': 'Gimel',  # gimel symbol
                '\u2138': 'Dalet',  # dalet symbol
            }
            
            for unicode_char, replacement in replacements.items():
                msg = msg.replace(unicode_char, replacement)
            
            # Ensure the message can be encoded as UTF-8
            msg = msg.encode('utf-8', errors='replace').decode('utf-8')
            return msg
        except Exception as e:
            return f"Error encoding message: {e}"
    
    for message in msgs:
        # Clean the message for safe display and logging
        safe_message = safe_encode_message(message)
        
        # Always print to console first
        try:
            pprint(safe_message) if pretty else print(safe_message, end=end, flush=flush)
        except UnicodeEncodeError:
            # Fallback for console output
            print(f"Message contains unsupported characters: {repr(safe_message)}")
        
        # Try to write to log file with retry logic
        max_retries = 3
        retry_delay = 0.1  # Start with 100ms delay
        
        for attempt in range(max_retries):
            try:
                # Try to open and write to the log file
                with open(__logs_file_path, 'a+', encoding="utf-8") as file:
                    file.write(safe_message + end)
                    file.flush()  # Ensure data is written immediately
                break  # Success, exit retry loop
                
            except (PermissionError, OSError, IOError) as e:
                if attempt < max_retries - 1:  # Not the last attempt
                    # Wait with exponential backoff and jitter
                    wait_time = retry_delay * (2 ** attempt) + random.uniform(0, 0.1)
                    time.sleep(wait_time)
                    continue
                else:
                    # Last attempt failed, handle the error
                    if from_critical:
                        # For critical errors, just skip logging to avoid infinite loops
                        print(f"CRITICAL: Could not write to log file after {max_retries} attempts: {e}")
                    else:
                        # For non-critical errors, show alert and try critical logging
                        trail = f'Skipped saving this message: "{safe_message}" to log.txt!' if from_critical else "We'll try one more time to log..."
                        alert(f"log.txt in {logs_folder_path} is open or is occupied by another program! Please close it! {trail}", "Failed Logging")
                        if not from_critical:
                            critical_error_log("Log.txt is open or is occupied by another program!", e)
            except Exception as e:
                # Handle other unexpected errors
                if from_critical:
                    print(f"CRITICAL: Unexpected error writing to log file: {e}")
                else:
                    trail = f'Skipped saving this message: "{safe_message}" to log.txt!' if from_critical else "We'll try one more time to log..."
                    alert(f"Unexpected error writing to log file: {e}\n{trail}", "Failed Logging")
                    if not from_critical:
                        critical_error_log("Unexpected error writing to log file!", e)
                break
#>


def buffer(speed: int=0) -> None:
    '''
    Function to wait within a period of selected random range.
    * Will not wait if input `speed <= 0`
    * Will wait within a random range of 
      - `0.6 to 1.0 secs` if `1 <= speed < 2`
      - `1.0 to 1.8 secs` if `2 <= speed < 3`
      - `1.8 to speed secs` if `3 <= speed`
    '''
    if speed<=0:
        return
    elif speed <= 1 and speed < 2:
        return sleep(randint(6,10)*0.1)
    elif speed <= 2 and speed < 3:
        return sleep(randint(10,18)*0.1)
    else:
        return sleep(randint(18,round(speed)*10)*0.1)
    

def manual_login_retry(is_logged_in: callable, limit: int = 2) -> None:
    '''
    Function to ask and validate manual login
    '''
    count = 0
    while not is_logged_in():
        print_lg("Seems like you're not logged in!")
        button = "Confirm Login"
        message = 'After you successfully Log In, please click "{}" button below.'.format(button)
        if count > limit:
            button = "Skip Confirmation"
            message = 'If you\'re seeing this message even after you logged in, Click "{}". Seems like auto login confirmation failed!'.format(button)
        count += 1
        if alert(message, "Login Required", button) and count > limit: return



def calculate_date_posted(time_string: str) -> datetime | None | ValueError:
    '''
    Function to calculate date posted from string.
    Returns datetime object | None if unable to calculate | ValueError if time_string is invalid
    Valid time string examples:
    * 10 seconds ago
    * 15 minutes ago
    * 2 hours ago
    * 1 hour ago
    * 1 day ago
    * 10 days ago
    * 1 week ago
    * 1 month ago
    * 1 year ago
    '''
    import re
    time_string = time_string.strip()
    now = datetime.now()

    match = re.search(r'(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago', time_string, re.IGNORECASE)

    if match:
        try:
            value = int(match.group(1))
            unit = match.group(2).lower()

            if 'second' in unit:
                return now - timedelta(seconds=value)
            elif 'minute' in unit:
                return now - timedelta(minutes=value)
            elif 'hour' in unit:
                return now - timedelta(hours=value)
            elif 'day' in unit:
                return now - timedelta(days=value)
            elif 'week' in unit:
                return now - timedelta(weeks=value)
            elif 'month' in unit:
                return now - timedelta(days=value * 30)  # Approximation
            elif 'year' in unit:
                return now - timedelta(days=value * 365)  # Approximation
        except (ValueError, IndexError):
            # Fallback for cases where parsing fails
            pass
    
    # If regex doesn't match, or parsing failed, return None.
    # This will skip jobs where the date can't be determined, preventing crashes.
    return None


def convert_to_lakhs(value: str) -> str:
    '''
    Converts str value to lakhs, no validations are done except for length and stripping.
    Examples:
    * "100000" -> "1.00"
    * "101,000" -> "10.1," Notice ',' is not removed 
    * "50" -> "0.00"
    * "5000" -> "0.05" 
    '''
    value = value.strip()
    l = len(value)
    if l > 0:
        if l > 5:
            value = value[:l-5] + "." + value[l-5:l-3]
        else:
            value = "0." + "0"*(5-l) + value[:2]
    return value


def convert_to_json(data) -> dict:
    '''
    Function to convert data to JSON, if unsuccessful, returns `{"error": "Unable to parse the response as JSON", "data": data}`
    '''
    try:
        # Clean the data to handle encoding issues
        if isinstance(data, str):
            # Replace problematic Unicode characters
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
                '\u2020': '+',      # dagger
                '\u2021': '++',     # double dagger
                '\u2030': '%',      # per mille
                '\u2032': "'",      # prime
                '\u2033': '"',      # double prime
                '\u2039': '<',      # single left-pointing angle quotation mark
                '\u203a': '>',      # single right-pointing angle quotation mark
                '\u2044': '/',      # fraction slash
                '\u2045': '[',      # left square bracket with quill
                '\u2046': ']',      # right square bracket with quill
                '\u20ac': 'EUR',    # euro sign
                '\u2117': '(P)',    # sound recording copyright
                '\u211e': 'Rx',     # prescription take
                '\u2120': '(SM)',   # service mark
                '\u2126': 'Ohm',    # ohm sign
                '\u212a': 'K',      # kelvin sign
                '\u212b': 'A',      # angstrom sign
                '\u2132': 'F',      # turned capital F
                '\u2133': 'M',      # script capital M
                '\u2134': 'O',      # script capital O
                '\u2135': 'Alef',   # alef symbol
                '\u2136': 'Bet',    # bet symbol
                '\u2137': 'Gimel',  # gimel symbol
                '\u2138': 'Dalet',  # dalet symbol
            }
            
            for unicode_char, replacement in replacements.items():
                data = data.replace(unicode_char, replacement)
            
            # Ensure the data can be encoded as UTF-8
            data = data.encode('utf-8', errors='replace').decode('utf-8')
        
        result_json = json.loads(data)
        return result_json
    except json.JSONDecodeError as e:
        return {"error": "Unable to parse the response as JSON", "data": str(data), "json_error": str(e)}
    except Exception as e:
        return {"error": "Unexpected error converting to JSON", "data": str(data), "error": str(e)}


def truncate_for_csv(data, max_length: int = 131000, suffix: str = "...[TRUNCATED]") -> str:
    '''
    Function to truncate data for CSV writing to avoid field size limit errors.
    * Takes in `data` of any type and converts to string
    * Takes in `max_length` of type `int` - maximum allowed length (default: 131000, leaving room for suffix)
    * Takes in `suffix` of type `str` - text to append when truncated
    * Returns truncated string if data exceeds max_length
    '''
    try:
        # Convert data to string
        str_data = str(data) if data is not None else ""
        
        # If within limit, return as-is
        if len(str_data) <= max_length:
            return str_data
        
        # Truncate and add suffix
        truncated = str_data[:max_length - len(suffix)] + suffix
        return truncated
    except Exception as e:
        return f"[ERROR CONVERTING DATA: {e}]"