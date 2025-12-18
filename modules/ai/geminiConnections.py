import google.generativeai as genai
from config.secrets import llm_model, llm_api_key
from config.settings import showAiErrorAlerts
from modules.helpers import print_lg, critical_error_log, convert_to_json
from modules.ai.prompts import *
from modules.safe_pyautogui import confirm
from typing import Literal

def gemini_get_models_list():
    """
    Lists available Gemini models that support content generation.
    """
    try:
        print_lg("Getting Gemini models list...")
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print_lg("Available models:")
        for model in models:
            print_lg(f"- {model}")
        return models
    except Exception as e:
        critical_error_log("Error occurred while getting Gemini models list!", e)
        return ["error", e]

def gemini_create_client():
    """
    Configures the Gemini client and validates the selected model.
    * Returns a configured Gemini model object or None if an error occurs.
    """
    try:
        print_lg("Configuring Gemini client...")
        if not llm_api_key or "YOUR_API_KEY" in llm_api_key:
            raise ValueError("Gemini API key is not set. Please set it in `config/secrets.py`.")
        
        genai.configure(api_key=llm_api_key)
        
        models = gemini_get_models_list()
        if "error" in models:
            raise ValueError(models[1])
        if not any(llm_model in m for m in models):
             raise ValueError(f"Model `{llm_model}` is not found or not available for content generation!")

        model = genai.GenerativeModel(llm_model)
        
        print_lg("---- SUCCESSFULLY CONFIGURED GEMINI CLIENT! ----")
        print_lg(f"Using Model: {llm_model}")
        print_lg("Check './config/secrets.py' for more details.\n")
        print_lg("---------------------------------------------")
        
        return model
    except Exception as e:
        error_message = f"Error occurred while configuring Gemini client. Make sure your API key and model name are correct."
        critical_error_log(error_message, e)
        if showAiErrorAlerts:
            if "Pause AI error alerts" == confirm(f"{error_message}\n{str(e)}", "Gemini Connection Error", ["Pause AI error alerts", "Okay Continue"]):
                showAiErrorAlerts = False
        return None

def gemini_completion(model, prompt: str, is_json: bool = False) -> dict | str:
    """
    Generates content using the Gemini model.
    * Takes in `model` - The Gemini model object.
    * Takes in `prompt` of type `str` - The prompt to send to the model.
    * Takes in `is_json` of type `bool` - Whether to expect a JSON response.
    * Returns the response as a string or a dictionary.
    """
    if not model:
        raise ValueError("Gemini client is not available!")

    try:
        # The Gemini API has a 'safety_settings' parameter to control content filtering.
        # For a job application helper, it's generally safe to set these to a less restrictive level
        # to avoid blocking legitimate content from resumes or job descriptions.
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]

        print_lg(f"Calling Gemini API for completion...")
        response = model.generate_content(prompt, safety_settings=safety_settings)
        
        # The response might be blocked. Check for that.
        if not response.parts:
             raise ValueError("The response from the Gemini API was empty. This might be due to the safety filters blocking the prompt or the response. The prompt was:\n" + prompt)

        result = response.text

        if is_json:
            # Clean the response to remove Markdown formatting
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            
            return convert_to_json(result)
        
        return result
    except Exception as e:
        critical_error_log(f"Error occurred while getting Gemini completion!", e)
        return {"error": str(e)}

def gemini_extract_skills(model, job_description: str) -> list[str] | None:
    """
    Extracts skills from a job description using the Gemini model.
    * Takes in `model` - The Gemini model object.
    * Takes in `job_description` of type `str`.
    * Returns a `dict` object representing JSON response.
    """
    try:
        print_lg("Extracting skills from job description using Gemini...")
        
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
            prompt = extract_skills_prompt.format(clean_description) + "\n\nImportant: Respond with only the JSON object, without any markdown formatting or other text."
            # Double-check the prompt is clean
            prompt = clean_text_for_ai(prompt)
        except Exception as e:
            print_lg(f"Error formatting prompt: {e}")
            prompt = f"Extract skills from this job description: {clean_description}\n\nImportant: Respond with only the JSON object, without any markdown formatting or other text."
        
        return gemini_completion(model, prompt, is_json=True)
    except Exception as e:
        critical_error_log("Error occurred while extracting skills with Gemini!", e)
        return {"error": str(e)}

def gemini_answer_question(
    model,
    question: str, options: list[str] | None = None, 
    question_type: Literal['text', 'textarea', 'single_select', 'multiple_select'] = 'text', 
    job_description: str = None, about_company: str = None, user_information_all: str = None
) -> str:
    """
    Answers a question using the Gemini API.
    """
    try:
        print_lg(f"Answering question using Gemini AI: {question}")
        
        # Enhanced text cleaning function
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
        
        # Clean all inputs
        clean_question = clean_text_for_ai(question)
        clean_user_info = clean_text_for_ai(user_information_all) if user_information_all else "N/A"
        
        prompt = ai_answer_prompt.format(clean_user_info, clean_question)

        if options and (question_type in ['single_select', 'multiple_select']):
            clean_options = [clean_text_for_ai(option) for option in options]
            options_str = "OPTIONS:\n" + "\n".join([f"- {option}" for option in clean_options])
            prompt += f"\n\n{options_str}"
            if question_type == 'single_select':
                prompt += "\n\nPlease select exactly ONE option from the list above."
            else:
                prompt += "\n\nYou may select MULTIPLE options from the list above if appropriate."
        
        if job_description and job_description != "Unknown":
            clean_job_desc = clean_text_for_ai(job_description)
            prompt += f"\n\nJOB DESCRIPTION:\n{clean_job_desc}"
        
        if about_company and about_company != "Unknown":
            clean_company = clean_text_for_ai(about_company)
            prompt += f"\n\nABOUT COMPANY:\n{clean_company}"

        return gemini_completion(model, prompt)
    except Exception as e:
        critical_error_log("Error occurred while answering question with Gemini!", e)
        return {"error": str(e)}
