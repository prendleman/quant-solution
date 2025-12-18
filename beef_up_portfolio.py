'''
Automated script to improve portfolio repository based on cataloged job descriptions.
This script will analyze all JDs and add missing functionality to beef up your portfolio.
'''

import os
import sys
import csv
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import quant_poc_repo_path, quant_poc_repo_remote, jobs_catalog_file
from config.secrets import use_AI, ai_provider, github_token
from modules.git_integration import analyze_jd_requirements, identify_repo_gaps, generate_poc_improvements, commit_to_poc_repo
from modules.helpers import print_lg


def find_or_create_portfolio_repo():
    '''
    Find existing portfolio repo or create one.
    '''
    # Check if path is already set
    if quant_poc_repo_path and os.path.exists(quant_poc_repo_path):
        return quant_poc_repo_path
    
    # Try common locations
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'quant_portfolio'),
        os.path.join(os.path.expanduser('~'), 'quant_portfolio'),
        'G:/My Drive/fuck_u_cunt/quant_portfolio',
        'G:/My Drive/quant_portfolio'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print_lg(f"Found existing portfolio repo: {path}")
            return path
    
    # Create in parent directory
    default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'quant_portfolio')
    print_lg(f"Creating portfolio repo at: {default_path}")
    os.makedirs(default_path, exist_ok=True)
    return default_path


def analyze_all_jds(repo_path: str):
    '''
    Analyze all cataloged JDs and improve portfolio.
    '''
    print_lg("=" * 80)
    print_lg("BEEFING UP YOUR QUANT PORTFOLIO")
    print_lg("=" * 80)
    
    if not os.path.exists(jobs_catalog_file):
        print_lg(f"ERROR: Jobs catalog not found: {jobs_catalog_file}")
        return False
    
    # Initialize AI client
    ai_client = None
    if use_AI:
        try:
            from modules.ai.openaiConnections import ai_create_openai_client
            from modules.ai.deepseekConnections import deepseek_create_client
            from modules.ai.geminiConnections import gemini_create_client
            
            if ai_provider.lower() == "openai":
                ai_client = ai_create_openai_client()
            elif ai_provider.lower() == "deepseek":
                ai_client = deepseek_create_client()
            elif ai_provider.lower() == "gemini":
                ai_client = gemini_create_client()
            print_lg(f"Initialized {ai_provider} AI client")
        except Exception as e:
            print_lg(f"AI client initialization failed: {e}")
            print_lg("Continuing with keyword-based extraction")
    
    # Aggregate requirements from all JDs
    print_lg(f"\nAnalyzing {jobs_catalog_file}...")
    all_requirements = {
        'skills': set(),
        'technologies': set(),
        'algorithms': set(),
        'tools': set(),
        'methodologies': set()
    }
    
    jobs_count = 0
    try:
        with open(jobs_catalog_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                job_desc = row.get('Job Description', '')
                if job_desc and job_desc != 'Unknown' and len(job_desc) > 100:
                    jobs_count += 1
                    jd_req = analyze_jd_requirements(job_desc, ai_client)
                    
                    # Aggregate
                    for key in all_requirements:
                        items = jd_req.get(key, [])
                        if isinstance(items, list):
                            all_requirements[key].update(items)
                        elif items:
                            all_requirements[key].add(items)
        
        print_lg(f"Processed {jobs_count} job descriptions")
        
        # Show aggregated requirements
        print_lg("\nRequirements Found:")
        for key, values in all_requirements.items():
            if values:
                items = list(values)[:15]
                print_lg(f"  {key}: {len(values)} items")
                print_lg(f"    {', '.join(items)}")
                if len(values) > 15:
                    print_lg(f"    ... and {len(values) - 15} more")
    
    except Exception as e:
        print_lg(f"Error reading jobs: {e}")
        return False
    
    # Convert to lists
    aggregated_req = {k: list(v) for k, v in all_requirements.items()}
    
    # Identify gaps
    print_lg(f"\nAnalyzing portfolio: {repo_path}")
    gaps = identify_repo_gaps(aggregated_req, repo_path)
    
    if not gaps:
        print_lg("\nNo gaps found! Your portfolio already covers all requirements.")
        return True
    
    print_lg(f"\nFound {len(gaps)} gaps to address:")
    for i, gap in enumerate(gaps[:10], 1):
        print_lg(f"  {i}. {gap}")
    if len(gaps) > 10:
        print_lg(f"  ... and {len(gaps) - 10} more")
    
    # Generate improvements
    print_lg("\nGenerating portfolio improvements...")
    created_files = generate_poc_improvements(gaps, aggregated_req, ai_client, repo_path)
    
    if not created_files:
        print_lg("No new files created")
        return False
    
    print_lg(f"\nCreated {len(created_files)} new files:")
    for file_path in created_files:
        rel_path = os.path.relpath(file_path, repo_path)
        print_lg(f"  - {rel_path}")
    
    # Commit changes
    print_lg("\nCommitting to repository...")
    success = commit_to_poc_repo(
        repo_path,
        created_files,
        gaps[:5],  # Limit to first 5 for commit message
        quant_poc_repo_remote,
        github_token
    )
    
    if success:
        print_lg("\n" + "=" * 80)
        print_lg("PORTFOLIO SUCCESSFULLY IMPROVED!")
        print_lg("=" * 80)
        print_lg(f"   Repository: {repo_path}")
        print_lg(f"   Added {len(created_files)} new features")
        print_lg(f"   Technologies: {len(aggregated_req.get('technologies', []))}")
        print_lg(f"   Skills: {len(aggregated_req.get('skills', []))}")
        print_lg("=" * 80)
    else:
        print_lg("\nFiles created but commit may have failed")
    
    # Close AI client
    if ai_client and ai_provider.lower() == "openai":
        try:
            from modules.ai.openaiConnections import ai_close_openai_client
            ai_close_openai_client(ai_client)
        except:
            pass
    
    return True


def main():
    '''
    Main function.
    '''
    # Find or create repo
    repo_path = find_or_create_portfolio_repo()
    
    if not repo_path:
        print_lg("Could not find or create portfolio repository")
        return
    
    # Update config if needed
    if repo_path != quant_poc_repo_path:
        print_lg(f"\nTip: Set quant_poc_repo_path = \"{repo_path}\" in config/settings.py")
        print_lg("   to use this path automatically in future runs\n")
    
    # Improve portfolio
    analyze_all_jds(repo_path)


if __name__ == "__main__":
    main()
