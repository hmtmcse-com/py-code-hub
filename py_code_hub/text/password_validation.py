def validate_basic(password: str):
    forbidden = ["admin", "manager"]

    number_password = ""
    zero_number_password = ""
    for index in range(len(password)):
        number_password += f"{index + 1}"
        zero_number_password += f"{index}"

    forbidden.append(number_password)
    forbidden.append(zero_number_password)

    if password.lower() in forbidden:
        print(f"Password is forbidden. {password}")
        return False
    return True


print(validate_basic("admin"))
print(validate_basic("1234"))
print(validate_basic("manager"))