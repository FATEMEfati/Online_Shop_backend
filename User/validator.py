from django.core.validators import RegexValidator
import re

iran_phone_regex = RegexValidator(
    regex=r"^(\+98|0)?9\d{9}$",
    message="Phone number must be entered in the format: '+989xxxxxxxxx' or '09xxxxxxxxx'.",
)

def is_valid_password(password):
    """
    Validate a password based on specified criteria.

    The password must meet the following requirements:
    - At least 8 characters long.
    - Contains at least one uppercase letter.
    - Contains at least one lowercase letter.
    - Contains at least one digit.
    - Contains at least one special character (e.g., !@#$%^&*(),.?":{}|<>).

    Args:
        password (str): The password to be validated.

    Returns:
        tuple: A tuple containing a boolean indicating the validity of the password
               and a message explaining the result.
               - (True, "Password is valid.") if the password meets all criteria.
               - (False, message) if the password fails to meet any of the criteria.
    """

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit."

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."

    return True, "Password is valid."