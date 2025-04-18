def number_to_excel_column(index: int, start_column="A") -> str:
    result = ""
    start_ascii_number = ord(start_column)
    while index > 0:
        index -= 1  # Adjust to 0-indexed
        result = chr(start_ascii_number + (index % 26)) + result
        index //= 26

    return result


print(number_to_excel_column(index=1))
print(number_to_excel_column(index=26))
print(number_to_excel_column(index=27))
print(number_to_excel_column(index=55))
print(number_to_excel_column(index=710))
