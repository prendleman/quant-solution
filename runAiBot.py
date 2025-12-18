'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''


# Fix Windows console encoding issues
import sys
import os

# Set UTF-8 encoding for stdout and stderr on Windows
if sys.platform == 'win32':
    try:
        # Try to set the console code page to UTF-8
        os.system('chcp 65001 >nul 2>&1')
    except:
        pass
    
    # Reconfigure stdout and stderr to use UTF-8
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        # Python < 3.7 fallback
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

# Imports
import csv
import re
import pyautogui
from modules.safe_pyautogui import alert as safe_alert, confirm as safe_confirm

# Set CSV field size limit to prevent field size errors
csv.field_size_limit(10000000)  # Set to 10MB instead of default 131KB to handle large job descriptions

from random import choice, shuffle, randint
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchWindowException, ElementNotInteractableException, WebDriverException

from config.personals import *
from config.questions import *
from config.search import *
from config.secrets import use_AI, username, password, ai_provider, github_token
from config.settings import *

from modules.open_chrome import *
from modules.helpers import *
from modules.clickers_and_finders import *
from modules.validator import validate_config
from modules.ai.openaiConnections import ai_create_openai_client, ai_extract_skills, ai_answer_question, ai_generate_coverletter, ai_close_openai_client
from modules.ai.deepseekConnections import deepseek_create_client, deepseek_extract_skills, deepseek_answer_question
from modules.ai.geminiConnections import gemini_create_client, gemini_extract_skills, gemini_answer_question
from modules.git_integration import analyze_jd_requirements, identify_repo_gaps, generate_poc_improvements, commit_to_poc_repo

from typing import Literal


pyautogui.FAILSAFE = False
# if use_resume_generator:    from resume_generator import is_logged_in_GPT, login_GPT, open_resume_chat, create_custom_resume


#< Global Variables and logics

if run_in_background == True:
    pause_at_failed_question = False
    pause_before_submit = False
    run_non_stop = False

first_name = first_name.strip()
middle_name = middle_name.strip()
last_name = last_name.strip()
full_name = first_name + " " + middle_name + " " + last_name if middle_name else first_name + " " + last_name

useNewResume = True
randomly_answered_questions = set()

tabs_count = 1
easy_applied_count = 0
external_jobs_count = 0
failed_count = 0
skip_count = 0
dailyEasyApplyLimitReached = False

re_experience = re.compile(r'[(]?\s*(\d+)\s*[)]?\s*[-to]*\s*\d*[+]*\s*year[s]?', re.IGNORECASE)

desired_salary_lakhs = str(round(desired_salary / 100000, 2))
desired_salary_monthly = str(round(desired_salary/12, 2))
desired_salary = str(desired_salary)

current_ctc_lakhs = str(round(current_ctc / 100000, 2))
current_ctc_monthly = str(round(current_ctc/12, 2))
current_ctc = str(current_ctc)

notice_period_months = str(notice_period//30)
notice_period_weeks = str(notice_period//7)
notice_period = str(notice_period)

aiClient = None
##> ------ Dheeraj Deshwal : dheeraj9811 Email:dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Feature ------
about_company_for_ai = None # TODO extract about company for AI
##<

#>


#< Login Functions
def is_logged_in_LN() -> bool:
    '''
    Function to check if user is logged-in in LinkedIn
    * Returns: `True` if user is logged-in or `False` if not
    '''
    if driver.current_url == "https://www.linkedin.com/feed/": return True
    if try_linkText(driver, "Sign in"): return False
    if try_xp(driver, '//button[@type="submit" and contains(text(), "Sign in")]'):  return False
    if try_linkText(driver, "Join now"): return False
    print_lg("Didn't find Sign in link, so assuming user is logged in!")
    return True


def login_LN() -> None:
    '''
    Function to login for LinkedIn
    * Tries to login using given `username` and `password` from `secrets.py`
    * If failed, tries to login using saved LinkedIn profile button if available
    * If both failed, asks user to login manually
    '''
    # Find the username and password fields and fill them with user credentials
    driver.get("https://www.linkedin.com/login")
    try:
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
        try:
            text_input_by_ID(driver, "username", username, 1)
        except Exception as e:
            print_lg("Couldn't find username field.")
            # print_lg(e)
        try:
            text_input_by_ID(driver, "password", password, 1)
        except Exception as e:
            print_lg("Couldn't find password field.")
            # print_lg(e)
        # Find the login submit button and click it
        driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
    except Exception as e1:
        try:
            profile_button = find_by_class(driver, "profile__details")
            profile_button.click()
        except Exception as e2:
            # print_lg(e1, e2)
            print_lg("Couldn't Login!")

    try:
        # Wait until successful redirect, indicating successful login
        wait.until(EC.url_to_be("https://www.linkedin.com/feed/")) # wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space(.)="Start a post"]')))
        return print_lg("Login successful!")
    except Exception as e:
        print_lg("Seems like login attempt failed! Possibly due to wrong credentials or already logged in! Try logging in manually!")
        # print_lg(e)
        manual_login_retry(is_logged_in_LN, 2)
#>



def get_cataloged_job_ids() -> set:
    '''
    Function to get a `set` of cataloged job's Job IDs
    * Returns a set of Job IDs from existing jobs catalog csv file
    '''
    job_ids = set()
    try:
        if os.path.exists(jobs_catalog_file):
            with open(jobs_catalog_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row and row.get('Job ID'):
                        job_ids.add(row['Job ID'])
    except FileNotFoundError:
        print_lg(f"The CSV file '{jobs_catalog_file}' does not exist.")
    except Exception as e:
        print_lg(f"Error reading cataloged jobs: {e}")
    return job_ids


# Legacy function for backward compatibility
def get_applied_job_ids() -> set:
    '''
    Legacy function - redirects to get_cataloged_job_ids for cataloging purposes.
    '''
    return get_cataloged_job_ids()



def set_search_location() -> None:
    '''
    Function to set search location
    '''
    if search_location.strip():
        try:
            print_lg(f'Setting search location as: "{search_location.strip()}"')
            search_location_ele = try_xp(driver, ".//input[@aria-label='City, state, or zip code'and not(@disabled)]", False) #  and not(@aria-hidden='true')]")
            text_input(actions, search_location_ele, search_location, "Search Location")
        except ElementNotInteractableException:
            try_xp(driver, ".//label[@class='jobs-search-box__input-icon jobs-search-box__keywords-label']")
            actions.send_keys(Keys.TAB, Keys.TAB).perform()
            actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
            actions.send_keys(search_location.strip()).perform()
            sleep(2)
            actions.send_keys(Keys.ENTER).perform()
            try_xp(driver, ".//button[@aria-label='Cancel']")
        except Exception as e:
            try_xp(driver, ".//button[@aria-label='Cancel']")
            print_lg("Failed to update search location, continuing with default location!", e)


def apply_filters() -> None:
    '''
    Function to apply job search filters
    '''
    set_search_location()

    try:
        recommended_wait = 1 if click_gap < 1 else 0

        wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space()="All filters"]'))).click()
        buffer(recommended_wait)

        wait_span_click(driver, sort_by)
        wait_span_click(driver, date_posted)
        buffer(recommended_wait)

        multi_sel_noWait(driver, experience_level) 
        multi_sel_noWait(driver, companies, actions)
        if experience_level or companies: buffer(recommended_wait)

        multi_sel_noWait(driver, job_type)
        multi_sel_noWait(driver, on_site)
        if job_type or on_site: buffer(recommended_wait)

        if easy_apply_only: boolean_button_click(driver, actions, "Easy Apply")
        
        multi_sel_noWait(driver, location)
        multi_sel_noWait(driver, industry)
        if location or industry: buffer(recommended_wait)

        multi_sel_noWait(driver, job_function)
        multi_sel_noWait(driver, job_titles)
        if job_function or job_titles: buffer(recommended_wait)

        if under_10_applicants: boolean_button_click(driver, actions, "Under 10 applicants")
        if in_your_network: boolean_button_click(driver, actions, "In your network")
        if fair_chance_employer: boolean_button_click(driver, actions, "Fair Chance Employer")

        wait_span_click(driver, salary)
        buffer(recommended_wait)
        
        multi_sel_noWait(driver, benefits)
        multi_sel_noWait(driver, commitments)
        if benefits or commitments: buffer(recommended_wait)

        show_results_button: WebElement = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Apply current filters to show")]')
        show_results_button.click()

        global pause_after_filters
        if pause_after_filters and "Turn off Pause after search" == safe_confirm("These are your configured search results and filter. It is safe to change them while this dialog is open, any changes later could result in errors and skipping this search run.", "Please check your results", ["Turn off Pause after search", "Look's good, Continue"]):
            pause_after_filters = False

    except Exception as e:
        print_lg("Setting the preferences failed!")
        # print_lg(e)



def get_page_info() -> tuple[WebElement | None, int | None]:
    '''
    Function to get pagination element and current page number
    '''
    try:
        pagination_element = try_find_by_classes(driver, ["jobs-search-pagination__pages", "artdeco-pagination", "artdeco-pagination__pages"])
        scroll_to_view(driver, pagination_element)
        current_page = int(pagination_element.find_element(By.XPATH, "//button[contains(@class, 'active')]").text)
    except Exception as e:
        print_lg("Failed to find Pagination element, hence couldn't scroll till end!")
        pagination_element = None
        current_page = None
        print_lg(e)
    return pagination_element, current_page



def should_skip_job_by_location(work_location: str, work_style: str, title: str, company: str, job_id: str) -> bool:
    '''
    Function to determine if a job should be skipped based on location requirements.
    Returns True if job should be skipped, False if job should be applied to.
    
    Rules:
    - Remote jobs: Accept from anywhere (all locations)
    - Chicago area jobs: Accept all (on-site, remote, hybrid)
    - Outside Chicago: Only accept remote (skip on-site and hybrid)
    '''
    # Check if location is in Chicago area
    chicago_indicators = ["Chicago", "IL", "Illinois", "chicago", "illinois"]
    location_lower = work_location.lower() if work_location else ""
    
    is_chicago = False
    for indicator in chicago_indicators:
        if indicator.lower() in location_lower:
            is_chicago = True
            break
    
    # If it's a Remote job, always accept (regardless of location)
    if work_style and "Remote" in work_style:
        return False  # Don't skip - remote jobs accepted everywhere
    
    # If it's in Chicago area, accept all work styles (on-site, hybrid, remote)
    if is_chicago:
        return False  # Don't skip - all Chicago area jobs accepted
    
    # If it's On-site or Hybrid outside Chicago, skip it
    if work_style and ("On-site" in work_style or "Hybrid" in work_style):
        print_lg(f'Skipping "{title} | {company}" job ({work_style} but not in Chicago area: {work_location}). Job ID: {job_id}!')
        return True
    
    # If work style is unknown, be conservative and accept
    return False


def extract_salary_from_job_listing(job: WebElement) -> float:
    '''
    Extract salary information from job listing element.
    Returns salary as float (highest value if range), or 0.0 if not found.
    '''
    try:
        # Try to find salary information in the job listing
        salary_text = ""
        
        # Try multiple selectors for salary in listing
        salary_selectors = [
            './/span[contains(text(), "$")]',
            './/span[contains(text(), "k")]',
            './/span[contains(@class, "salary")]',
            './/div[contains(@class, "salary")]',
            './/span[contains(@class, "job-card-container__metadata-item")]',
            './/li[contains(@class, "job-card-container__metadata-item")]',
        ]
        
        for selector in salary_selectors:
            try:
                salary_elements = job.find_elements(By.XPATH, selector)
                for elem in salary_elements:
                    text = elem.text.strip()
                    if '$' in text or ('k' in text.lower() and any(c.isdigit() for c in text)) or 'salary' in text.lower():
                        salary_text = text
                        break
                if salary_text:
                    break
            except:
                continue
        
        # If not found in listing, try to extract from job details panel (if visible)
        if not salary_text:
            try:
                # Check if job details panel is visible and contains salary
                salary_panel_selectors = [
                    '//div[contains(@class, "jobs-box__html-content")]//span[contains(text(), "$")]',
                    '//div[contains(@class, "jobs-details-top-card")]//span[contains(text(), "$")]',
                    '//div[contains(@class, "jobs-details")]//span[contains(text(), "$")]',
                ]
                for selector in salary_panel_selectors:
                    try:
                        salary_elements = driver.find_elements(By.XPATH, selector)
                        for elem in salary_elements:
                            text = elem.text.strip()
                            if '$' in text and any(c.isdigit() for c in text):
                                salary_text = text
                                break
                        if salary_text:
                            break
                    except:
                        continue
            except:
                pass
        
        if not salary_text:
            return 0.0
        
        # Extract numeric value from salary text
        import re
        # Remove commas and extract numbers
        numbers = re.findall(r'[\d,]+', salary_text.replace(',', ''))
        if not numbers:
            return 0.0
        
        # Get the highest number (for ranges like "$100k - $150k" or "$100,000 - $150,000")
        max_salary = 0.0
        for num_str in numbers:
            try:
                num = float(num_str.replace(',', ''))
                # Handle 'k' suffix (thousands) - if number is less than 1000 and text has 'k'
                if 'k' in salary_text.lower() and num < 1000:
                    num = num * 1000
                # If number seems too small for salary (less than 10k), might be in thousands already
                elif num < 10000 and 'k' in salary_text.lower():
                    num = num * 1000
                max_salary = max(max_salary, num)
            except:
                continue
        
        return max_salary
        
    except Exception as e:
        return 0.0


def get_job_main_details(job: WebElement, blacklisted_companies: set, rejected_jobs: set) -> tuple[str, str, str, str, str, bool]:
    '''
    # Function to get job main details.
    Returns a tuple of (job_id, title, company, work_location, work_style, skip)
    * job_id: Job ID
    * title: Job title
    * company: Company name
    * work_location: Work location of this job
    * work_style: Work style of this job (Remote, On-site, Hybrid)
    * skip: A boolean flag to skip this job
    '''
    try:
        # Try multiple ways to find the job details button
        job_details_button = None
        try:
            job_details_button = job.find_element(By.TAG_NAME, 'a')
        except:
            try:
                job_details_button = job.find_element(By.CLASS_NAME, "job-card-list__title")
            except:
                try:
                    job_details_button = job.find_element(By.CSS_SELECTOR, "a[data-control-id]")
                except:
                    pass
        
        if not job_details_button:
            print_lg("Could not find job details button")
            return ("unknown", "Unknown Job", "Unknown Company", "Unknown Location", "Unknown", True)
            
        scroll_to_view(driver, job_details_button, True)
        job_id = job.get_dom_attribute('data-occludable-job-id')
        title = job_details_button.text
        title = title[:title.find("\n")] if "\n" in title else title
        
        # Try multiple possible class names for job details
        other_details = ""
        try:
            other_details = job.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__subtitle').text
        except:
            try:
                other_details = job.find_element(By.CLASS_NAME, 'job-card-container__primary-description').text
            except:
                try:
                    other_details = job.find_element(By.CLASS_NAME, 'job-card-container__metadata-item').text
                except:
                    try:
                        other_details = job.find_element(By.CLASS_NAME, 'job-card-container__secondary-description').text
                    except:
                        try:
                            other_details = job.find_element(By.CSS_SELECTOR, '[class*="job-card-container"] [class*="description"]').text
                        except:
                            other_details = "Unknown Company · Unknown Location"
        
        if ' · ' in other_details:
            index = other_details.find(' · ')
            company = other_details[:index]
            work_location = other_details[index+3:]
            if '(' in work_location and ')' in work_location:
                work_style = work_location[work_location.rfind('(')+1:work_location.rfind(')')]
                work_location = work_location[:work_location.rfind('(')].strip()
            else:
                work_style = "Unknown"
        else:
            company = other_details
            work_location = "Unknown"
            work_style = "Unknown"
    except Exception as e:
        print_lg(f"Failed to extract job details: {e}")
        return ("unknown", "Unknown Job", "Unknown Company", "Unknown Location", "Unknown", True)
    
    # Skip if previously rejected due to blacklist or already applied
    skip = False
    if company in blacklisted_companies:
        print_lg(f'Skipping "{title} | {company}" job (Blacklisted Company). Job ID: {job_id}!')
        skip = True
    elif job_id in rejected_jobs: 
        print_lg(f'Skipping previously rejected "{title} | {company}" job. Job ID: {job_id}!')
        skip = True
    
    # Chicago location filtering logic
    if not skip:
        skip = should_skip_job_by_location(work_location, work_style, title, company, job_id)
    try:
        if job.find_element(By.CLASS_NAME, "job-card-container__footer-job-state").text == "Applied":
            skip = True
            print_lg(f'Already applied to "{title} | {company}" job. Job ID: {job_id}!')
    except: pass
    try: 
        if not skip: job_details_button.click()
    except Exception as e:
        print_lg(f'Failed to click "{title} | {company}" job on details button. Job ID: {job_id}!') 
        # print_lg(e)
        discard_job()
        job_details_button.click() # To pass the error outside
    buffer(click_gap)
    return (job_id,title,company,work_location,work_style,skip)


# Function to check for Blacklisted words in About Company
def check_blacklist(rejected_jobs: set, job_id: str, company: str, blacklisted_companies: set) -> tuple[set, set, WebElement, str] | ValueError:
    jobs_top_card = try_find_by_classes(driver, ["job-details-jobs-unified-top-card__primary-description-container","job-details-jobs-unified-top-card__primary-description","jobs-unified-top-card__primary-description","jobs-details__main-content"])
    about_company_org = find_by_class(driver, "jobs-company__box")
    scroll_to_view(driver, about_company_org)
    about_company_org = about_company_org.text
    about_company = about_company_org.lower()
    skip_checking = False
    for word in about_company_good_words:
        if word.lower() in about_company:
            print_lg(f'Found the word "{word}". So, skipped checking for blacklist words.')
            skip_checking = True
            break
    if not skip_checking:
        for word in about_company_bad_words: 
            if word.lower() in about_company: 
                rejected_jobs.add(job_id)
                blacklisted_companies.add(company)
                raise ValueError(f'\n"{about_company_org}"\n\nContains "{word}".')
    buffer(click_gap)
    scroll_to_view(driver, jobs_top_card)
    return rejected_jobs, blacklisted_companies, jobs_top_card, about_company_org



# Function to extract years of experience required from About Job
def extract_years_of_experience(text: str) -> int:
    # Extract all patterns like '10+ years', '5 years', '3-5 years', etc.
    matches = re.findall(re_experience, text)
    if len(matches) == 0: 
        print_lg(f'\n{text}\n\nCouldn\'t find experience requirement in About the Job!')
        return 0
    return max([int(match) for match in matches if int(match) <= 12])



def get_job_description(
) -> tuple[
    str | Literal['Unknown'],
    int | Literal['Unknown'],
    bool,
    str | None,
    str | None
    ]:
    '''
    # Job Description
    Function to extract job description from About the Job.
    ### Returns:
    - `jobDescription: str | 'Unknown'`
    - `experience_required: int | 'Unknown'`
    - `skip: bool`
    - `skipReason: str | None`
    - `skipMessage: str | None`
    '''
    try:
        ##> ------ Dheeraj Deshwal : dheeraj9811 Email:dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Feature ------
        jobDescription = "Unknown"
        ##<
        experience_required = "Unknown"
        found_masters = 0
        jobDescription = find_by_class(driver, "jobs-box__html-content").text
        jobDescriptionLow = jobDescription.lower()
        skip = False
        skipReason = None
        skipMessage = None
        for word in bad_words:
            if word.lower() in jobDescriptionLow:
                skipMessage = f'\n{jobDescription}\n\nContains bad word "{word}". Skipping this job!\n'
                skipReason = "Found a Bad Word in About Job"
                skip = True
                break
        if not skip and security_clearance == False and ('polygraph' in jobDescriptionLow or 'clearance' in jobDescriptionLow or 'secret' in jobDescriptionLow):
            skipMessage = f'\n{jobDescription}\n\nFound "Clearance" or "Polygraph". Skipping this job!\n'
            skipReason = "Asking for Security clearance"
            skip = True
        if not skip:
            if did_masters and 'master' in jobDescriptionLow:
                print_lg(f'Found the word "master" in \n{jobDescription}')
                found_masters = 2
            experience_required = extract_years_of_experience(jobDescription)
            if current_experience > -1 and experience_required > current_experience + found_masters:
                skipMessage = f'\n{jobDescription}\n\nExperience required {experience_required} > Current Experience {current_experience + found_masters}. Skipping this job!\n'
                skipReason = "Required experience is high"
                skip = True
    except Exception as e:
        if jobDescription == "Unknown":    print_lg("Unable to extract job description!")
        else:
            experience_required = "Error in extraction"
            print_lg("Unable to extract years of experience required!")
            # print_lg(e)
    return jobDescription, experience_required, skip, skipReason, skipMessage
        


# Function to upload resume
def upload_resume(modal: WebElement, resume: str) -> tuple[bool, str]:
    try:
        modal.find_element(By.NAME, "file").send_keys(os.path.abspath(resume))
        return True, os.path.basename(default_resume_path)
    except: return False, "Previous resume"

# Function to answer common questions for Easy Apply
def get_enhanced_user_information() -> str:
    '''
    Get user information with portfolio repository URL appended.
    Returns enhanced user_information_all string with portfolio URL if available.
    '''
    enhanced_info = user_information_all if user_information_all else ""
    
    # Add portfolio repo URL if available
    if quant_poc_repo_remote:
        repo_url = quant_poc_repo_remote
        # Remove authentication token if present
        if '@' in repo_url:
            repo_url = repo_url.split('@')[-1]
        # Remove .git extension if present
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        # Ensure https:// format
        if not repo_url.startswith('http'):
            repo_url = 'https://' + repo_url.lstrip('/')
        
        portfolio_section = f"\n\nPortfolio Repository: {repo_url}"
        enhanced_info = enhanced_info + portfolio_section if enhanced_info else portfolio_section
    
    return enhanced_info


def answer_common_questions(label: str, answer: str) -> str:
    if 'sponsorship' in label or 'visa' in label: answer = require_visa
    return answer


# Function to answer the questions for Easy Apply
def answer_questions(modal: WebElement, questions_list: set, work_location: str, job_description: str | None = None, about_company: str | None = None, required_skills: dict | None = None) -> set:
    # Get all questions from the page
     
    all_questions = modal.find_elements(By.XPATH, ".//div[@data-test-form-element]")
    # all_questions = modal.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-element")
    # all_list_questions = modal.find_elements(By.XPATH, ".//div[@data-test-text-entity-list-form-component]")
    # all_single_line_questions = modal.find_elements(By.XPATH, ".//div[@data-test-single-line-text-form-component]")
    # all_questions = all_questions + all_list_questions + all_single_line_questions

    for Question in all_questions:
        # Check if it's a select Question
        select = try_xp(Question, ".//select", False)
        if select:
            label_org = "Unknown"
            try:
                label = Question.find_element(By.TAG_NAME, "label")
                label_org = label.find_element(By.TAG_NAME, "span").text
            except: pass
            answer = 'Yes'
            label = label_org.lower()
            select = Select(select)
            selected_option = select.first_selected_option.text
            optionsText = []
            options = '"List of phone country codes"'
            if label != "phone country code":
                optionsText = [option.text for option in select.options]
                options = "".join([f' "{option}",' for option in optionsText])
            prev_answer = selected_option
            if overwrite_previous_answers or selected_option == "Select an option":
                ##> ------ WINDY_WINDWARD Email:karthik.sarode23@gmail.com - Added fuzzy logic to answer location based questions ------
                if 'email' in label or 'phone' in label: 
                    answer = prev_answer
                elif 'gender' in label or 'sex' in label: 
                    answer = gender
                elif 'disability' in label: 
                    answer = disability_status
                elif 'proficiency' in label: 
                    answer = 'Professional'
                # Add location handling
                elif any(loc_word in label for loc_word in ['location', 'city', 'state', 'country']):
                    if 'country' in label:
                        answer = country 
                    elif 'state' in label:
                        answer = state
                    elif 'city' in label:
                        answer = current_city if current_city else work_location
                    else:
                        answer = work_location
                else: 
                    answer = answer_common_questions(label,answer)
                try: 
                    select.select_by_visible_text(answer)
                except NoSuchElementException as e:
                    # Define similar phrases for common answers
                    possible_answer_phrases = []
                    if answer == 'Decline':
                        possible_answer_phrases = ["Decline", "not wish", "don't wish", "Prefer not", "not want"]
                    elif 'yes' in answer.lower():
                        possible_answer_phrases = ["Yes", "Agree", "I do", "I have"]
                    elif 'no' in answer.lower():
                        possible_answer_phrases = ["No", "Disagree", "I don't", "I do not"]
                    else:
                        # Try partial matching for any answer
                        possible_answer_phrases = [answer]
                        # Add lowercase and uppercase variants
                        possible_answer_phrases.append(answer.lower())
                        possible_answer_phrases.append(answer.upper())
                        # Try without special characters
                        possible_answer_phrases.append(''.join(c for c in answer if c.isalnum()))
                    ##<
                    foundOption = False
                    for phrase in possible_answer_phrases:
                        for option in optionsText:
                            # Check if phrase is in option or option is in phrase (bidirectional matching)
                            if phrase.lower() in option.lower() or option.lower() in phrase.lower():
                                select.select_by_visible_text(option)
                                answer = option
                                foundOption = True
                                break
                    if not foundOption:
                        #TODO: Use AI to answer the question need to be implemented logic to extract the options for the question
                        print_lg(f'Failed to find an option with text "{answer}" for question labelled "{label_org}", answering randomly!')
                        select.select_by_index(randint(1, len(select.options)-1))
                        answer = select.first_selected_option.text
                        randomly_answered_questions.add((f'{label_org} [ {options} ]',"select"))
            questions_list.add((f'{label_org} [ {options} ]', answer, "select", prev_answer))
            continue
        
        # Check if it's a radio Question
        radio = try_xp(Question, './/fieldset[@data-test-form-builder-radio-button-form-component="true"]', False)
        if radio:
            prev_answer = None
            label = try_xp(radio, './/span[@data-test-form-builder-radio-button-form-component__title]', False)
            try: label = find_by_class(label, "visually-hidden", 2.0)
            except: pass
            label_org = label.text if label else "Unknown"
            answer = 'Yes'
            label = label_org.lower()

            label_org += ' [ '
            options = radio.find_elements(By.TAG_NAME, 'input')
            options_labels = []
            
            for option in options:
                id = option.get_attribute("id")
                option_label = try_xp(radio, f'.//label[@for="{id}"]', False)
                options_labels.append( f'"{option_label.text if option_label else "Unknown"}"<{option.get_attribute("value")}>' ) # Saving option as "label <value>"
                if option.is_selected(): prev_answer = options_labels[-1]
                label_org += f' {options_labels[-1]},'

            if overwrite_previous_answers or prev_answer is None:
                if 'citizenship' in label or 'employment eligibility' in label: answer = us_citizenship
                elif 'veteran' in label or 'protected' in label: answer = veteran_status
                elif 'disability' in label or 'handicapped' in label: 
                    answer = disability_status
                else: answer = answer_common_questions(label,answer)
                foundOption = try_xp(radio, f".//label[normalize-space()='{answer}']", False)
                if foundOption: 
                    actions.move_to_element(foundOption).click().perform()
                else:    
                    if not options or not options_labels:
                        print_lg(f'No options found for radio question "{label_org}". Skipping this question.')
                        randomly_answered_questions.add((f'{label_org} ]',"radio"))
                        continue
                    possible_answer_phrases = ["Decline", "not wish", "don't wish", "Prefer not", "not want"] if answer == 'Decline' else [answer]
                    ele = options[0]
                    answer = options_labels[0]
                    for phrase in possible_answer_phrases:
                        for i, option_label in enumerate(options_labels):
                            if phrase in option_label:
                                foundOption = options[i]
                                ele = foundOption
                                answer = f'Decline ({option_label})' if len(possible_answer_phrases) > 1 else option_label
                                break
                        if foundOption: break
                    # if answer == 'Decline':
                    #     answer = options_labels[0]
                    #     for phrase in ["Prefer not", "not want", "not wish"]:
                    #         foundOption = try_xp(radio, f".//label[normalize-space()='{phrase}']", False)
                    #         if foundOption:
                    #             answer = f'Decline ({phrase})'
                    #             ele = foundOption
                    #             break
                    actions.move_to_element(ele).click().perform()
                    if not foundOption: randomly_answered_questions.add((f'{label_org} ]',"radio"))
            else: answer = prev_answer
            questions_list.add((label_org+" ]", answer, "radio", prev_answer))
            continue
        
        # Check if it's a text question
        text = try_xp(Question, ".//input[@type='text']", False)
        if text: 
            do_actions = False
            label = try_xp(Question, ".//label[@for]", False)
            try: label = label.find_element(By.CLASS_NAME,'visually-hidden')
            except: pass
            label_org = label.text if label else "Unknown"
            answer = "" # years_of_experience
            label = label_org.lower()

            prev_answer = text.get_attribute("value")
            if not prev_answer or overwrite_previous_answers:
                if 'experience' in label or 'years' in label: answer = years_of_experience
                elif 'phone' in label or 'mobile' in label: answer = phone_number
                elif 'street' in label: answer = street
                elif 'city' in label or 'location' in label or 'address' in label:
                    answer = current_city if current_city else work_location
                    do_actions = True
                elif 'signature' in label: answer = full_name # 'signature' in label or 'legal name' in label or 'your name' in label or 'full name' in label: answer = full_name     # What if question is 'name of the city or university you attend, name of referral etc?'
                elif 'name' in label:
                    if 'full' in label: answer = full_name
                    elif 'first' in label and 'last' not in label: answer = first_name
                    elif 'middle' in label and 'last' not in label: answer = middle_name
                    elif 'last' in label and 'first' not in label: answer = last_name
                    elif 'employer' in label: answer = recent_employer
                    else: answer = full_name
                elif 'notice' in label:
                    if 'month' in label:
                        answer = notice_period_months
                    elif 'week' in label:
                        answer = notice_period_weeks
                    else: answer = notice_period
                elif 'salary' in label or 'compensation' in label or 'ctc' in label or 'pay' in label: 
                    if 'current' in label or 'present' in label:
                        if 'month' in label:
                            answer = current_ctc_monthly
                        elif 'lakh' in label:
                            answer = current_ctc_lakhs
                        else:
                            answer = current_ctc
                    else:
                        if 'month' in label:
                            answer = desired_salary_monthly
                        elif 'lakh' in label:
                            answer = desired_salary_lakhs
                        else:
                            answer = desired_salary
                elif 'linkedin' in label: answer = linkedIn
                elif 'website' in label or 'blog' in label or 'portfolio' in label or 'link' in label: answer = website
                elif 'scale of 1-10' in label: answer = confidence_level
                elif 'headline' in label: answer = linkedin_headline
                elif ('hear' in label or 'come across' in label) and 'this' in label and ('job' in label or 'position' in label): answer = "https://github.com/GodsScion/Auto_job_applier_linkedIn"
                elif 'state' in label or 'province' in label: answer = state
                elif 'zip' in label or 'postal' in label or 'code' in label: answer = zipcode
                elif 'country' in label: answer = country
                # College/Education related questions
                elif 'college' in label or 'university' in label or 'school' in label:
                    if 'name' in label or 'institution' in label: answer = college_name
                    elif 'start' in label or 'begin' in label: answer = college_start_date
                    elif 'end' in label or 'graduation' in label or 'graduate' in label: answer = college_end_date
                    elif 'degree' in label: answer = college_degree
                    elif 'major' in label or 'field' in label or 'study' in label: answer = college_major
                    else: answer = college_name
                elif 'education' in label or 'degree' in label:
                    if 'start' in label or 'begin' in label: answer = college_start_date
                    elif 'end' in label or 'graduation' in label or 'graduate' in label: answer = college_end_date
                    elif 'institution' in label or 'school' in label: answer = college_name
                    elif 'major' in label or 'field' in label or 'study' in label: answer = college_major
                    else: answer = college_degree
                elif 'graduation' in label or 'graduate' in label:
                    if 'date' in label or 'year' in label: answer = college_end_date
                    elif 'school' in label or 'college' in label or 'university' in label: answer = college_name
                    else: answer = college_end_date
                else: answer = answer_common_questions(label,answer)
                ##> ------ Yang Li : MARKYangL - Feature ------
                if answer == "":
                    if use_AI and aiClient:
                        try:
                            ai_answer = None
                            enhanced_user_info = get_enhanced_user_information()
                            if ai_provider.lower() == "openai":
                                ai_answer = ai_answer_question(aiClient, label_org, question_type="text", job_description=job_description, user_information_all=enhanced_user_info)
                            elif ai_provider.lower() == "deepseek":
                                ai_answer = deepseek_answer_question(aiClient, label_org, options=None, question_type="text", job_description=job_description, about_company=None, user_information_all=enhanced_user_info)
                            elif ai_provider.lower() == "gemini":
                                ai_answer = gemini_answer_question(aiClient, label_org, options=None, question_type="text", job_description=job_description, about_company=None, user_information_all=enhanced_user_info)
                            
                            # Check if AI returned a valid answer
                            if ai_answer and isinstance(ai_answer, str) and len(ai_answer) > 0:
                                answer = ai_answer
                                print_lg(f'AI Answered received for question "{label_org}" \nhere is answer: "{answer}"')
                            else:
                                # AI failed or returned empty - use fallback
                                randomly_answered_questions.add((label_org, "text"))
                                answer = years_of_experience
                        except Exception as e:
                            # Gracefully handle AI errors - use fallback answer
                            print_lg(f"Failed to get AI answer (using fallback): {e}")
                            randomly_answered_questions.add((label_org, "text"))
                            answer = years_of_experience
                    else:
                        randomly_answered_questions.add((label_org, "text"))
                        answer = years_of_experience
                ##<
                text.clear()
                text.send_keys(answer)
                if do_actions:
                    sleep(2)
                    actions.send_keys(Keys.ARROW_DOWN)
                    actions.send_keys(Keys.ENTER).perform()
            questions_list.add((label, text.get_attribute("value"), "text", prev_answer))
            continue

        # Check if it's a textarea question
        text_area = try_xp(Question, ".//textarea", False)
        if text_area:
            label = try_xp(Question, ".//label[@for]", False)
            label_org = label.text if label else "Unknown"
            label = label_org.lower()
            answer = ""
            prev_answer = text_area.get_attribute("value")
            if not prev_answer or overwrite_previous_answers:
                if 'summary' in label: answer = linkedin_summary
                elif 'cover' in label:
                    # Use AI to generate dynamic cover letter if AI is enabled and we have the necessary info
                    if use_AI and aiClient and job_description and job_description != "Unknown":
                        try:
                            print_lg("Detected cover letter question - generating dynamic cover letter using AI...")
                            enhanced_user_info = get_enhanced_user_information()
                            if ai_provider.lower() == "openai":
                                generated_cover_letter = ai_generate_coverletter(
                                    aiClient, 
                                    job_description, 
                                    about_company if about_company else "Unknown",
                                    required_skills if required_skills and isinstance(required_skills, dict) else {},
                                    user_information_all=enhanced_user_info
                                )
                                if generated_cover_letter and isinstance(generated_cover_letter, str) and len(generated_cover_letter) > 0:
                                    answer = generated_cover_letter
                                    print_lg(f'AI Generated cover letter for question "{label_org}"')
                                else:
                                    # Fallback to static cover letter if AI generation fails
                                    answer = cover_letter
                                    print_lg("AI cover letter generation returned empty, using static cover letter")
                            else:
                                # For other AI providers, use static cover letter for now
                                # TODO: Implement cover letter generation for DeepSeek and Gemini
                                answer = cover_letter
                                print_lg(f"Cover letter generation for {ai_provider} not yet implemented, using static cover letter")
                        except Exception as e:
                            # Fallback to static cover letter on error
                            print_lg(f"Failed to generate AI cover letter (using static): {e}")
                            answer = cover_letter
                    else:
                        # Use static cover letter if AI is not enabled or info is missing
                        answer = cover_letter
                if answer == "":
                ##> ------ Yang Li : MARKYangL - Feature ------
                    if use_AI and aiClient:
                        try:
                            ai_answer = None
                            enhanced_user_info = get_enhanced_user_information()
                            if ai_provider.lower() == "openai":
                                ai_answer = ai_answer_question(aiClient, label_org, question_type="textarea", job_description=job_description, user_information_all=enhanced_user_info)
                            elif ai_provider.lower() == "deepseek":
                                ai_answer = deepseek_answer_question(aiClient, label_org, options=None, question_type="textarea", job_description=job_description, about_company=None, user_information_all=enhanced_user_info)
                            elif ai_provider.lower() == "gemini":
                                ai_answer = gemini_answer_question(aiClient, label_org, options=None, question_type="textarea", job_description=job_description, about_company=None, user_information_all=enhanced_user_info)
                            
                            # Check if AI returned a valid answer
                            if ai_answer and isinstance(ai_answer, str) and len(ai_answer) > 0:
                                answer = ai_answer
                                print_lg(f'AI Answered received for question "{label_org}" \nhere is answer: "{answer}"')
                            else:
                                # AI failed or returned empty - use fallback
                                randomly_answered_questions.add((label_org, "textarea"))
                                answer = ""
                        except Exception as e:
                            # Gracefully handle AI errors - use fallback answer
                            print_lg(f"Failed to get AI answer (using fallback): {e}")
                            randomly_answered_questions.add((label_org, "textarea"))
                            answer = ""
                    else:
                        randomly_answered_questions.add((label_org, "textarea"))
            text_area.clear()
            text_area.send_keys(answer)
            if do_actions:
                    sleep(2)
                    actions.send_keys(Keys.ARROW_DOWN)
                    actions.send_keys(Keys.ENTER).perform()
            questions_list.add((label, text_area.get_attribute("value"), "textarea", prev_answer))
            ##<
            continue

        # Check if it's a checkbox question
        checkbox = try_xp(Question, ".//input[@type='checkbox']", False)
        if checkbox:
            label = try_xp(Question, ".//span[@class='visually-hidden']", False)
            label_org = label.text if label else "Unknown"
            label = label_org.lower()
            answer = try_xp(Question, ".//label[@for]", False)  # Sometimes multiple checkboxes are given for 1 question, Not accounted for that yet
            answer = answer.text if answer else "Unknown"
            prev_answer = checkbox.is_selected()
            checked = prev_answer
            if not prev_answer:
                try:
                    actions.move_to_element(checkbox).click().perform()
                    checked = True
                except Exception as e: 
                    print_lg("Checkbox click failed!", e)
                    pass
            questions_list.add((f'{label} ([X] {answer})', checked, "checkbox", prev_answer))
            continue


    # Select todays date
    try_xp(driver, "//button[contains(@aria-label, 'This is today')]")

    # Collect important skills
    # if 'do you have' in label and 'experience' in label and ' in ' in label -> Get word (skill) after ' in ' from label
    # if 'how many years of experience do you have in ' in label -> Get word (skill) after ' in '

    return questions_list




def external_apply(pagination_element: WebElement, job_id: str, job_link: str, resume: str, date_listed, application_link: str, screenshot_name: str) -> tuple[bool, str, int]:
    '''
    Function to open new tab and save external job application links
    '''
    global tabs_count, dailyEasyApplyLimitReached
    if easy_apply_only:
        try:
            if "exceeded the daily application limit" in driver.find_element(By.CLASS_NAME, "artdeco-inline-feedback__message").text: dailyEasyApplyLimitReached = True
        except: pass
        print_lg("Easy apply failed I guess!")
        if pagination_element != None: return True, application_link, tabs_count
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, ".//button[contains(@class,'jobs-apply-button') and contains(@class, 'artdeco-button--3')]"))).click() # './/button[contains(span, "Apply") and not(span[contains(@class, "disabled")])]'
        wait_span_click(driver, "Continue", 1, True, False)
        windows = driver.window_handles
        tabs_count = len(windows)
        driver.switch_to.window(windows[-1])
        application_link = driver.current_url
        print_lg('Got the external application link "{}"'.format(application_link))
        if close_tabs and driver.current_window_handle != linkedIn_tab: driver.close()
        driver.switch_to.window(linkedIn_tab)
        return False, application_link, tabs_count
    except Exception as e:
        # print_lg(e)
        print_lg("Failed to apply!")
        failed_job(job_id, job_link, resume, date_listed, "Probably didn't find Apply button or unable to switch tabs.", e, application_link, screenshot_name)
        global failed_count
        failed_count += 1
        return True, application_link, tabs_count



def follow_company(modal: WebDriver = driver) -> None:
    '''
    Function to follow or un-follow easy applied companies based om `follow_companies`
    '''
    try:
        follow_checkbox_input = try_xp(modal, ".//input[@id='follow-company-checkbox' and @type='checkbox']", False)
        if follow_checkbox_input and follow_checkbox_input.is_selected() != follow_companies:
            try_xp(modal, ".//label[@for='follow-company-checkbox']")
    except Exception as e:
        print_lg("Failed to update follow companies checkbox!", e)
    


#< Failed attempts logging
def failed_job(job_id: str, job_link: str, resume: str, date_listed, error: str, exception: Exception, application_link: str, screenshot_name: str) -> None:
    '''
    Function to update failed jobs list in excel
    '''
    try:
        with open(failed_file_name, 'a', newline='', encoding='utf-8') as file:
            fieldnames = ['Job ID', 'Job Link', 'Resume Tried', 'Date listed', 'Date Tried', 'Assumed Reason', 'Stack Trace', 'External Job link', 'Screenshot Name']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0: writer.writeheader()
            writer.writerow({'Job ID':truncate_for_csv(job_id), 'Job Link':truncate_for_csv(job_link), 'Resume Tried':truncate_for_csv(resume), 'Date listed':truncate_for_csv(date_listed), 'Date Tried':datetime.now(), 'Assumed Reason':truncate_for_csv(error), 'Stack Trace':truncate_for_csv(exception), 'External Job link':truncate_for_csv(application_link), 'Screenshot Name':truncate_for_csv(screenshot_name)})
            file.close()
    except Exception as e:
        print_lg("Failed to update failed jobs list!", e)
        safe_alert("Failed to update the excel of failed jobs!\nProbably because of 1 of the following reasons:\n1. The file is currently open or in use by another program\n2. Permission denied to write to the file\n3. Failed to find the file", "Failed Logging")


def screenshot(driver: WebDriver, job_id: str, failedAt: str) -> str:
    '''
    Function to to take screenshot for debugging
    - Returns screenshot name as String
    '''
    screenshot_name = "{} - {} - {}.png".format( job_id, failedAt, str(datetime.now()) )
    path = logs_folder_path+"/screenshots/"+screenshot_name.replace(":",".")
    # special_chars = {'*', '"', '\\', '<', '>', ':', '|', '?'}
    # for char in special_chars:  path = path.replace(char, '-')
    driver.save_screenshot(path.replace("//","/"))
    return screenshot_name
#>



def catalog_job(job_id: str, title: str, company: str, work_location: str, work_style: str, description: str, 
                experience_required: int | Literal['Unknown', 'Error in extraction'], 
                skills: list[str] | Literal['In Development'], hr_name: str | Literal['Unknown'], 
                hr_link: str | Literal['Unknown'], reposted: bool, date_listed: datetime | Literal['Unknown'], 
                job_link: str, connection_status: str = "Not Connected", connection_date: str = "") -> None:
    '''
    Function to catalog job information to CSV file for quant job search tracking.
    '''
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(jobs_catalog_file), exist_ok=True)
        
        with open(jobs_catalog_file, mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['Job ID', 'Title', 'Company', 'Work Location', 'Work Style', 'Job Description', 
                         'Experience required', 'Skills required', 'Recruiter Name', 'Recruiter Link', 
                         'Recruiter Title', 'Recruiter Company', 'Date Posted', 'Job Link', 
                         'Connection Status', 'Connection Date']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            if csv_file.tell() == 0: writer.writeheader()
            writer.writerow({
                'Job ID': truncate_for_csv(job_id), 
                'Title': truncate_for_csv(title), 
                'Company': truncate_for_csv(company), 
                'Work Location': truncate_for_csv(work_location), 
                'Work Style': truncate_for_csv(work_style), 
                'Job Description': truncate_for_csv(description), 
                'Experience required': truncate_for_csv(experience_required), 
                'Skills required': truncate_for_csv(skills), 
                'Recruiter Name': truncate_for_csv(hr_name), 
                'Recruiter Link': truncate_for_csv(hr_link), 
                'Recruiter Title': truncate_for_csv(""),  # Will be populated by catalog_recruiter
                'Recruiter Company': truncate_for_csv(""),  # Will be populated by catalog_recruiter
                'Date Posted': truncate_for_csv(date_listed), 
                'Job Link': truncate_for_csv(job_link), 
                'Connection Status': truncate_for_csv(connection_status),
                'Connection Date': truncate_for_csv(connection_date)
            })
        csv_file.close()
    except Exception as e:
        print_lg("Failed to catalog job!", e)
        safe_alert("Failed to update the jobs catalog!\nProbably because of 1 of the following reasons:\n1. The file is currently open or in use by another program\n2. Permission denied to write to the file\n3. Failed to find the file", "Failed Logging")


def catalog_recruiter(recruiter_name: str, recruiter_link: str, recruiter_title: str = "", 
                      recruiter_company: str = "", job_id: str = "", connection_status: str = "Not Connected",
                      first_contact_date: str = "", last_message_date: str = "", notes: str = "") -> None:
    '''
    Function to catalog recruiter information to CSV file.
    Updates existing entry if recruiter already exists, otherwise creates new entry.
    '''
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(recruiters_catalog_file), exist_ok=True)
        
        # Read existing recruiters
        recruiters = {}
        fieldnames = ['Recruiter Name', 'Recruiter Link', 'Recruiter Title', 'Recruiter Company', 
                     'Jobs Posted', 'First Contact Date', 'Connection Status', 'Last Message Date', 'Notes']
        
        if os.path.exists(recruiters_catalog_file):
            try:
                with open(recruiters_catalog_file, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row.get('Recruiter Link'):
                            recruiters[row['Recruiter Link']] = row
            except Exception as e:
                print_lg(f"Error reading existing recruiters file: {e}")
        
        # Update or create recruiter entry
        if recruiter_link in recruiters:
            # Update existing entry
            existing = recruiters[recruiter_link]
            # Update jobs posted list
            jobs_posted = existing.get('Jobs Posted', '')
            if job_id and job_id not in jobs_posted:
                jobs_posted = f"{jobs_posted},{job_id}" if jobs_posted else job_id
            existing['Jobs Posted'] = jobs_posted
            # Update other fields if provided
            if recruiter_title: existing['Recruiter Title'] = recruiter_title
            if recruiter_company: existing['Recruiter Company'] = recruiter_company
            if connection_status: existing['Connection Status'] = connection_status
            if first_contact_date: existing['First Contact Date'] = first_contact_date
            if last_message_date: existing['Last Message Date'] = last_message_date
            if notes: existing['Notes'] = notes
        else:
            # Create new entry
            recruiters[recruiter_link] = {
                'Recruiter Name': recruiter_name,
                'Recruiter Link': recruiter_link,
                'Recruiter Title': recruiter_title,
                'Recruiter Company': recruiter_company,
                'Jobs Posted': job_id,
                'First Contact Date': first_contact_date,
                'Connection Status': connection_status,
                'Last Message Date': last_message_date,
                'Notes': notes
            }
        
        # Write all recruiters back to file
        with open(recruiters_catalog_file, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for recruiter in recruiters.values():
                writer.writerow({k: truncate_for_csv(v) for k, v in recruiter.items()})
        csv_file.close()
    except Exception as e:
        print_lg("Failed to catalog recruiter!", e)
        safe_alert("Failed to update the recruiters catalog!\nProbably because of 1 of the following reasons:\n1. The file is currently open or in use by another program\n2. Permission denied to write to the file\n3. Failed to find the file", "Failed Logging")


# Legacy function for backward compatibility
def submitted_jobs(job_id: str, title: str, company: str, work_location: str, work_style: str, description: str, 
                   experience_required: int | Literal['Unknown', 'Error in extraction'], 
                   skills: list[str] | Literal['In Development'], hr_name: str | Literal['Unknown'], 
                   hr_link: str | Literal['Unknown'], resume: str, reposted: bool, 
                   date_listed: datetime | Literal['Unknown'], date_applied: datetime | Literal['Pending'], 
                   job_link: str, application_link: str, questions_list: set | None, 
                   connect_request: Literal['In Development']) -> None:
    '''
    Legacy function - redirects to catalog_job for cataloging purposes.
    '''
    catalog_job(job_id, title, company, work_location, work_style, description, experience_required, 
                skills, hr_name, hr_link, reposted, date_listed, job_link)



def connect_with_recruiter(hr_link: str, hr_name: str, message_template: str = "") -> tuple[bool, str]:
    '''
    Sends a LinkedIn connection request to a recruiter.
    Returns (success: bool, status_message: str)
    '''
    if not connect_with_recruiters:
        return False, "Connection requests disabled in settings"
    
    if not hr_link or hr_link == "Unknown":
        return False, "No recruiter link available"
    
    try:
        # Store current window
        original_window = driver.current_window_handle
        
        # Open recruiter profile in new tab
        driver.execute_script(f"window.open('{hr_link}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        buffer(2)
        
        # Check if already connected
        try:
            if try_xp(driver, ".//span[contains(text(), 'Connected')]", 2):
                driver.close()
                driver.switch_to.window(original_window)
                return True, "Already connected"
        except:
            pass
        
        # Check if connection request already sent
        try:
            if try_xp(driver, ".//span[contains(text(), 'Pending')]", 2):
                driver.close()
                driver.switch_to.window(original_window)
                return True, "Connection request already pending"
        except:
            pass
        
        # Find and click Connect button
        connect_button = None
        try:
            # Try to find Connect button
            connect_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, ".//button[contains(@aria-label, 'Connect') or contains(span, 'Connect')]"))
            )
        except:
            try:
                # Alternative: look for More button then Connect
                more_button = try_xp(driver, ".//button[contains(@aria-label, 'More')]", 2)
                if more_button:
                    more_button.click()
                    buffer(1)
                    connect_button = try_xp(driver, ".//button[contains(span, 'Connect')]", 2)
            except:
                pass
        
        if not connect_button:
            driver.close()
            driver.switch_to.window(original_window)
            return False, "Could not find Connect button"
        
        scroll_to_view(driver, connect_button)
        connect_button.click()
        buffer(2)
        
        # Add note if message template provided
        if message_template:
            try:
                # Look for "Add a note" button
                add_note_button = try_xp(driver, ".//button[contains(span, 'Add a note') or contains(text(), 'Add a note')]", 2)
                if add_note_button:
                    add_note_button.click()
                    buffer(1)
                    
                    # Find message textarea
                    message_box = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, ".//textarea[@placeholder or @aria-label]"))
                    )
                    message_box.clear()
                    message_box.send_keys(message_template)
                    buffer(1)
            except Exception as e:
                print_lg(f"Could not add note to connection request: {e}")
        
        # Send connection request
        try:
            send_button = try_xp(driver, ".//button[contains(@aria-label, 'Send') or contains(span, 'Send')]", 2)
            if send_button:
                send_button.click()
                buffer(2)
        except:
            # Some LinkedIn UIs auto-send when note is added
            pass
        
        # Close tab and return to original window
        if close_tabs:
            driver.close()
        driver.switch_to.window(original_window)
        
        return True, "Connection request sent successfully"
        
    except Exception as e:
        print_lg(f"Failed to send connection request to {hr_name}: {e}")
        try:
            if len(driver.window_handles) > 1:
                driver.close()
            driver.switch_to.window(original_window)
        except:
            pass
        return False, f"Error: {str(e)}"


def send_message_to_connection(profile_link: str, message: str) -> tuple[bool, str]:
    '''
    Send a LinkedIn message to an existing connection.
    Returns (success: bool, status_message: str)
    '''
    try:
        # Store current window
        original_window = driver.current_window_handle
        
        # Open profile in new tab
        driver.execute_script(f"window.open('{profile_link}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        buffer(2)
        
        # Check if connected
        try:
            if not try_xp(driver, ".//span[contains(text(), 'Connected')]", 2):
                driver.close()
                driver.switch_to.window(original_window)
                return False, "Not connected yet"
        except:
            pass
        
        # Find Message button
        message_button = None
        try:
            # Try to find Message button directly
            message_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, ".//button[contains(@aria-label, 'Message') or contains(span, 'Message')]"))
            )
        except:
            try:
                # Alternative: look for More button then Message
                more_button = try_xp(driver, ".//button[contains(@aria-label, 'More')]", 2)
                if more_button:
                    more_button.click()
                    buffer(1)
                    message_button = try_xp(driver, ".//button[contains(span, 'Message')]", 2)
            except:
                pass
        
        if not message_button:
            driver.close()
            driver.switch_to.window(original_window)
            return False, "Could not find Message button"
        
        scroll_to_view(driver, message_button)
        message_button.click()
        buffer(3)
        
        # Find message input box
        try:
            # Wait for message box to appear
            message_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, ".//div[@contenteditable='true' and @role='textbox'] | .//textarea[@placeholder or @aria-label]"))
            )
            buffer(1)
            
            # Clear and type message
            message_box.click()
            buffer(1)
            message_box.send_keys(Keys.CONTROL + "a")
            message_box.send_keys(Keys.DELETE)
            buffer(0.5)
            message_box.send_keys(message)
            buffer(1)
            
            # Send message
            send_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, ".//button[contains(@aria-label, 'Send') or contains(@data-control-name, 'send')]"))
            )
            send_button.click()
            buffer(2)
            
        except Exception as e:
            print_lg(f"Could not send message: {e}")
            driver.close()
            driver.switch_to.window(original_window)
            return False, f"Error sending message: {str(e)}"
        
        # Close tab and return to original window
        if close_tabs:
            driver.close()
        driver.switch_to.window(original_window)
        
        return True, "Message sent successfully"
        
    except Exception as e:
        print_lg(f"Failed to send message to {profile_link}: {e}")
        try:
            if len(driver.window_handles) > 1:
                driver.close()
            driver.switch_to.window(original_window)
        except:
            pass
        return False, f"Error: {str(e)}"


def send_followup_to_accepted_connections() -> None:
    '''
    Check for recruiters who accepted connection requests and send them follow-up messages
    with the portfolio repository URL.
    '''
    from config.settings import (
        send_followup_to_accepted_connections, 
        followup_message_template,
        max_followup_messages_per_day,
        recruiters_catalog_file,
        quant_poc_repo_remote
    )
    
    if not send_followup_to_accepted_connections:
        return
    
    try:
        # Read recruiters catalog
        if not os.path.exists(recruiters_catalog_file):
            return
        
        recruiters_to_check = []
        with open(recruiters_catalog_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Check for recruiters with pending connections or who haven't been messaged yet
                connection_status = row.get('Connection Status', '')
                last_message_date = row.get('Last Message Date', '')
                
                # Check if we should send follow-up:
                # 1. Connection status is "Pending" or "Not Connected" (might have accepted)
                # 2. No message sent yet (empty Last Message Date)
                if (connection_status in ['Pending', 'Not Connected', ''] or not last_message_date) and row.get('Recruiter Link'):
                    recruiters_to_check.append(row)
        
        if not recruiters_to_check:
            print_lg("[Follow-up] No recruiters to check for accepted connections")
            return
        
        print_lg(f"[Follow-up] Checking {len(recruiters_to_check)} recruiter(s) for accepted connections...")
        
        # Get portfolio repo URL
        portfolio_repo_url = ""
        if quant_poc_repo_remote:
            repo_url = quant_poc_repo_remote
            if '@' in repo_url:
                repo_url = repo_url.split('@')[-1]
            if repo_url.endswith('.git'):
                repo_url = repo_url[:-4]
            if not repo_url.startswith('http'):
                repo_url = 'https://' + repo_url.lstrip('/')
            portfolio_repo_url = repo_url
        
        messages_sent_today = 0
        
        for recruiter in recruiters_to_check:
            if messages_sent_today >= max_followup_messages_per_day:
                print_lg(f"[Follow-up] Reached daily limit of {max_followup_messages_per_day} messages")
                break
            
            recruiter_name = recruiter.get('Recruiter Name', '')
            recruiter_link = recruiter.get('Recruiter Link', '')
            recruiter_company = recruiter.get('Recruiter Company', '')
            
            if not recruiter_link or recruiter_link == "Unknown":
                continue
            
            # Check if connection was accepted
            try:
                original_window = driver.current_window_handle
                driver.execute_script(f"window.open('{recruiter_link}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
                buffer(2)
                
                # Check connection status
                is_connected = False
                try:
                    if try_xp(driver, ".//span[contains(text(), 'Connected')]", 2):
                        is_connected = True
                except:
                    pass
                
                driver.close()
                driver.switch_to.window(original_window)
                
                if is_connected:
                    # Format message
                    message = followup_message_template.format(
                        recruiter_name=recruiter_name,
                        company_name=recruiter_company,
                        portfolio_repo_url=portfolio_repo_url
                    ) if followup_message_template else f"Hi {recruiter_name}, thanks for connecting! Check out my portfolio: {portfolio_repo_url}"
                    
                    # Send message
                    success, status = send_message_to_connection(recruiter_link, message)
                    
                    if success:
                        # Update catalog
                        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        catalog_recruiter(
                            recruiter_name, recruiter_link,
                            recruiter.get('Recruiter Title', ''),
                            recruiter_company,
                            recruiter.get('Jobs Posted', ''),
                            connection_status="Connected",
                            last_message_date=current_date,
                            notes=f"Follow-up message sent: {current_date}"
                        )
                        messages_sent_today += 1
                        print_lg(f"[Follow-up] Sent message to {recruiter_name}: {status}")
                    else:
                        print_lg(f"[Follow-up] Failed to send message to {recruiter_name}: {status}")
                
            except Exception as e:
                print_lg(f"[Follow-up] Error checking {recruiter_name}: {e}")
                continue
        
        if messages_sent_today > 0:
            print_lg(f"[Follow-up] Sent {messages_sent_today} follow-up message(s) to accepted connections")
        
    except Exception as e:
        print_lg(f"[Follow-up] Error in follow-up process: {e}")


# Function to discard the job application
def discard_job() -> None:
    actions.send_keys(Keys.ESCAPE).perform()
    wait_span_click(driver, 'Discard', 2)






# Function to catalog quant jobs
def catalog_quant_jobs(search_terms: list[str]) -> None:
    '''
    Main function to search for quant jobs, catalog them, and optionally connect with recruiters.
    Removed all application logic - focuses on cataloging and networking.
    '''
    cataloged_jobs = get_cataloged_job_ids()
    rejected_jobs = set()
    blacklisted_companies = set()
    connections_today = 0
    global current_city, failed_count, skip_count
    current_city = current_city.strip()
    
    # Portfolio improvement tracking
    portfolio_improvements = []  # Track improvements per job: [(job_id, title, gaps, files_created)]
    pending_files_to_commit = []  # Batch files for commit
    pending_gaps_to_commit = []  # Batch gaps for commit message

    if randomize_search_order:  shuffle(search_terms)
    for searchTerm in search_terms:
        driver.get(f"https://www.linkedin.com/jobs/search/?keywords={searchTerm}")
        print_lg("\n________________________________________________________________________________________________________________________\n")
        print_lg(f'\n>>>> Now searching for "{searchTerm}" <<<<\n\n')

        apply_filters()

        current_count = 0
        try:
            while current_count < switch_number:
                # Wait until job listings are loaded
                wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[@data-occludable-job-id]")))

                pagination_element, current_page = get_page_info()

                # Find all job listings in current page
                buffer(3)
                job_listings = driver.find_elements(By.XPATH, "//li[@data-occludable-job-id]")
                
                # Extract salary and filter/sort by salary if enabled
                from config.search import sort_by_salary_descending, minimum_salary_filter
                
                if sort_by_salary_descending or minimum_salary_filter > 0:
                    print_lg("[Salary Filter] Extracting salaries from job listings...")
                    # Extract salary for each job and create tuples (salary, job_element)
                    jobs_with_salary = []
                    for job in job_listings:
                        salary = extract_salary_from_job_listing(job)
                        jobs_with_salary.append((salary, job))
                    
                    # Filter by minimum salary if enabled
                    if minimum_salary_filter > 0:
                        original_count = len(jobs_with_salary)
                        jobs_with_salary = [(s, j) for s, j in jobs_with_salary if s >= minimum_salary_filter or s == 0]
                        filtered_count = len(jobs_with_salary)
                        if original_count > filtered_count:
                            print_lg(f"[Salary Filter] Filtered out {original_count - filtered_count} job(s) below ${minimum_salary_filter:,}")
                        print_lg(f"[Salary Filter] Processing {filtered_count} job(s) meeting minimum salary of ${minimum_salary_filter:,}")
                    
                    # Sort by salary descending (highest first) if enabled
                    if sort_by_salary_descending:
                        # Sort: jobs with salary (highest first), then jobs without salary info
                        jobs_with_salary.sort(key=lambda x: (x[0] > 0, x[0]), reverse=True)
                        # Count jobs with salary info
                        jobs_with_salary_count = sum(1 for salary, _ in jobs_with_salary if salary > 0)
                        print_lg(f"[Sorting] Sorted {len(jobs_with_salary)} jobs by salary ({jobs_with_salary_count} with salary info, highest first)")
                    
                    job_listings = [job for _, job in jobs_with_salary]

            
                for job in job_listings:
                    if keep_screen_awake: pyautogui.press('shiftright')
                    if current_count >= switch_number: break
                    print_lg("\n-@-\n")

                    job_id, title, company, work_location, work_style, skip = get_job_main_details(job, blacklisted_companies, rejected_jobs)
                    
                    if skip: continue
                    
                    # Check if already cataloged
                    try:
                        if job_id in cataloged_jobs:
                            print_lg(f'Already cataloged "{title} | {company}" job. Job ID: {job_id}!')
                            continue
                    except Exception as e:
                        print_lg(f'Cataloging "{title} | {company}" job. Job ID: {job_id}')

                    job_link = "https://www.linkedin.com/jobs/view/"+job_id
                    hr_link = "Unknown"
                    hr_name = "Unknown"
                    hr_title = ""
                    hr_company = ""
                    date_listed = "Unknown"
                    skills = "Not extracted"
                    reposted = False
                    connection_status = "Not Connected"
                    connection_date = ""

                    about_company_text = "Unknown"
                    jobs_top_card = None
                    try:
                        rejected_jobs, blacklisted_companies, jobs_top_card, about_company_text = check_blacklist(rejected_jobs, job_id, company, blacklisted_companies)
                    except ValueError as e:
                        print_lg(e, 'Skipping this job!\n')
                        skip_count += 1
                        continue
                    except Exception as e:
                        print_lg("Failed to scroll to About Company!")
                        # print_lg(e)



                    # Recruiter/Hiring Manager info
                    try:
                        hr_info_card = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "hirer-card__hirer-information")))
                        hr_link = hr_info_card.find_element(By.TAG_NAME, "a").get_attribute("href")
                        hr_name = hr_info_card.find_element(By.TAG_NAME, "span").text
                        # Try to extract recruiter title and company if available
                        try:
                            hr_title_elem = hr_info_card.find_elements(By.TAG_NAME, "span")
                            if len(hr_title_elem) > 1:
                                hr_title = hr_title_elem[1].text if len(hr_title_elem) > 1 else ""
                        except:
                            pass
                    except Exception as e:
                        print_lg(f'Recruiter info was not given for "{title}" with Job ID: {job_id}!')
                        # print_lg(e)

                    # Calculation of date posted
                    try:
                        if jobs_top_card:
                            time_posted_text = jobs_top_card.find_element(By.XPATH, './/span[contains(normalize-space(), " ago")]').text
                            print("Time Posted: " + time_posted_text)
                            if time_posted_text.__contains__("Reposted"):
                                reposted = True
                                time_posted_text = time_posted_text.replace("Reposted", "")
                            date_listed = calculate_date_posted(time_posted_text.strip())
                    except Exception as e:
                        print_lg("Failed to calculate the date posted!", e)

                    # Extract job description
                    description, experience_required, skip, reason, message = get_job_description()
                    if skip and not catalog_all_jobs:
                        print_lg(message)
                        rejected_jobs.add(job_id)
                        skip_count += 1
                        continue

                    # Extract skills using AI if enabled
                    if use_AI and description != "Unknown" and save_job_descriptions:
                        try:
                            if aiClient:
                                if ai_provider.lower() == "openai":
                                    skills = ai_extract_skills(aiClient, description)
                                elif ai_provider.lower() == "deepseek":
                                    skills = deepseek_extract_skills(aiClient, description)
                                elif ai_provider.lower() == "gemini":
                                    skills = gemini_extract_skills(aiClient, description)
                                else:
                                    skills = "Not extracted"
                                print_lg(f"Extracted skills using {ai_provider} AI")
                            else:
                                skills = "AI client not available"
                                print_lg("AI client not available, skipping skill extraction")
                        except Exception as e:
                            print_lg(f"Failed to extract skills: {e}")
                            skills = "AI extraction failed"

                    # Catalog the job
                    catalog_job(job_id, title, company, work_location, work_style, description, 
                               experience_required, skills, hr_name, hr_link, reposted, date_listed, 
                               job_link, connection_status, connection_date)
                    
                    # Catalog the recruiter
                    if hr_name != "Unknown" and hr_link != "Unknown" and save_recruiter_profiles:
                        # Add portfolio repo URL to notes if available
                        notes = ""
                        if quant_poc_repo_remote:
                            repo_url = quant_poc_repo_remote
                            # Remove authentication token if present
                            if '@' in repo_url:
                                repo_url = repo_url.split('@')[-1]
                            # Remove .git extension if present
                            if repo_url.endswith('.git'):
                                repo_url = repo_url[:-4]
                            # Ensure https:// format
                            if not repo_url.startswith('http'):
                                repo_url = 'https://' + repo_url.lstrip('/')
                            notes = f"Portfolio: {repo_url}"
                        
                        catalog_recruiter(hr_name, hr_link, hr_title, hr_company, job_id, 
                                         connection_status, connection_date, "", notes)

                    # Optionally connect with recruiter
                    if connect_with_recruiters and hr_link != "Unknown" and connections_today < max_connections_per_day:
                        # Get portfolio repo URL for message
                        portfolio_repo_url = ""
                        if quant_poc_repo_remote:
                            # Convert git URL to GitHub URL format (remove .git, handle https://token@github.com format)
                            repo_url = quant_poc_repo_remote
                            # Remove authentication token if present
                            if '@' in repo_url:
                                repo_url = repo_url.split('@')[-1]
                            # Remove .git extension if present
                            if repo_url.endswith('.git'):
                                repo_url = repo_url[:-4]
                            # Ensure https:// format
                            if not repo_url.startswith('http'):
                                repo_url = 'https://' + repo_url.lstrip('/')
                            portfolio_repo_url = repo_url
                        
                        # Format connection message template
                        message = connection_message_template.format(
                            recruiter_name=hr_name,
                            company_name=company,
                            job_title=title,
                            portfolio_repo_url=portfolio_repo_url
                        ) if connection_message_template else ""
                        
                        success, status = connect_with_recruiter(hr_link, hr_name, message)
                        if success:
                            connections_today += 1
                            # Update connection status in catalog
                            connection_status = "Connected" if "connected" in status.lower() else "Pending"
                            catalog_recruiter(
                                hr_name, hr_link, hr_title, hr_company, job_id,
                                connection_status=connection_status,
                                notes=notes if notes else f"Connection request sent: {status}"
                            )
                            print_lg(f"Connection request to {hr_name}: {status}") 
                            # For now, we'll track it in the next run or manually update.
                        else:
                            print_lg(f"Failed to connect with {hr_name}: {status}")

                    print_lg(f'Successfully cataloged "{title} | {company}" job. Job ID: {job_id}')
                    
                    # Improve portfolio repo based on JD requirements if enabled (sophisticated real-time improvement)
                    if auto_improve_repo and quant_poc_repo_path and description != "Unknown":
                        try:
                            if use_ai_for_requirements and aiClient:
                                print_lg(f"\n[Portfolio Improvement] Analyzing JD for: {title} at {company}")
                                
                                # Analyze JD requirements with enhanced extraction
                                jd_requirements = analyze_jd_requirements(description, aiClient)
                                
                                # Identify gaps in portfolio with enhanced analysis
                                from config.settings import portfolio_min_gap_priority
                                gaps = identify_repo_gaps(jd_requirements, quant_poc_repo_path, 
                                                         min_priority=portfolio_min_gap_priority)
                                
                                if gaps:
                                    print_lg(f"[Portfolio] Identified {len(gaps)} gap(s) from this JD: {', '.join(gaps[:3])}")
                                    if len(gaps) > 3:
                                        print_lg(f"  ... and {len(gaps) - 3} more")
                                    
                                    # Generate improvements
                                    created_files = generate_poc_improvements(
                                        gaps, jd_requirements, aiClient, quant_poc_repo_path
                                    )
                                    
                                    if created_files:
                                        # Track improvement for this job
                                        if track_improvements_per_job:
                                            portfolio_improvements.append({
                                                'job_id': job_id,
                                                'title': title,
                                                'company': company,
                                                'gaps': gaps,
                                                'files_created': created_files
                                            })
                                        
                                        # Batch commits based on settings
                                        from config.settings import portfolio_commit_batch_size
                                        
                                        if portfolio_commit_batch_size == 0:
                                            # Commit immediately
                                            commit_to_poc_repo(
                                                quant_poc_repo_path, 
                                                created_files, 
                                                gaps,
                                                quant_poc_repo_remote,
                                                github_token
                                            )
                                            print_lg(f"[Portfolio] ✓ Committed {len(created_files)} new file(s) immediately")
                                        else:
                                            # Batch for later commit
                                            pending_files_to_commit.extend(created_files)
                                            pending_gaps_to_commit.extend(gaps)
                                            print_lg(f"[Portfolio] ✓ Queued {len(created_files)} file(s) for batch commit")
                                            
                                            # Commit if batch size reached
                                            if len(pending_files_to_commit) >= portfolio_commit_batch_size:
                                                # Remove duplicates while preserving order
                                                unique_files = []
                                                seen = set()
                                                for f in pending_files_to_commit:
                                                    if f not in seen:
                                                        unique_files.append(f)
                                                        seen.add(f)
                                                
                                                unique_gaps = list(set(pending_gaps_to_commit))
                                                
                                                commit_to_poc_repo(
                                                    quant_poc_repo_path, 
                                                    unique_files, 
                                                    unique_gaps,
                                                    quant_poc_repo_remote,
                                                    github_token
                                                )
                                                print_lg(f"[Portfolio] ✓ Batch committed {len(unique_files)} file(s) from {len(portfolio_improvements)} job(s)")
                                                
                                                # Clear batch
                                                pending_files_to_commit = []
                                                pending_gaps_to_commit = []
                                    else:
                                        print_lg("[Portfolio] No new files created (may already exist)")
                                else:
                                    print_lg("[Portfolio] ✓ No gaps - portfolio already covers all requirements")
                            else:
                                if not use_ai_for_requirements:
                                    print_lg("[Portfolio] AI requirements extraction disabled")
                                elif not aiClient:
                                    print_lg("[Portfolio] AI client not available")
                        except Exception as e:
                            print_lg(f"[Portfolio] Error improving portfolio repo: {e}")
                            import traceback
                            print_lg(traceback.format_exc())
                    
                    current_count += 1
                    cataloged_jobs.add(job_id)



                # Switching to next page
                if pagination_element == None:
                    print_lg("Couldn't find pagination element, probably at the end page of results!")
                    break
                try:
                    pagination_element.find_element(By.XPATH, f"//button[@aria-label='Page {current_page+1}']").click()
                    print_lg(f"\n>-> Now on Page {current_page+1} \n")
                except NoSuchElementException:
                    print_lg(f"\n>-> Didn't find Page {current_page+1}. Probably at the end page of results!\n")
                    break

        except (NoSuchWindowException, WebDriverException) as e:
            print_lg("Browser window closed or session is invalid. Ending cataloging process.", e)
            raise e # Re-raise to be caught by main
        except Exception as e:
            print_lg("Failed to find Job listings!")
            critical_error_log("In Cataloger", e)
            try:
                print_lg(driver.page_source, pretty=True)
            except Exception as page_source_error:
                print_lg(f"Failed to get page source, browser might have crashed. {page_source_error}")
            # print_lg(e)
    
    # Send follow-up messages to recruiters who accepted connections
    try:
        send_followup_to_accepted_connections()
    except Exception as e:
        print_lg(f"[Follow-up] Error in follow-up process: {e}")
    
    # Final commit of any pending portfolio improvements
    if auto_improve_repo and quant_poc_repo_path and pending_files_to_commit:
        try:
            from config.settings import portfolio_commit_batch_size
            if portfolio_commit_batch_size != 0:  # Only if batching is enabled
                # Remove duplicates while preserving order
                unique_files = []
                seen = set()
                for f in pending_files_to_commit:
                    if f not in seen:
                        unique_files.append(f)
                        seen.add(f)
                
                unique_gaps = list(set(pending_gaps_to_commit))
                
                if unique_files:
                    print_lg(f"\n[Portfolio] Committing final batch of {len(unique_files)} file(s)...")
                    commit_to_poc_repo(
                        quant_poc_repo_path, 
                        unique_files, 
                        unique_gaps,
                        quant_poc_repo_remote,
                        github_token
                    )
                    print_lg(f"[Portfolio] ✓ Final batch committed: {len(unique_files)} file(s) from {len(portfolio_improvements)} job(s)")
        except Exception as e:
            print_lg(f"[Portfolio] Error in final commit: {e}")
    
    # Print portfolio improvement summary
    if track_improvements_per_job and portfolio_improvements:
        print_lg("\n" + "="*80)
        print_lg("PORTFOLIO IMPROVEMENT SUMMARY")
        print_lg("="*80)
        print_lg(f"Total jobs that improved portfolio: {len(portfolio_improvements)}")
        total_files = sum(len(imp['files_created']) for imp in portfolio_improvements)
        print_lg(f"Total files created: {total_files}")
        print_lg("\nImprovements by job:")
        for imp in portfolio_improvements:
            print_lg(f"  • {imp['title']} at {imp['company']}")
            print_lg(f"    - {len(imp['gaps'])} gap(s) identified")
            print_lg(f"    - {len(imp['files_created'])} file(s) created")
        print_lg("="*80 + "\n")


# Legacy function for backward compatibility
def apply_to_jobs(search_terms: list[str]) -> None:
    '''
    Legacy function - redirects to catalog_quant_jobs for cataloging purposes.
    '''
    catalog_quant_jobs(search_terms)

        
def run(total_runs: int) -> int:
    print_lg("\n########################################################################################################################\n")
    print_lg(f"Date and Time: {datetime.now()}")
    print_lg(f"Cycle number: {total_runs}")
    print_lg(f"Currently looking for jobs posted within '{date_posted}' and sorting them by '{sort_by}'")
    catalog_quant_jobs(search_terms)
    print_lg("########################################################################################################################\n")
    if run_non_stop:
        print_lg("Sleeping for 10 min...")
        sleep(300)
        print_lg("Few more min... Gonna start with in next 5 min...")
        sleep(300)
    buffer(3)
    return total_runs + 1



chatGPT_tab = False
linkedIn_tab = False

def main() -> None:
    try:
        global linkedIn_tab, tabs_count, useNewResume, aiClient
        alert_title = "Error Occurred. Closing Browser!"
        total_runs = 1
        
        # Clean up any existing log file issues
        safe_log_cleanup()
        force_close_log_handles()
        
        validate_config()
        
        if not os.path.exists(default_resume_path):
            current_dir = os.getcwd()
            absolute_path = os.path.abspath(default_resume_path)
            error_message = f'Your default resume "{default_resume_path}" is missing!\n\nCurrent working directory: {current_dir}\nAbsolute path: {absolute_path}\n\nPlease update the folder path "default_resume_path" in config/questions.py\n\nOR\n\nAdd a resume with exact name and path (check for spelling mistakes including cases).\n\n\nFor now the bot will continue using your previous upload from LinkedIn!'
            safe_alert(text=error_message, title="Missing Resume", button="OK")
            useNewResume = False
        
        # Login to LinkedIn
        tabs_count = len(driver.window_handles)
        driver.get("https://www.linkedin.com/login")
        if not is_logged_in_LN(): login_LN()
        
        linkedIn_tab = driver.current_window_handle

        # # Login to ChatGPT in a new tab for resume customization
        # if use_resume_generator:
        #     try:
        #         driver.switch_to.new_window('tab')
        #         driver.get("https://chat.openai.com/")
        #         if not is_logged_in_GPT(): login_GPT()
        #         open_resume_chat()
        #         global chatGPT_tab
        #         chatGPT_tab = driver.current_window_handle
        #     except Exception as e:
        #         print_lg("Opening OpenAI chatGPT tab failed!")
        if use_AI:
            if ai_provider == "openai":
                aiClient = ai_create_openai_client()
            ##> ------ Yang Li : MARKYangL - Feature ------
            # Create DeepSeek client
            elif ai_provider == "deepseek":
                aiClient = deepseek_create_client()
            elif ai_provider == "gemini":
                aiClient = gemini_create_client()
            ##<

            try:
                about_company_for_ai = " ".join([word for word in (first_name+" "+last_name).split() if len(word) > 3])
                print_lg(f"Extracted about company info for AI: '{about_company_for_ai}'")
            except Exception as e:
                print_lg("Failed to extract about company info!", e)
        
        # Start cataloging quant jobs
        driver.switch_to.window(linkedIn_tab)
        total_runs = run(total_runs)
        while(run_non_stop):
            if cycle_date_posted:
                date_options = ["Any time", "Past month", "Past week", "Past 24 hours"]
                global date_posted
                date_posted = date_options[date_options.index(date_posted)+1 if date_options.index(date_posted)+1 > len(date_options) else -1] if stop_date_cycle_at_24hr else date_options[0 if date_options.index(date_posted)+1 >= len(date_options) else date_options.index(date_posted)+1]
            if alternate_sortby:
                global sort_by
                sort_by = "Most recent" if sort_by == "Most relevant" else "Most relevant"
                total_runs = run(total_runs)
                sort_by = "Most recent" if sort_by == "Most relevant" else "Most relevant"
            total_runs = run(total_runs)
        

    except (NoSuchWindowException, WebDriverException) as e:
        print_lg("Browser window closed or session is invalid. Exiting.", e)
    except Exception as e:
        critical_error_log("In Applier Main", e)
        safe_alert(str(e), alert_title)
    finally:
        print_lg("\n\nTotal runs:                     {}".format(total_runs))
        print_lg("Jobs Easy Applied:              {}".format(easy_applied_count))
        print_lg("External job links collected:   {}".format(external_jobs_count))
        print_lg("                              ----------")
        print_lg("Total applied or collected:     {}".format(easy_applied_count + external_jobs_count))
        print_lg("\nFailed jobs:                    {}".format(failed_count))
        print_lg("Irrelevant jobs skipped:        {}\n".format(skip_count))
        if randomly_answered_questions: print_lg("\n\nQuestions randomly answered:\n  {}  \n\n".format(";\n".join(str(question) for question in randomly_answered_questions)))
        quote = choice([
            "You're one step closer than before.", 
            "All the best with your future interviews.", 
            "Keep up with the progress. You got this.", 
            "If you're tired, learn to take rest but never give up.",
            "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
            "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson",
            "Every job is a self-portrait of the person who does it. Autograph your work with excellence.",
            "The only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle. - Steve Jobs",
            "Opportunities don't happen, you create them. - Chris Grosser",
            "The road to success and the road to failure are almost exactly the same. The difference is perseverance.",
            "Obstacles are those frightful things you see when you take your eyes off your goal. - Henry Ford",
            "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt"
            ])
        msg = f"\n{quote}\n\n\nBest regards,\nSai Vignesh Golla\nhttps://www.linkedin.com/in/saivigneshgolla/\n\n"
        safe_alert(msg, "Exiting..")
        print_lg(msg,"Closing the browser...")
        if tabs_count >= 10:
            msg = "NOTE: IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM!\n\nOr it's highly likely that application will just open browser and not do anything next time!" 
            safe_alert(msg,"Info")
            print_lg("\n"+msg)
        ##> ------ Yang Li : MARKYangL - Feature ------
        if use_AI and aiClient:
            try:
                if ai_provider.lower() == "openai":
                    ai_close_openai_client(aiClient)
                elif ai_provider.lower() == "deepseek":
                    ai_close_openai_client(aiClient)
                elif ai_provider.lower() == "gemini":
                    pass # Gemini client does not need to be closed
                print_lg(f"Closed {ai_provider} AI client.")
            except Exception as e:
                print_lg("Failed to close AI client:", e)
        ##<
        try:
            if driver:
                driver.quit()
        except WebDriverException as e:
            print_lg("Browser already closed.", e)
        except Exception as e: 
            critical_error_log("When quitting...", e)


if __name__ == "__main__":
    main()
