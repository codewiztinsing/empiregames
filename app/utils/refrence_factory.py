import uuid
import random
import string
import time
    

def generate_reference():

    # Get current timestamp for uniqueness
    timestamp = str(int(time.time()))
    
    # Define character sets
    letters = string.ascii_letters  # a-z, A-Z
    digits = string.digits  # 0-9
    symbols = "!@#$%&*+-="
    
    # Combine all character sets
    all_chars = letters + digits + symbols
    
    # Generate random part (12 characters)
    random_part = ''.join(random.choice(all_chars) for _ in range(12))
    
    # Combine timestamp and random part with separator
    reference = f"REF_{timestamp}_{random_part}"
    
    return reference



