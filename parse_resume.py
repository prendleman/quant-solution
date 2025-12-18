#!/usr/bin/env python3
"""
Resume Parser Script
Extracts college/education information from PDF resume
"""

import os
import re
import PyPDF2
import pdfplumber
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using multiple methods"""
    text = ""
    
    # Method 1: Try pdfplumber (better for complex layouts)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        print("SUCCESS: Successfully extracted text using pdfplumber")
        return text
    except Exception as e:
        print(f"ERROR: pdfplumber failed: {e}")
    
    # Method 2: Try PyPDF2 (fallback)
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        print("SUCCESS: Successfully extracted text using PyPDF2")
        return text
    except Exception as e:
        print(f"ERROR: PyPDF2 failed: {e}")
    
    return ""

def extract_college_info(text):
    """Extract college information from resume text"""
    college_info = {
        'college_name': '',
        'college_start_date': '',
        'college_end_date': '',
        'college_degree': '',
        'college_major': ''
    }
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Extract college/university name
    college_patterns = [
        r'(university of [^,\n]+)',
        r'([^,\n]+ university)',
        r'([^,\n]+ college)',
        r'([^,\n]+ institute)',
        r'([^,\n]+ school)'
    ]
    
    for pattern in college_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            college_info['college_name'] = matches[0].strip()
            break
    
    # Extract degree information
    degree_patterns = [
        r'(bachelor of [^,\n]+)',
        r'(master of [^,\n]+)',
        r'(phd in [^,\n]+)',
        r'(doctor of [^,\n]+)',
        r'(associate of [^,\n]+)',
        r'(b\.s\. in [^,\n]+)',
        r'(m\.s\. in [^,\n]+)',
        r'(b\.a\. in [^,\n]+)',
        r'(m\.a\. in [^,\n]+)'
    ]
    
    for pattern in degree_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            college_info['college_degree'] = matches[0].strip()
            break
    
    # Extract major/field of study
    major_patterns = [
        r'(computer science)',
        r'(engineering)',
        r'(business administration)',
        r'(mathematics)',
        r'(physics)',
        r'(chemistry)',
        r'(biology)',
        r'(psychology)',
        r'(economics)',
        r'(finance)',
        r'(marketing)',
        r'(accounting)'
    ]
    
    for pattern in major_patterns:
        if re.search(pattern, text_lower):
            college_info['college_major'] = pattern.title()
            break
    
    # Extract dates (look for years)
    year_pattern = r'\b(19|20)\d{2}\b'
    years = re.findall(year_pattern, text)
    
    if years:
        years = [int(year) for year in years if 1950 <= int(year) <= 2030]
        if len(years) >= 2:
            years.sort()
            college_info['college_start_date'] = str(years[0])
            college_info['college_end_date'] = str(years[-1])
        elif len(years) == 1:
            college_info['college_end_date'] = str(years[0])
    
    return college_info

def update_config_file(college_info):
    """Update the questions.py config file with extracted college info"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'questions.py')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Update each college variable
        updates = {
            'college_name': college_info['college_name'] or 'Your College Name',
            'college_start_date': college_info['college_start_date'] or '2018',
            'college_end_date': college_info['college_end_date'] or '2022',
            'college_degree': college_info['college_degree'] or 'Bachelor of Science',
            'college_major': college_info['college_major'] or 'Computer Science'
        }
        
        for key, value in updates.items():
            # Escape quotes in the value
            escaped_value = value.replace('"', '\\"')
            pattern = rf'{key} = "[^"]*"'
            replacement = f'{key} = "{escaped_value}"'
            content = re.sub(pattern, replacement, content)
        
        with open(config_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"SUCCESS: Updated config file: {config_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to update config file: {e}")
        return False

def main():
    """Main function to parse resume and update config"""
    print("Resume Parser - Extracting College Information")
    print("=" * 50)
    
    # Path to resume
    resume_path = os.path.join(os.path.dirname(__file__), 'all resumes', 'default', 'resume.pdf')
    
    if not os.path.exists(resume_path):
        print(f"X Resume not found at: {resume_path}")
        return
    
    print(f"Found resume: {resume_path}")
    
    # Extract text from PDF
    text = extract_text_from_pdf(resume_path)
    
    if not text:
        print("X Could not extract text from PDF")
        return
    
    print(f"Extracted {len(text)} characters of text")
    
    # Extract college information
    college_info = extract_college_info(text)
    
    print("\nExtracted College Information:")
    print("-" * 30)
    for key, value in college_info.items():
        print(f"{key}: {value if value else 'Not found'}")
    
    # Update config file
    print(f"\nUpdating configuration...")
    if update_config_file(college_info):
        print("SUCCESS: Configuration updated successfully!")
        print("\nYour bot is now configured with your actual college information!")
    else:
        print("ERROR: Failed to update configuration")

if __name__ == "__main__":
    main()
