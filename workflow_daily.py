#!/usr/bin/env python3
"""
Daily Workflow Script for Quant Job Cataloging and Portfolio Improvement

This script orchestrates the complete daily workflow:
1. Consolidate today's job descriptions (from existing catalog)
2. Improve portfolio repository based on today's consolidated JDs
3. Optionally push changes to GitHub

Usage:
    python workflow_daily.py [--skip-consolidate] [--skip-improve] [--skip-push] [--date YYYYMMDD]
"""

import os
import sys
import subprocess
from datetime import date
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.helpers import print_lg


def run_script(script_name: str, args: list = None) -> bool:
    """
    Run a Python script and return success status.
    
    Args:
        script_name: Name of the script to run (without .py extension)
        args: Optional list of additional arguments
        
    Returns:
        True if script executed successfully, False otherwise
    """
    script_path = Path(__file__).parent / f"{script_name}.py"
    
    if not script_path.exists():
        print_lg(f"ERROR: Script not found: {script_path}")
        return False
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        print_lg(f"\n{'='*80}")
        print_lg(f"Running: {script_name}.py")
        print_lg(f"{'='*80}\n")
        
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent,
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        if result.returncode == 0:
            print_lg(f"\n[SUCCESS] {script_name}.py completed successfully")
            return True
        else:
            print_lg(f"\n[ERROR] {script_name}.py exited with code {result.returncode}")
            return False
            
    except Exception as e:
        print_lg(f"\n[ERROR] Failed to run {script_name}.py: {e}")
        return False


def check_consolidated_csv_exists(date_str: str = None) -> bool:
    """
    Check if consolidated CSV for today (or specified date) exists.
    
    Args:
        date_str: Optional date string in YYYYMMDD format
        
    Returns:
        True if file exists, False otherwise
    """
    if date_str is None:
        date_str = date.today().strftime('%Y%m%d')
    
    script_dir = Path(__file__).parent
    csv_file = script_dir / "all excels" / f"today_jobs_summary_{date_str}.csv"
    return csv_file.exists()


def main():
    """
    Main workflow function that orchestrates the daily process.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Daily workflow: Consolidate JDs -> Improve Portfolio -> Push to GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full workflow
  python workflow_daily.py
  
  # Skip consolidation (if already done)
  python workflow_daily.py --skip-consolidate
  
  # Skip portfolio improvement
  python workflow_daily.py --skip-improve
  
  # Skip GitHub push
  python workflow_daily.py --skip-push
  
  # Process specific date
  python workflow_daily.py --date 20251216
  
  # Run only consolidation
  python workflow_daily.py --skip-improve --skip-push
        """
    )
    
    parser.add_argument(
        '--skip-consolidate',
        action='store_true',
        help='Skip consolidation step (use if already consolidated)'
    )
    parser.add_argument(
        '--skip-improve',
        action='store_true',
        help='Skip portfolio improvement step'
    )
    parser.add_argument(
        '--skip-push',
        action='store_true',
        help='Skip GitHub push step'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Date override in YYYYMMDD format (default: today)'
    )
    parser.add_argument(
        '--push-only',
        action='store_true',
        help='Only push existing changes to GitHub (skip all other steps)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print_lg("\n" + "="*80)
    print_lg("QUANT JOB CATALOGING & PORTFOLIO IMPROVEMENT - DAILY WORKFLOW")
    print_lg("="*80)
    
    target_date = args.date if args.date else date.today().strftime('%Y%m%d')
    print_lg(f"\nTarget Date: {target_date}")
    print_lg(f"Current Date: {date.today().strftime('%Y-%m-%d')}\n")
    
    # Push-only mode
    if args.push_only:
        print_lg("Mode: Push-only (skipping all other steps)")
        return push_to_github()
    
    # Step 1: Consolidate today's JDs
    consolidate_success = True
    if not args.skip_consolidate:
        print_lg("\n" + "="*80)
        print_lg("STEP 1: Consolidating Today's Job Descriptions")
        print_lg("="*80)
        
        consolidate_args = []
        if args.date:
            # Note: consolidate_today_jds.py doesn't have date override yet
            # This would need to be added if needed
            pass
        
        consolidate_success = run_script("consolidate_today_jds", consolidate_args)
        
        if not consolidate_success:
            print_lg("\n[WARNING] Consolidation failed, but continuing workflow...")
    else:
        print_lg("\n[SKIPPED] Step 1: Consolidation (--skip-consolidate flag set)")
        # Check if consolidated CSV exists
        if not check_consolidated_csv_exists(target_date):
            print_lg(f"[WARNING] Consolidated CSV not found for date {target_date}")
            print_lg("         Portfolio improvement step may fail.")
    
    # Step 2: Improve portfolio from today's JDs
    improve_success = True
    if not args.skip_improve:
        print_lg("\n" + "="*80)
        print_lg("STEP 2: Improving Portfolio Repository")
        print_lg("="*80)
        
        improve_args = []
        if args.date:
            improve_args.extend(['--date', args.date])
        
        improve_success = run_script("improve_portfolio_from_today", improve_args)
        
        if not improve_success:
            print_lg("\n[WARNING] Portfolio improvement failed, but continuing workflow...")
    else:
        print_lg("\n[SKIPPED] Step 2: Portfolio Improvement (--skip-improve flag set)")
    
    # Step 3: Push to GitHub
    push_success = True
    if not args.skip_push:
        print_lg("\n" + "="*80)
        print_lg("STEP 3: Pushing Changes to GitHub")
        print_lg("="*80)
        
        push_success = push_to_github()
        
        if not push_success:
            print_lg("\n[WARNING] GitHub push failed or was skipped")
    else:
        print_lg("\n[SKIPPED] Step 3: GitHub Push (--skip-push flag set)")
    
    # Summary
    print_lg("\n" + "="*80)
    print_lg("WORKFLOW SUMMARY")
    print_lg("="*80)
    
    steps = []
    if not args.skip_consolidate:
        steps.append(("Consolidation", consolidate_success))
    if not args.skip_improve:
        steps.append(("Portfolio Improvement", improve_success))
    if not args.skip_push:
        steps.append(("GitHub Push", push_success))
    
    for step_name, success in steps:
        status = "[SUCCESS]" if success else "[FAILED]"
        print_lg(f"  {status} {step_name}")
    
    print_lg("\n" + "="*80)
    print_lg("Daily workflow complete!")
    print_lg("="*80 + "\n")
    
    # Return overall success
    all_success = all(success for _, success in steps) if steps else False
    return all_success


def push_to_github() -> bool:
    """
    Push portfolio repository changes to GitHub.
    
    Returns:
        True if push was successful or skipped, False on error
    """
    try:
        from config.settings import quant_poc_repo_path
        
        if not quant_poc_repo_path or not os.path.exists(quant_poc_repo_path):
            print_lg("[SKIPPED] Portfolio repository path not configured or doesn't exist")
            return True
        
        repo_path = Path(quant_poc_repo_path)
        
        # Check if there are any changes to push
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print_lg("[SKIPPED] Not a git repository or git error")
                return True
            
            # Check if ahead of remote
            result = subprocess.run(
                ['git', 'status', '--short', '--branch'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if 'ahead' not in result.stdout:
                print_lg("[INFO] No commits to push (repository is up to date)")
                return True
            
            # Push to remote
            print_lg("Pushing changes to GitHub...")
            result = subprocess.run(
                ['git', 'push', 'origin', 'main'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print_lg("[SUCCESS] Changes pushed to GitHub successfully")
                return True
            else:
                print_lg(f"[ERROR] Git push failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print_lg("[ERROR] Git operation timed out")
            return False
        except Exception as e:
            print_lg(f"[ERROR] Failed to push to GitHub: {e}")
            return False
            
    except Exception as e:
        print_lg(f"[ERROR] Error checking repository: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
