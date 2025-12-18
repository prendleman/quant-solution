"""
Module: SWIFTPortfolio
This module contains functions for managing a quantitative finance portfolio using SWIFT messaging.
"""

from typing import List, Dict
import r
import SWIFT
import ISO20022
import ACH

def send_swift_message(message: str, recipient: str) -> bool:
    """
    Sends a SWIFT message to the specified recipient.
    
    Args:
    message: The message to be sent
    recipient: The recipient's SWIFT address
    
    Returns:
    bool: True if the message was successfully sent, False otherwise
    """
    try:
        SWIFT.send_message(message, recipient)
        return True
    except SWIFT.SWIFTError:
        return False

def generate_iso20022_message(data: Dict[str, str]) -> str:
    """
    Generates an ISO 20022 message based on the provided data.
    
    Args:
    data: A dictionary containing the data for the message
    
    Returns:
    str: The generated ISO 20022 message
    """
    return ISO20022.generate_message(data)

def process_ach_payment(amount: float, recipient: str) -> bool:
    """
    Processes an ACH payment to the specified recipient.
    
    Args:
    amount: The amount to be paid
    recipient: The recipient's ACH account number
    
    Returns:
    bool: True if the payment was successfully processed, False otherwise
    """
    try:
        ACH.process_payment(amount, recipient)
        return True
    except ACH.ACHError:
        return False

if __name__ == "__main__":
    # Example usage
    message = "Buy 100 shares of AAPL"
    recipient = "BICXYZ123"
    if send_swift_message(message, recipient):
        print("SWIFT message sent successfully")
    else:
        print("Failed to send SWIFT message")
    
    data = {"transaction_id": "12345", "amount": "1000", "currency": "USD"}
    iso_message = generate_iso20022_message(data)
    print("Generated ISO 20022 message:", iso_message)
    
    amount = 500.0
    ach_recipient = "123456789"
    if process_ach_payment(amount, ach_recipient):
        print("ACH payment processed successfully")
    else:
        print("Failed to process ACH payment")