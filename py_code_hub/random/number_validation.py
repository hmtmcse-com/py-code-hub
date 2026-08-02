

import re

def is_valid_sg_number(phone: str) -> bool:
    """
    Validates Singapore phone numbers.
    Supports:
    - 8-digit local numbers
    - With or without +65 country code
    """
    pattern = re.compile(r'^(?:\+65|65)?[689]\d{7}$')
    return bool(pattern.match(phone))


numbers = [
    "80265647",
]

for n in numbers:
    print(n, is_valid_sg_number(n))