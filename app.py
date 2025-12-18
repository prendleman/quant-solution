from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import csv
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

PATH = 'all excels/'

##> ------ Updated for Quant Job Cataloging ------
@app.route('/')
def home():
    """Displays the home page of the application."""
    return render_template('index.html')

@app.route('/cataloged-jobs', methods=['GET'])
def get_cataloged_jobs():
    '''
    Retrieves a list of cataloged quant jobs from the jobs catalog CSV file.
    
    Returns a JSON response containing a list of jobs with details such as 
    Job ID, Title, Company, Work Location, Work Style, Job Description, 
    Recruiter Name, Recruiter Link, Connection Status, and Date Posted.
    
    If the CSV file is not found, returns a 404 error with a relevant message.
    If any other exception occurs, returns a 500 error with the exception message.
    '''
    try:
        jobs = []
        csvPath = PATH + 'quant_jobs_catalog.csv'
        
        if not os.path.exists(csvPath):
            return jsonify({"error": "No jobs catalog found"}), 404
        
        with open(csvPath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                jobs.append({
                    'Job_ID': row.get('Job ID', ''),
                    'Title': row.get('Title', ''),
                    'Company': row.get('Company', ''),
                    'Work_Location': row.get('Work Location', ''),
                    'Work_Style': row.get('Work Style', ''),
                    'Job_Description': row.get('Job Description', ''),
                    'Experience_Required': row.get('Experience required', ''),
                    'Skills_Required': row.get('Skills required', ''),
                    'Recruiter_Name': row.get('Recruiter Name', ''),
                    'Recruiter_Link': row.get('Recruiter Link', ''),
                    'Recruiter_Title': row.get('Recruiter Title', ''),
                    'Recruiter_Company': row.get('Recruiter Company', ''),
                    'Date_Posted': row.get('Date Posted', ''),
                    'Job_Link': row.get('Job Link', ''),
                    'Connection_Status': row.get('Connection Status', 'Not Connected'),
                    'Connection_Date': row.get('Connection Date', '')
                })
        return jsonify(jobs)
    except FileNotFoundError:
        return jsonify({"error": "No jobs catalog found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recruiters', methods=['GET'])
def get_recruiters():
    '''
    Retrieves a list of cataloged recruiters from the recruiters catalog CSV file.
    
    Returns a JSON response containing a list of recruiters with details such as 
    Recruiter Name, Recruiter Link, Recruiter Title, Recruiter Company, 
    Jobs Posted, First Contact Date, Connection Status, and Last Message Date.
    '''
    try:
        recruiters = []
        csvPath = PATH + 'recruiters_catalog.csv'
        
        if not os.path.exists(csvPath):
            return jsonify({"error": "No recruiters catalog found"}), 404
        
        with open(csvPath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                recruiters.append({
                    'Recruiter_Name': row.get('Recruiter Name', ''),
                    'Recruiter_Link': row.get('Recruiter Link', ''),
                    'Recruiter_Title': row.get('Recruiter Title', ''),
                    'Recruiter_Company': row.get('Recruiter Company', ''),
                    'Jobs_Posted': row.get('Jobs Posted', ''),
                    'First_Contact_Date': row.get('First Contact Date', ''),
                    'Connection_Status': row.get('Connection Status', 'Not Connected'),
                    'Last_Message_Date': row.get('Last Message Date', ''),
                    'Notes': row.get('Notes', '')
                })
        return jsonify(recruiters)
    except FileNotFoundError:
        return jsonify({"error": "No recruiters catalog found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cataloged-jobs/<job_id>', methods=['PUT'])
def update_connection_status(job_id):
    """
    Updates the connection status of a job in the jobs catalog CSV file.

    Args:
        job_id (str): The Job ID of the job to be updated.

    Returns:
        A JSON response with a message indicating success or failure of the update
        operation. If the job is not found, returns a 404 error with a relevant
        message. If any other exception occurs, returns a 500 error with the
        exception message.
    """
    try:
        data = []
        csvPath = PATH + 'quant_jobs_catalog.csv'
        
        if not os.path.exists(csvPath):
            return jsonify({"error": f"CSV file not found at {csvPath}"}), 404
        
        request_data = request.get_json()
        connection_status = request_data.get('Connection_Status', '')
        connection_date = request_data.get('Connection_Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
        # Read current CSV content
        with open(csvPath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldNames = reader.fieldnames
            found = False
            for row in reader:
                if row.get('Job ID') == job_id:
                    if connection_status:
                        row['Connection Status'] = connection_status
                    if connection_date:
                        row['Connection Date'] = connection_date
                    found = True
                data.append(row)
        
        if not found:
            return jsonify({"error": f"Job ID {job_id} not found"}), 404

        with open(csvPath, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldNames)
            writer.writeheader()
            writer.writerows(data)
        
        return jsonify({"message": "Connection status updated successfully"}), 200
    except Exception as e:
        print(f"Error updating connection status: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Legacy route for backward compatibility
@app.route('/applied-jobs', methods=['GET'])
def get_applied_jobs():
    '''Legacy route - redirects to cataloged-jobs'''
    return get_cataloged_jobs()
##<

if __name__ == '__main__':
    app.run(debug=True)

##<