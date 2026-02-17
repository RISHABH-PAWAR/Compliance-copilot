"""Input Validators"""
import re

def validate_email(email: str) -> bool:
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

def validate_phone(phone: str) -> bool:
    return bool(re.match(r'^[+]?[0-9]{10,15}$', phone.replace(" ", "")))

def validate_gstin(gstin: str) -> bool:
    return bool(re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', gstin))

def validate_pan(pan: str) -> bool:
    return bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan))
