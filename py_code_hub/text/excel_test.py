
def number_to_column(index: int, start_column="A", minus_index=1) -> str:
    result = ""
    start_ascii_number = ord(start_column)

    while index > 0:
        # only adjust if minus_index is a valid int and nonzero
        if isinstance(minus_index, int) and minus_index:
            index -= minus_index

        index, remainder = divmod(index, 26)
        result = chr(start_ascii_number + remainder) + result

    return result or start_column


def number_to_column2(index: int, start_column="A", minus_index=1) -> str:
    if index < 1:
        return start_column

    # Adjust for 1-based indexing
    if minus_index:
        index -= minus_index

    result = ""
    start_ascii = ord(start_column)

    while index >= 0:
        result = chr(start_ascii + (index % 26)) + result
        index = (index // 26) - 1

    return result or start_column


print(number_to_column2(index=53, minus_index=0))
print(number_to_column2(index=90, minus_index=0))