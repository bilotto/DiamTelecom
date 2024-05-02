import re

def is_valid_msisdn(msisdn: str) -> bool:
    # Add your MSISDN validation logic here
    # For example, you can use a regular expression
    pattern = r"^\d{10}$"  # Assuming MSISDN is a 10-digit number
    return re.match(pattern, msisdn) is not None

def is_valid_imsi(imsi: str) -> bool:
    # Add your IMSI validation logic here
    # For example, you can use a regular expression
    pattern = r"^\d{15}$"  # Assuming IMSI is a 15-digit number
    return re.match(pattern, imsi) is not None