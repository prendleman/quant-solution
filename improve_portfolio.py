'''
Standalone script to improve portfolio repository based on cataloged job descriptions.
This script analyzes all cataloged JDs and adds missing functionality to the portfolio repo.
'''

import os
import sys
import csv
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import quant_poc_repo_path, quant_poc_repo_remote, auto_improve_repo, use_ai_for_requirements
from config.secrets import use_AI, ai_provider, github_token
from config.settings import jobs_catalog_file
from modules.git_integration import analyze_jd_requirements, identify_repo_gaps, generate_poc_improvements, commit_to_poc_repo
from modules.helpers import print_lg
from modules.ai.openaiConnections import ai_create_openai_client, ai_close_openai_client
from modules.ai.deepseekConnections import deepseek_create_client
from modules.ai.geminiConnections import gemini_create_client


def main():
    '''
    Main function to improve portfolio based on cataloged JDs.
    '''
    print_lg("=" * 80)
    print_lg("Portfolio Improvement Script")
    print_lg("=" * 80)
    
    # Check if portfolio repo path is set
    if not quant_poc_repo_path:
        print_lg("ERROR: quant_poc_repo_path is not set in config/settings.py")
        print_lg("Please set the path to your portfolio repository.")
        return
    
    if not os.path.exists(quant_poc_repo_path):
        print_lg(f"ERROR: Portfolio repository path does not exist: {quant_poc_repo_path}")
        print_lg("Please create the directory or update the path in config/settings.py")
        return
    
    # Check if jobs catalog exists
    if not os.path.exists(jobs_catalog_file):
        print_lg(f"ERROR: Jobs catalog file not found: {jobs_catalog_file}")
        print_lg("Please run the cataloging script first to collect job descriptions.")
        return
    
    # Initialize AI client if needed
    ai_client = None
    if use_AI and use_ai_for_requirements:
        try:
            if ai_provider.lower() == "openai":
                ai_client = ai_create_openai_client()
            elif ai_provider.lower() == "deepseek":
                ai_client = deepseek_create_client()
            elif ai_provider.lower() == "gemini":
                ai_client = gemini_create_client()
            print_lg(f"Initialized {ai_provider} AI client")
        except Exception as e:
            print_lg(f"Failed to initialize AI client: {e}")
            print_lg("Continuing without AI (will use template-based generation)")
    
    # Read all cataloged jobs
    print_lg(f"\nReading cataloged jobs from: {jobs_catalog_file}")
    all_requirements = {
        'skills': set(),
        'technologies': set(),
        'algorithms': set(),
        'tools': set(),
        'methodologies': set()
    }
    
    jobs_processed = 0
    try:
        with open(jobs_catalog_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                job_desc = row.get('Job Description', '')
                if job_desc and job_desc != 'Unknown':
                    jobs_processed += 1
                    print_lg(f"\nProcessing job {jobs_processed}: {row.get('Title', 'Unknown')}")
                    
                    # Analyze JD requirements
                    jd_req = analyze_jd_requirements(job_desc, ai_client)
                    
                    # Aggregate requirements
                    for key in all_requirements:
                        if isinstance(jd_req.get(key), list):
                            all_requirements[key].update(jd_req[key])
                        elif jd_req.get(key):
                            all_requirements[key].add(jd_req[key])
        
        print_lg(f"\nProcessed {jobs_processed} job descriptions")
        print_lg("\nAggregated Requirements:")
        for key, values in all_requirements.items():
            if values:
                print_lg(f"  {key}: {', '.join(list(values)[:10])}")
                if len(values) > 10:
                    print_lg(f"    ... and {len(values) - 10} more")
    
    except Exception as e:
        print_lg(f"Error reading jobs catalog: {e}")
        return
    
    # Convert sets to lists for gap identification
    aggregated_req = {k: list(v) for k, v in all_requirements.items()}
    
    # Identify gaps in portfolio
    print_lg(f"\nAnalyzing portfolio repository: {quant_poc_repo_path}")
    gaps = identify_repo_gaps(aggregated_req, quant_poc_repo_path)
    
    if not gaps:
        print_lg("\nNo gaps identified! Your portfolio already covers all requirements.")
        return
    
    print_lg(f"\nIdentified {len(gaps)} gaps in portfolio:")
    for i, gap in enumerate(gaps, 1):
        print_lg(f"  {i}. {gap}")
    
    # Generate improvements
    print_lg("\nGenerating portfolio improvements...")
    created_files = generate_poc_improvements(
        gaps, aggregated_req, ai_client, quant_poc_repo_path
    )
    
    if not created_files:
        print_lg("No new files were created.")
        return
    
    print_lg(f"\nCreated {len(created_files)} new files:")
    for file_path in created_files:
        print_lg(f"  - {os.path.relpath(file_path, quant_poc_repo_path)}")
    
    # Commit to repo
    print_lg("\nCommitting changes to repository...")
    success = commit_to_poc_repo(
        quant_poc_repo_path,
        created_files,
        gaps,
        quant_poc_repo_remote,
        github_token
    )
    
    if success:
        print_lg("\n✅ Portfolio repository successfully improved!")
        print_lg(f"   Added {len(created_files)} new features")
        print_lg(f"   Repository: {quant_poc_repo_path}")
    else:
        print_lg("\n⚠️  Files created but commit may have failed. Check git status.")
    
    # Close AI client
    if ai_client and ai_provider.lower() == "openai":
        try:
            ai_close_openai_client(ai_client)
        except:
            pass
    
    print_lg("\n" + "=" * 80)
    print_lg("Portfolio improvement complete!")
    print_lg("=" * 80)


if __name__ == "__main__":
    main()
