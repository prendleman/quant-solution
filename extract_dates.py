#!/usr/bin/env python3
"""
Date Extractor Script
Finds specific dates from resume text
"""

import os
import re
import pdfplumber

def extract_dates_from_pdf(pdf_path):
    """Extract all dates from PDF"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        print("Extracted text from PDF successfully")
        print("=" * 50)
        print("FULL TEXT FROM RESUME:")
        print("=" * 50)
        print(text)
        print("=" * 50)
        
        # Look for various date patterns
        date_patterns = [
            r'\b(19|20)\d{2}\b',  # Years
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',  # Month Year
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',  # YYYY/MM/DD
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',  # Full month names
        ]
        
        all_dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            all_dates.extend(matches)
        
        # Remove duplicates and sort
        unique_dates = list(set(all_dates))
        unique_dates.sort()
        
        print(f"\nFOUND {len(unique_dates)} DATE(S):")
        print("-" * 30)
        for i, date in enumerate(unique_dates, 1):
            print(f"{i}. {date}")
        
        # Look for education section specifically
        print(f"\nEDUCATION SECTION ANALYSIS:")
        print("-" * 30)
        
        # Split text into lines and look for education-related content
        lines = text.split('\n')
        education_lines = []
        
        for i, line in enumerate(lines):
            if any(word in line.lower() for word in ['education', 'university', 'college', 'degree', 'bachelor', 'master', 'phd', 'shimer']):
                education_lines.append(f"Line {i+1}: {line.strip()}")
        
        if education_lines:
            print("Education-related lines found:")
            for line in education_lines:
                print(line)
        else:
            print("No education section clearly identified")
        
        return unique_dates, text
        
    except Exception as e:
        print(f"ERROR: Failed to extract dates: {e}")
        return [], ""

def main():
    """Main function to extract dates from resume"""
    print("Date Extractor - Finding College Dates")
    print("=" * 50)
    
    # Path to resume
    resume_path = os.path.join(os.path.dirname(__file__), 'all resumes', 'default', 'resume.pdf')
    
    if not os.path.exists(resume_path):
        print(f"ERROR: Resume not found at: {resume_path}")
        return
    
    print(f"Found resume: {resume_path}")
    
    # Extract dates
    dates, full_text = extract_dates_from_pdf(resume_path)
    
    if dates:
        print(f"\nRECOMMENDED COLLEGE DATES:")
        print("-" * 30)
        print("Based on the dates found, here are likely candidates:")
        print("Start Date: Look for the earliest date (likely 2018-2020)")
        print("End Date: Look for the most recent date (likely 2022-2024)")
        print("\nPlease review the dates above and let me know which ones are correct!")

if __name__ == "__main__":
    main()
