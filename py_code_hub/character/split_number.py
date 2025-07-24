import random


def split(number):
    divisor = 1000
    quotient = number // divisor
    remainder = number % divisor
    print(f" {number} -> {quotient * divisor} -> {remainder} ")


split(120)
split(895)
split(111)
split(123)
split(436)
split(100)
split(150)
split(50)
split(30)
split(2)
split(1020)
split(1120)

print(f"{25:03}")
print(f"{25:03}")
print(f"{1000:03}")
print(f"{99:00}")
print(f"{1:00}")
print(f"{5:00}")


def split_number_math(num: int):
    parts = []

    last_two = num % 100  # last two digits
    leading = num // 100  # remaining part

    # Process leading part digits
    place = 1
    while place <= leading:
        place *= 10
    place //= 10

    while place > 0:
        digit = leading // place
        if digit != 0:
            parts.append(digit * place * 100)
        leading %= place
        place //= 10

    # Add last two digits if not zero
    if last_two != 0:
        parts.append(last_two)

    # If parts empty (like num < 100), return num as is
    if not parts:
        return [num]

    return parts


print("\n\n--------------------")
print(split_number_math(121))
print(split_number_math(20))
print(split_number_math(1001))
print(split_number_math(1012))
print(split_number_math(1100))
print(split_number_math(800))
print(split_number_math(836))
print(split_number_math(10123))

print("\n\n=====")


def split(number: int):
    divisor = 10
    quotient = number // divisor
    remainder = number % divisor
    print(f" {number} -> {quotient * divisor} -> {remainder} ")


split(100)
split(895)
split(111)
split(1110)
split(29)


def extract_number(num):
    if num < 100:
        return [num]
    elif num < 1000:
        if num % 100 == 0:
            return [num]
        else:
            return [(num // 100) * 100, num % 100]
    else:  # num >= 1000
        if num % 1000 == 0:
            return [num]
        else:
            result = []
            thousands = (num // 1000) * 1000
            if thousands > 0:
                result.append(thousands)

            remainder_hundreds = num % 1000
            hundreds = (remainder_hundreds // 100) * 100
            if hundreds > 0:
                result.append(hundreds)
            remainder_tens_ones = remainder_hundreds % 100
            if remainder_tens_ones > 0:
                result.append(remainder_tens_ones)
            return result

# Example usage:
print(f"1 >> {extract_number(1.1)}")
print(f"29 >> {extract_number(29.2)}")
print(f"100 >> {extract_number(100)}")
print(f"200 >> {extract_number(200)}")
print(f"300 >> {extract_number(300)}")
print(f"111 >> {extract_number(111)}")
print(f"112 >> {extract_number(112)}")
print(f"113 >> {extract_number(113)}")
print(f"999 >> {extract_number(999)}")
print(f"1000 >> {extract_number(1000)}")
print(f"1212 >> {extract_number(1212)}")
print(f"1356 >> {extract_number(1356)}")


print("\n\n---------------------------------------")
print("Final")
print("---------------------------------------")


def number_to_fragment(number):
    if isinstance(number, str) and not number.isdigit():
        return None
    elif isinstance(number, str):
        number = float(number)
        number = int(number)
    elif isinstance(number, float):
        number = int(number)

    response = None
    if number < 100:
        response = [number]
    elif number < 1000:
        if number % 100 == 0:
            response = [number]
        else:
            response = [(number // 100) * 100, number % 100]
    else:
        if number % 1000 == 0:
            response = [number]
        else:
            response = []

            thousands = (number // 1000) * 1000
            if thousands > 0:
                response.append(thousands)

            remainder_hundreds = number % 1000
            hundreds = (remainder_hundreds // 100) * 100
            if hundreds > 0:
                response.append(hundreds)

            remainder_tens_ones = remainder_hundreds % 100
            if remainder_tens_ones > 0:
                response.append(remainder_tens_ones)

    print(f"number: {number} >> {response}")


for index in range(0, 205):
    number = random.randint(1, 999)
    number_to_fragment(number)
