import secrets

def generate_barcode(length=12):
    return ''.join(str(secrets.randbelow(10)) for _ in range(length))

CHARS = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"

def generate_registration_code(length=8):
    return ''.join(secrets.choice(CHARS) for _ in range(length))

contain = []
for _ in range(10000):
    code = generate_registration_code()
    if code in contain:
        print(f"duplicate {code}")
    else:
        contain.append(code)
    print(code)