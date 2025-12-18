'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''


from config.secrets import *
from config.settings import showAiErrorAlerts
from config.personals import ethnicity, gender, disability_status, veteran_status
from config.questions import *
from config.search import security_clearance, did_masters

from modules.helpers import print_lg, critical_error_log, convert_to_json
from modules.ai.prompts import *
from modules.safe_pyautogui import confirm
from openai import OpenAI
from openai.types.model import Model
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from typing import Iterator, Literal


apiCheckInstructions = """

1. Make sure your AI API connection details like url, key, model names, etc are correct.
2. If you're using an local LLM, please check if the server is running.
3. Check if appropriate LLM and Embedding models are loaded and running.

Open secret.py in /config folder to configure your AI API connections.

ERROR:
"""

# Helper function to safely convert objects to ASCII strings
def _safe_str(obj):
    """Safely convert object to string, handling encoding issues"""
    try:
        s = str(obj)
        # Remove non-ASCII immediately to prevent f-string formatting errors
        return s.encode('ascii', errors='ignore').decode('ascii')
    except:
        return "Error converting to string"


# Helper function to categorize errors and determine if dialog should be shown
def _should_show_error_dialog(error_str: str) -> tuple[bool, str]:
    """
    Intelligently determines if an error dialog should be shown.
    Returns: (should_show: bool, simplified_message: str)
    """
    error_lower = error_str.lower()
    
    # Known expected errors that should NOT show dialogs (just log silently)
    silent_errors = [
        'invalid_api_key',
        'incorrect api key',
        'api key',
        '401',
        'authentication',
        'unauthorized',
        'invalid_request_error',
        'rate limit',
        '429',
        'quota',
        'insufficient_quota',
        'model not found',
        'model_not_found',
        '404',
    ]
    
    # Check if this is a known error we should handle silently
    for silent_error in silent_errors:
        if silent_error in error_lower:
            # Still log it, but don't show dialog
            simplified = "API configuration issue detected. Check your API key and settings in config/secrets.py"
            if 'rate limit' in error_lower or '429' in error_lower or 'quota' in error_lower:
                simplified = "API rate limit or quota exceeded. Please wait and try again later."
            elif 'model' in error_lower and 'not found' in error_lower:
                simplified = "AI model not found. Check your model name in config/secrets.py"
            return False, simplified
    
    # Unknown/unexpected errors - show dialog
    return True, error_str


# Function to show an AI error alert with intelligent error handling
def ai_error_alert(message: str, stackTrace: str, title: str = "AI Connection Error") -> None:
    """
    Function to show an AI error alert and log it.
    Intelligently suppresses known errors (like invalid API keys) and only shows dialogs for unexpected errors.
    Note: The confirm dialog is now automatically safe for non-ASCII characters via safe_pyautogui wrapper
    """
    global showAiErrorAlerts
    
    try:
        # Clean the stackTrace BEFORE formatting to prevent encoding errors during f-string creation
        safe_message = _safe_str(message)
        safe_stack_trace = _safe_str(stackTrace)
        
        # Combine message and stack trace for error analysis
        full_error = f"{safe_message} {safe_stack_trace}"
        
        # Check if we should show dialog or just log silently
        should_show, simplified_message = _should_show_error_dialog(full_error)
        
        # Always log the error (for debugging)
        if should_show:
            # Full error for unexpected issues
            critical_error_log(safe_message, safe_stack_trace)
        else:
            # Simplified error for known issues
            print_lg(f"AI Error (silent): {simplified_message}")
            critical_error_log(f"AI Error (known issue): {simplified_message}", safe_stack_trace)
        
        # Only show dialog for unexpected errors and if alerts are enabled
        if should_show and showAiErrorAlerts:
            # Safe wrapper handles dialog, but we need safe strings for f-string formatting
            dialog_text = f"{safe_message}\n{safe_stack_trace}\n"
            if "Pause AI error alerts" == confirm(dialog_text, title, ["Pause AI error alerts", "Okay Continue"]):
                showAiErrorAlerts = False
        elif not should_show:
            # For known errors, just print a helpful message
            print_lg(f"Note: {simplified_message}")
            print_lg("The bot will continue without AI features. Fix the issue in config/secrets.py to enable AI.")
            
    except Exception as e:
        # Fallback: just print to console if everything fails
        try:
            print(f"AI Error Alert failed: {_safe_str(message)} | {_safe_str(stackTrace)} | Alert Error: {_safe_str(e)}")
        except:
            print("AI Error Alert failed: Unable to display error message due to encoding issues")


# Function to check if an error occurred
def ai_check_error(response: ChatCompletion | ChatCompletionChunk) -> None:
    """
    Function to check if an error occurred.
    * Takes in `response` of type `ChatCompletion` or `ChatCompletionChunk`
    * Raises a `ValueError` if an error is found
    """
    if response.model_extra.get("error"):
        raise ValueError(
            f'Error occurred with API: "{response.model_extra.get("error")}"'
        )


# Function to create an OpenAI client
def ai_create_openai_client() -> OpenAI:
    """
    Function to create an OpenAI client.
    * Takes no arguments
    * Returns an `OpenAI` object
    """
    try:
        print_lg("Creating OpenAI client...")
        if not use_AI:
            raise ValueError("AI is not enabled! Please enable it by setting `use_AI = True` in `secrets.py` in `config` folder.")
        
        client = OpenAI(base_url=llm_api_url, api_key=llm_api_key)

        # Best-effort model validation. Some environments raise encoding errors or
        # deny listing models; don't block startup on this.
        try:
            models = ai_get_models_list(client)
            if isinstance(models, list) and models and models[0] != "error":
                available_ids = [getattr(m, "id", None) for m in models]
                if llm_model not in available_ids:
                    print_lg(f"Model `{llm_model}` not found in listed models; continuing to let the API validate at runtime.")
        except Exception:
            print_lg("Skipping model listing due to an error; proceeding with runtime validation.")
        
        print_lg("---- SUCCESSFULLY CREATED OPENAI CLIENT! ----")
        print_lg(f"Using API URL: {llm_api_url}")
        print_lg(f"Using Model: {llm_model}")
        print_lg("Check './config/secrets.py' for more details.\n")
        print_lg("---------------------------------------------")

        return client
    except Exception as e:
        # Clean the exception before passing to error handler
        safe_e = _safe_str(e)
        ai_error_alert(f"Error occurred while creating OpenAI client. {apiCheckInstructions}", safe_e)


# Function to close an OpenAI client
def ai_close_openai_client(client: OpenAI) -> None:
    """
    Function to close an OpenAI client.
    * Takes in `client` of type `OpenAI`
    * Returns no value
    """
    try:
        if client:
            print_lg("Closing OpenAI client...")
            client.close()
    except Exception as e:
        # Clean the exception before passing to error handler
        safe_e = _safe_str(e)
        ai_error_alert("Error occurred while closing OpenAI client.", safe_e)



# Function to get list of models available in OpenAI API
def ai_get_models_list(client: OpenAI) -> list[ Model | str]:
    """
    Function to get list of models available in OpenAI API.
    * Takes in `client` of type `OpenAI`
    * Returns a `list` object
    """
    try:
        print_lg("Getting AI models list...")
        if not client: raise ValueError("Client is not available!")
        models = client.models.list()
        ai_check_error(models)
        print_lg("Available models fetched.")
        # Avoid printing full objects to prevent Windows console encoding issues
        try:
            ids = [getattr(m, "id", str(m)) for m in models.data]
            print_lg(ids, pretty=True)
        except Exception:
            print_lg("Skipped printing model details due to encoding issues.")
        return models.data
    except Exception as e:
        critical_error_log("Error occurred while getting models list!", e)
        return ["error", e]

def model_supports_temperature(model_name: str) -> bool:
    """
    Checks if the specified model supports the temperature parameter.
    
    Args:
        model_name (str): The name of the AI model.
    
    Returns:
        bool: True if the model supports temperature adjustments, otherwise False.
    """
    return model_name in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini"]

# Function to get chat completion from OpenAI API
def ai_completion(client: OpenAI, messages: list[dict], response_format: dict = None, temperature: float = 0, stream: bool = stream_output) -> dict | ValueError:
    """
    Function that completes a chat and prints and formats the results of the OpenAI API calls.
    * Takes in `client` of type `OpenAI`
    * Takes in `messages` of type `list[dict]`. Example: `[{"role": "user", "content": "Hello"}]`
    * Takes in `response_format` of type `dict` for JSON representation, default is `None`
    * Takes in `temperature` of type `float` for temperature, default is `0`
    * Takes in `stream` of type `bool` to indicate if it's a streaming call or not
    * Returns a `dict` object representing JSON response, will try to convert to JSON if `response_format` is given
    """
    if not client: raise ValueError("Client is not available!")

    params = {"model": llm_model, "messages": messages, "stream": stream}

    if model_supports_temperature(llm_model):
        params["temperature"] = temperature
    if response_format and llm_spec in ["openai", "openai-like"]:
        params["response_format"] = response_format

    completion = client.chat.completions.create(**params)

    result = ""
    
    # Log response
    if stream:
        print_lg("--STREAMING STARTED")
        for chunk in completion:
            ai_check_error(chunk)
            chunkMessage = chunk.choices[0].delta.content
            if chunkMessage != None:
                result += chunkMessage
            print_lg(chunkMessage, end="", flush=True)
        print_lg("\n--STREAMING COMPLETE")
    else:
        ai_check_error(completion)
        result = completion.choices[0].message.content
    
    if response_format:
        result = convert_to_json(result)
    
    print_lg("\nAI Answer to Question:\n")
    print_lg(result, pretty=response_format)
    return result


def ai_extract_skills(client: OpenAI, job_description: str, stream: bool = stream_output) -> dict | ValueError:
    """
    Function to extract skills from job description using OpenAI API.
    * Takes in `client` of type `OpenAI`
    * Takes in `job_description` of type `str`
    * Takes in `stream` of type `bool` to indicate if it's a streaming call
    * Returns a `dict` object representing JSON response
    """
    print_lg("-- EXTRACTING SKILLS FROM JOB DESCRIPTION")
    try:        
        # Enhanced text cleaning to handle encoding issues
        def clean_text_for_ai(text):
            """
            Clean text to handle various encoding issues and special characters
            """
            if not text or not isinstance(text, str):
                return "No job description available"
            
            try:
                # First, normalize Unicode characters
                import unicodedata
                text = unicodedata.normalize('NFKD', text)
                
                # Replace common problematic Unicode characters
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
                    text = text.replace(unicode_char, replacement)
                
                # Remove any remaining non-printable characters except newlines and tabs
                import re
                text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
                
                # Ensure the text is properly encoded as UTF-8
                text = text.encode('utf-8', errors='ignore').decode('utf-8')
                
                # Remove excessive whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                return text
                
            except Exception as e:
                print_lg(f"Error in text cleaning: {e}")
                # Fallback: basic UTF-8 conversion
                try:
                    return text.encode('utf-8', errors='replace').decode('utf-8')
                except:
                    return "Job description contains unsupported characters"
        
        clean_description = clean_text_for_ai(job_description)
        
        # Ensure the prompt is also properly encoded
        try:
            prompt = extract_skills_prompt.format(clean_description)
            # Double-check the prompt is clean
            prompt = clean_text_for_ai(prompt)
        except Exception as e:
            print_lg(f"Error formatting prompt: {e}")
            prompt = f"Extract skills from this job description: {clean_description}"
        
        messages = [{"role": "user", "content": prompt}]
        
        ##> ------ Dheeraj Deshwal : dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Bug fix ------
        return ai_completion(client, messages, response_format=extract_skills_response_format, stream=stream)
    ##<
    except Exception as e:
        # Clean the exception before passing to error handler
        safe_e = _safe_str(e)
        ai_error_alert(f"Error occurred while extracting skills from job description. {apiCheckInstructions}", safe_e)
        # Return a safe default value instead of crashing
        return {"error": "Failed to extract skills", "skills": []}


##> ------ Dheeraj Deshwal : dheeraj9811 Email:dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Feature ------
def ai_answer_question(
    client: OpenAI, 
    question: str, options: list[str] | None = None, question_type: Literal['text', 'textarea', 'single_select', 'multiple_select'] = 'text', 
    job_description: str = None, about_company: str = None, user_information_all: str = None,
    stream: bool = stream_output
) -> dict | ValueError:
    """
    Function to generate AI-based answers for questions in a form.
    
    Parameters:
    - `client`: OpenAI client instance.
    - `question`: The question being answered.
    - `options`: List of options (for `single_select` or `multiple_select` questions).
    - `question_type`: Type of question (text, textarea, single_select, multiple_select) It is restricted to one of four possible values.
    - `job_description`: Optional job description for context.
    - `about_company`: Optional company details for context.
    - `user_information_all`: information about you, AI cna use to answer question eg: Resume-like user information.
    - `stream`: Whether to use streaming AI completion.
    
    Returns:
    - `str`: The AI-generated answer.
    """

    print_lg("-- ANSWERING QUESTION using AI")
    try:
        # Enhanced text cleaning function (same as in ai_extract_skills)
        def clean_text_for_ai(text):
            """
            Clean text to handle various encoding issues and special characters
            """
            if not text or not isinstance(text, str) or text == "Unknown":
                return text if text != "Unknown" else "N/A"
            
            try:
                # First, normalize Unicode characters
                import unicodedata
                text = unicodedata.normalize('NFKD', text)
                
                # Replace common problematic Unicode characters
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
                    text = text.replace(unicode_char, replacement)
                
                # Remove any remaining non-printable characters except newlines and tabs
                import re
                text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
                
                # Ensure the text is properly encoded as UTF-8
                text = text.encode('utf-8', errors='ignore').decode('utf-8')
                
                # Remove excessive whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                return text
                
            except Exception as e:
                print_lg(f"Error in text cleaning: {e}")
                # Fallback: basic UTF-8 conversion
                try:
                    return text.encode('utf-8', errors='replace').decode('utf-8')
                except:
                    return "Text contains unsupported characters"
        
        clean_question = clean_text_for_ai(question)
        clean_user_info = clean_text_for_ai(user_information_all) if user_information_all else "N/A"
        
        prompt = ai_answer_prompt.format(clean_user_info, clean_question)
         # Append optional details if provided
        if job_description and job_description != "Unknown":
            clean_job_desc = clean_text_for_ai(job_description)
            prompt += f"\nJob Description:\n{clean_job_desc}"
        if about_company and about_company != "Unknown":
            clean_company = clean_text_for_ai(about_company)
            prompt += f"\nAbout the Company:\n{clean_company}"

        messages = [{"role": "user", "content": prompt}]
        print_lg("Prompt we are passing to AI: ", prompt)
        response =  ai_completion(client, messages, stream=stream)
        # print_lg("Response from AI: ", response)
        return response
    except Exception as e:
        # Clean the exception before passing to error handler
        safe_e = _safe_str(e)
        ai_error_alert(f"Error occurred while answering question. {apiCheckInstructions}", safe_e)
        # Return a safe default value instead of crashing
        return ""
##<


def ai_gen_experience(
    client: OpenAI, 
    job_description: str, about_company: str, 
    required_skills: dict, user_experience: dict,
    stream: bool = stream_output
) -> dict | ValueError:
    pass



def ai_generate_resume(
    client: OpenAI, 
    job_description: str, about_company: str, required_skills: dict,
    stream: bool = stream_output
) -> dict | ValueError:
    '''
    Function to generate resume. Takes in user experience and template info from config.
    '''
    pass



def ai_generate_coverletter(
    client: OpenAI, 
    job_description: str, about_company: str, required_skills: dict,
    user_information_all: str = None,
    stream: bool = stream_output
) -> str | ValueError:
    '''
    Function to generate a personalized cover letter based on job description, company info, and user information.
    * Takes in `client` of type `OpenAI`
    * Takes in `job_description` of type `str`
    * Takes in `about_company` of type `str`
    * Takes in `required_skills` of type `dict` (from ai_extract_skills)
    * Takes in `user_information_all` of type `str` (optional user background/resume info)
    * Takes in `stream` of type `bool` to indicate if it's a streaming call
    * Returns a `str` object representing the generated cover letter
    '''
    print_lg("-- GENERATING COVER LETTER using AI")
    try:
        # Enhanced text cleaning function (same as in ai_extract_skills)
        def clean_text_for_ai(text):
            """
            Clean text to handle various encoding issues and special characters
            """
            if not text or not isinstance(text, str) or text == "Unknown":
                return text if text != "Unknown" else "N/A"
            
            try:
                # First, normalize Unicode characters
                import unicodedata
                text = unicodedata.normalize('NFKD', text)
                
                # Replace common problematic Unicode characters
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
                }
                
                for unicode_char, replacement in replacements.items():
                    text = text.replace(unicode_char, replacement)
                
                # Remove any remaining non-printable characters except newlines and tabs
                import re
                text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
                
                # Ensure the text is properly encoded as UTF-8
                text = text.encode('utf-8', errors='ignore').decode('utf-8')
                
                # Remove excessive whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                return text
                
            except Exception as e:
                print_lg(f"Error in text cleaning: {e}")
                # Fallback: basic UTF-8 conversion
                try:
                    return text.encode('utf-8', errors='replace').decode('utf-8')
                except:
                    return "Text contains unsupported characters"
        
        # Clean all inputs
        clean_job_desc = clean_text_for_ai(job_description) if job_description and job_description != "Unknown" else "N/A"
        clean_company = clean_text_for_ai(about_company) if about_company and about_company != "Unknown" else "N/A"
        clean_user_info = clean_text_for_ai(user_information_all) if user_information_all else "N/A"
        
        # Format skills from the required_skills dict
        required_skills_list = []
        nice_to_have_list = []
        
        if isinstance(required_skills, dict):
            # Extract required skills
            if "required_skills" in required_skills and isinstance(required_skills["required_skills"], list):
                required_skills_list = required_skills["required_skills"]
            elif "tech_stack" in required_skills and isinstance(required_skills["tech_stack"], list):
                required_skills_list.extend(required_skills["tech_stack"])
            if "technical_skills" in required_skills and isinstance(required_skills["technical_skills"], list):
                required_skills_list.extend(required_skills["technical_skills"])
            
            # Extract nice-to-have skills
            if "nice_to_have" in required_skills and isinstance(required_skills["nice_to_have"], list):
                nice_to_have_list = required_skills["nice_to_have"]
        
        required_skills_str = ", ".join(required_skills_list) if required_skills_list else "N/A"
        nice_to_have_str = ", ".join(nice_to_have_list) if nice_to_have_list else "N/A"
        
        # Format the prompt
        prompt = generate_cover_letter_prompt.format(
            clean_user_info,
            clean_job_desc,
            clean_company,
            required_skills_str,
            nice_to_have_str
        )
        
        messages = [{"role": "user", "content": prompt}]
        
        # Generate cover letter (no JSON format needed, just plain text)
        generated_cover_letter = ai_completion(client, messages, response_format=None, temperature=0.7, stream=stream)
        
        # Ensure we return a string
        if isinstance(generated_cover_letter, str):
            return generated_cover_letter
        elif isinstance(generated_cover_letter, dict) and "content" in generated_cover_letter:
            return generated_cover_letter["content"]
        else:
            return str(generated_cover_letter)
            
    except Exception as e:
        # Clean the exception before passing to error handler
        safe_e = _safe_str(e)
        ai_error_alert(f"Error occurred while generating cover letter. {apiCheckInstructions}", safe_e)
        # Return a safe default value instead of crashing - use static cover_letter from config if available
        return cover_letter if cover_letter else "I am excited to apply for this position and believe my skills and experience make me a strong candidate."



##< Evaluation Agents
def ai_evaluate_resume(
    client: OpenAI, 
    job_description: str, about_company: str, required_skills: dict,
    resume: str,
    stream: bool = stream_output
) -> dict | ValueError:
    pass



def ai_evaluate_resume(
    client: OpenAI, 
    job_description: str, about_company: str, required_skills: dict,
    resume: str,
    stream: bool = stream_output
) -> dict | ValueError:
    pass



def ai_check_job_relevance(
    client: OpenAI, 
    job_description: str, about_company: str,
    stream: bool = stream_output
) -> dict:
    pass
#>