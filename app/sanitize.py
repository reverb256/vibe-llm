import re

def sanitize_input(text):
    # Remove dangerous shell characters and limit length
    text = re.sub(r'[;&|`$<>]', '', text)
    return text[:10000]
