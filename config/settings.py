'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''


###################################################### CONFIGURE YOUR BOT HERE ######################################################

# >>>>>>>>>>> LinkedIn Settings <<<<<<<<<<<

# Keep the External Application tabs open?
close_tabs = False                  # True or False, Note: True or False are case-sensitive
'''
Note: RECOMMENDED TO LEAVE IT AS `True`, if you set it `False`, be sure to CLOSE ALL TABS BEFORE CLOSING THE BROWSER!!!
'''

# Follow easy applied companies
follow_companies = False            # True or False, Note: True or False are case-sensitive

# >>>>>>>>>>> Recruiter Connection Settings <<<<<<<<<<<

# Send connection requests to recruiters?
connect_with_recruiters = True     # True or False, Note: True or False are case-sensitive

# What message do you want to send during connection request? (Max. 200 Characters)
# Leave Empty to send connection request without personalized invitation (recommended to leave it empty, since you only get 10 per month without LinkedIn Premium*)
# Supports variables: {recruiter_name}, {company_name}, {job_title}, {portfolio_repo_url}
connection_message_template = "Hi {recruiter_name}, I'm interested in quant opportunities. Would love to connect! Portfolio: {portfolio_repo_url}"    # Example: "Hi {recruiter_name}, I'm interested in quant opportunities at {company_name}. Check out my work: {portfolio_repo_url}"

# Maximum number of connection requests per day (LinkedIn limit consideration)
max_connections_per_day = 50        # Only numbers greater than 0

# Skip recruiters already in your network?
skip_already_connected = True       # True or False, Note: True or False are case-sensitive

# Send follow-up message to recruiters who accepted your connection?
# This will send a message with your portfolio repository URL
send_followup_to_accepted_connections = True     # True or False, Note: True or False are case-sensitive

# Message template for follow-up to accepted connections
# Supports variables: {recruiter_name}, {company_name}, {portfolio_repo_url}
followup_message_template = "Hi {recruiter_name}, thanks for connecting! I wanted to share my quantitative finance portfolio: {portfolio_repo_url} - it showcases my work in risk management, derivatives pricing, portfolio optimization, and more. Would love to discuss quant opportunities!"

# Maximum number of follow-up messages per day (LinkedIn limit consideration)
max_followup_messages_per_day = 20        # Only numbers greater than 0

# Do you want the program to run continuously until you stop it? (Beta)
run_non_stop = False                # True or False, Note: True or False are case-sensitive
'''
Note: Will be treated as False if `run_in_background = True`
'''
alternate_sortby = True             # True or False, Note: True or False are case-sensitive
cycle_date_posted = True            # True or False, Note: True or False are case-sensitive
stop_date_cycle_at_24hr = True      # True or False, Note: True or False are case-sensitive





# >>>>>>>>>>> RESUME GENERATOR (Experimental & In Development) <<<<<<<<<<<

# Give the path to the folder where all the generated resumes are to be stored
generated_resume_path = "all resumes/" # (In Development)





# >>>>>>>>>>> Global Settings <<<<<<<<<<<

# >>>>>>>>>>> Cataloging Settings <<<<<<<<<<<

# Directory and name of the files where cataloged jobs and recruiters are saved (Sentence after the last "/" will be considered as the file name).
jobs_catalog_file = "all excels/quant_jobs_catalog.csv"
recruiters_catalog_file = "all excels/recruiters_catalog.csv"
failed_file_name = "all excels/all_failed_applications_history.csv"
logs_folder_path = "logs/"

# Catalog all jobs found, not just filtered ones?
catalog_all_jobs = True            # True or False, Note: True or False are case-sensitive

# Save full job descriptions?
save_job_descriptions = True       # True or False, Note: True or False are case-sensitive

# Extract and save recruiter profile information?
save_recruiter_profiles = True     # True or False, Note: True or False are case-sensitive

# Legacy file names (for backward compatibility)
file_name = jobs_catalog_file      # Alias for jobs_catalog_file

# Set the maximum amount of time allowed to wait between each click in secs
click_gap = 3                       # Enter max allowed secs to wait approximately. (Only Non Negative Integers Eg: 0,1,2,3,....)

# If you want to see Chrome running then set run_in_background as False (May reduce performance). 
run_in_background = False           # True or False, Note: True or False are case-sensitive ,   If True, this will make pause_at_failed_question, pause_before_submit and run_in_background as False

# If you want to disable extensions then set disable_extensions as True (Better for performance)
disable_extensions = False          # True or False, Note: True or False are case-sensitive

# Run in safe mode. Set this true if chrome is taking too long to open or if you have multiple profiles in browser. This will open chrome in guest profile!
safe_mode = True                   # True or False, Note: True or False are case-sensitive

# Do you want scrolling to be smooth or instantaneous? (Can reduce performance if True)
smooth_scroll = True               # True or False, Note: True or False are case-sensitive

# If enabled (True), the program would keep your screen active and prevent PC from sleeping. Instead you could disable this feature (set it to false) and adjust your PC sleep settings to Never Sleep or a preferred time. 
keep_screen_awake = True            # True or False, Note: True or False are case-sensitive (Note: Will temporarily deactivate when any application dialog boxes are present (Eg: Pause before submit, Help needed for a question..))

# Run in undetected mode to bypass anti-bot protections (Preview Feature, UNSTABLE. Recommended to leave it as False)
stealth_mode = False                # True or False, Note: True or False are case-sensitive

# Do you want to get alerts on errors related to AI API connection?
showAiErrorAlerts = True            # True or False, Note: True or False are case-sensitive

# Use ChatGPT for resume building (Experimental Feature can break the application. Recommended to leave it as False) 
# use_resume_generator = False       # True or False, Note: True or False are case-sensitive ,   This feature may only work with 'stealth_mode = True'. As ChatGPT website is hosted by CloudFlare which is protected by Anti-bot protections!

# >>>>>>>>>>> Git Portfolio Repo Settings <<<<<<<<<<<

# Local path to quant portfolio git repository (leave empty to disable portfolio improvements)
quant_poc_repo_path = "G:/My Drive/fuck_u_cunt/quant_portfolio"            # Example: "C:/Users/YourName/quant_portfolio" or "/path/to/quant_portfolio"

# Remote repository URL (optional, for pushing to GitHub/GitLab)
quant_poc_repo_remote = "https://github.com/prendleman/quant-solution.git"         # Example: "https://github.com/username/quant_portfolio.git"

# Automatically improve portfolio repo based on JD requirements?
auto_improve_repo = True           # True or False, Note: True or False are case-sensitive

# Use AI to extract requirements from job descriptions?
use_ai_for_requirements = True     # True or False, Note: True or False are case-sensitive

# Ensure no company-specific info in commits/code?
sanitize_commits = True             # True or False, Note: True or False are case-sensitive

# Generate professional, portfolio-ready code (docstrings, type hints, tests)?
portfolio_quality_code = True      # True or False, Note: True or False are case-sensitive

# Automatically update README.md with new features?
update_readme_auto = True          # True or False, Note: True or False are case-sensitive

# Features tracking file name in portfolio repo
features_tracking_file = "FEATURES_TRACKING.md"  # File that tracks features added to portfolio

# Portfolio improvement settings for real-time cataloging
# Batch commits: commit improvements every N jobs (0 = commit immediately, -1 = commit at end)
portfolio_commit_batch_size = 3        # Commit every N jobs (recommended: 3-5 for balance)

# Minimum gap priority to generate code (0.0-1.0, higher = more selective)
portfolio_min_gap_priority = 0.3       # Only generate code for gaps with priority >= 0.3

# Track improvements per job for better reporting
track_improvements_per_job = True      # True or False, Note: True or False are case-sensitive











############################################################################################################
'''
THANK YOU for using my tool 😊! Wishing you the best in your job hunt 🙌🏻!

Sharing is caring! If you found this tool helpful, please share it with your peers 🥺. Your support keeps this project alive.

Support my work on <PATREON_LINK>. Together, we can help more job seekers.

As an independent developer, I pour my heart and soul into creating tools like this, driven by the genuine desire to make a positive impact.

Your support, whether through donations big or small or simply spreading the word, means the world to me and helps keep this project alive and thriving.

Gratefully yours 🙏🏻,
Sai Vignesh Golla
'''
############################################################################################################