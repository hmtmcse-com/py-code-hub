import re

def is_valid_local_bd_mobile(number: str) -> bool:
    BD_LOCAL_MOBILE_REGEX = re.compile(r"^01[3-9]\d{8}$")
    return bool(BD_LOCAL_MOBILE_REGEX.match(number.strip()))


# ---- Examples ----
tests = [
    "01712345678",   # ✅ valid
    "01399999999",   # ✅ valid
    "01987654321",   # ✅ valid
    "01112345678",   # ❌ invalid (011 not used)
    "+8801712345678",# ❌ invalid (intl format)
    "1712345678",    # ❌ missing '0'
    "01712-345678",  # ❌ contains separator
    "0171234567",    # ❌ too short
]

for t in tests:
    print(t, "=>", is_valid_local_bd_mobile(t))
