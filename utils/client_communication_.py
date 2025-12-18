"""
Module: client_communication

This module provides functions for client communication in a quantitative finance portfolio.

Functions:
- send_email: Sends an email to the client with the provided message.
- generate_report: Generates a financial analysis report for the client.

Usage:
Example usage of send_email and generate_report functions in the __main__ block.
"""

from typing import List
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject: str, message: str, recipient: str, sender_email: str, sender_password: str) -> None:
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

def generate_report(data: List[float]) -> str:
    try:
        # Perform financial analysis and modeling on the data
        report = "Financial Analysis Report:\n"
        # Add analysis results to the report
        return report
    except Exception as e:
        return f"An error occurred during report generation: {e}"

if __name__ == "__main__":
    # Example usage of send_email function
    send_email("Portfolio Update", "Your portfolio has been updated successfully.", "client@example.com", "sender@gmail.com", "password")

    # Example usage of generate_report function
    data = [100, 150, 200, 250, 300]
    report = generate_report(data)
    print(report)