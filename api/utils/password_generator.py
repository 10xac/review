import random
import string
from typing import Optional

def generate_secure_password(length: int = 12) -> str:
    """
    Generate a secure password with the specified length.
    The password will include:
    - Uppercase letters
    - Lowercase letters
    - Numbers
    - Special characters
    
    Args:
        length (int): Length of the password (default: 12)
    
    Returns:
        str: Generated secure password
    """
    # Define character sets
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    numbers = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Ensure at least one character from each set
    password = [
        random.choice(uppercase),
        random.choice(lowercase),
        random.choice(numbers),
        random.choice(special)
    ]
    
    # Fill the rest of the password with random characters from all sets
    all_chars = uppercase + lowercase + numbers + special
    password.extend(random.choice(all_chars) for _ in range(length - 4))
    
    # Shuffle the password to make it more random
    random.shuffle(password)
    
    return ''.join(password) 