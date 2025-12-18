#!/usr/bin/env python3
"""
Consolidate Today's Job Descriptions
Reads the quant_jobs_catalog.csv file and creates a consolidated document
with all job descriptions from today.
"""

import csv
import os
from datetime import datetime, date
from pathlib import Path

def parse_date(date_str):
    """
    Parse date from various formats that might be in the CSV.
    Handles datetime objects converted to strings, date strings, etc.
    """
    if not date_str or date_str == "Unknown" or date_str.strip() == "":
        return None
    
    date_str = str(date_str).strip()
    
    # Try parsing as datetime string (format: YYYY-MM-DD HH:MM:SS or similar)
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y-%m-%d %H:%M:%S.%f',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.date()
        except ValueError:
            continue
    
    # If all parsing fails, return None
    return None

def consolidate_today_jds():
    """
    Main function to consolidate all job descriptions from today.
    """
    # Get the path to the catalog file
    script_dir = Path(__file__).parent
    catalog_file = script_dir / "all excels" / "quant_jobs_catalog.csv"
    
    if not catalog_file.exists():
        print(f"Error: Catalog file not found at {catalog_file}")
        return
    
    # Get today's date
    today = date.today()
    print(f"Looking for jobs posted on: {today.strftime('%Y-%m-%d')}")
    print("=" * 80)
    
    # Read the CSV and filter for today's jobs
    today_jobs = []
    total_jobs = 0
    
    try:
        with open(catalog_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                total_jobs += 1
                date_posted_str = row.get('Date Posted', '').strip()
                
                # Parse the date
                job_date = parse_date(date_posted_str)
                
                if job_date == today:
                    today_jobs.append(row)
                    print(f"Found job: {row.get('Title', 'Unknown')} at {row.get('Company', 'Unknown')}")
    
    except Exception as e:
        print(f"Error reading catalog file: {e}")
        return
    
    print(f"\nTotal jobs in catalog: {total_jobs}")
    print(f"Jobs posted today: {len(today_jobs)}")
    print("=" * 80)
    
    if len(today_jobs) == 0:
        print("No jobs found for today. The consolidation document will not be created.")
        return
    
    # Create consolidated document
    output_dir = script_dir / "all excels"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"consolidated_jds_{today.strftime('%Y%m%d')}.md"
    
    # Write consolidated markdown document
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Consolidated Job Descriptions - {today.strftime('%B %d, %Y')}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Jobs:** {len(today_jobs)}\n\n")
        f.write("---\n\n")
        
        for i, job in enumerate(today_jobs, 1):
            f.write(f"## Job {i}: {job.get('Title', 'Unknown Title')}\n\n")
            f.write(f"**Company:** {job.get('Company', 'Unknown')}\n\n")
            f.write(f"**Location:** {job.get('Work Location', 'Unknown')}\n\n")
            f.write(f"**Work Style:** {job.get('Work Style', 'Unknown')}\n\n")
            f.write(f"**Experience Required:** {job.get('Experience required', 'Unknown')}\n\n")
            
            skills = job.get('Skills required', 'Not extracted')
            if skills and skills != 'Not extracted' and skills != 'Unknown':
                f.write(f"**Skills Required:** {skills}\n\n")
            
            f.write(f"**Job Link:** {job.get('Job Link', 'Unknown')}\n\n")
            
            recruiter_name = job.get('Recruiter Name', 'Unknown')
            recruiter_link = job.get('Recruiter Link', 'Unknown')
            if recruiter_name != 'Unknown' and recruiter_link != 'Unknown':
                f.write(f"**Recruiter:** [{recruiter_name}]({recruiter_link})\n\n")
            
            f.write(f"**Date Posted:** {job.get('Date Posted', 'Unknown')}\n\n")
            
            # Job Description
            description = job.get('Job Description', 'No description available')
            if description and description != 'Unknown':
                f.write("### Job Description\n\n")
                # Clean up the description (remove excessive newlines)
                description = description.replace('\r\n', '\n').replace('\r', '\n')
                # Limit consecutive newlines to 2
                while '\n\n\n' in description:
                    description = description.replace('\n\n\n', '\n\n')
                f.write(description)
                f.write("\n\n")
            else:
                f.write("### Job Description\n\n*No description available*\n\n")
            
            f.write("---\n\n")
    
    print(f"\n[SUCCESS] Consolidated document created: {output_file}")
    print(f"  Contains {len(today_jobs)} job descriptions from today.")
    
    # Also create a summary CSV with just today's jobs
    summary_csv = output_dir / f"today_jobs_summary_{today.strftime('%Y%m%d')}.csv"
    with open(summary_csv, 'w', newline='', encoding='utf-8') as f:
        if today_jobs:
            fieldnames = today_jobs[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(today_jobs)
    
    print(f"[SUCCESS] Summary CSV created: {summary_csv}")

if __name__ == "__main__":
    consolidate_today_jds()
