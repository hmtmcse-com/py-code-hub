import xlsxwriter

workbook = xlsxwriter.Workbook("cell_operations.xlsx")
ws = workbook.add_worksheet("Cells")

# Simple formats
bold = workbook.add_format({"bold": True})
center = workbook.add_format({"align": "center", "valign": "vcenter", "border": 1})
yellow = workbook.add_format({"bg_color": "yellow", "border": 1})
money = workbook.add_format({"num_format": "#,##0.00"})
date_fmt = workbook.add_format({"num_format": "dd-mmm-yyyy"})

########################################################################
# 1. Write data into cells
########################################################################

ws.write("A1", "Hello")
ws.write("A2", "World")

ws.write_number("A3", 12345)
ws.write_number("A4", 99.99)

ws.write_boolean("A5", True)

ws.write_blank("A6", None)

########################################################################
# 2. Write using row/column indexes
########################################################################

ws.write(0, 2, "C1")
ws.write(1, 2, "C2")
ws.write(2, 2, "C3")

########################################################################
# 3. Left / Right / Up / Down
########################################################################

# Center cell
ws.write("E5", "Center", bold)

# Left
ws.write("D5", "Left")

# Right
ws.write("F5", "Right")

# Up
ws.write("E4", "Up")

# Down
ws.write("E6", "Down")

########################################################################
# 4. Merge cells
########################################################################

ws.merge_range("A8:D9", "Merged Cell", center)

########################################################################
# 5. Different data types
########################################################################

ws.write_string("A11", "Text")
ws.write_number("B11", 500)
ws.write_formula("C11", "=B11*2")
ws.write_url("D11", "https://python.org", string="Python")
ws.write_datetime("E11", __import__("datetime").datetime.now(), date_fmt)

########################################################################
# 6. Row operations
########################################################################

ws.set_row(12, 30)
ws.write("A13", "Tall Row")

########################################################################
# 7. Column operations
########################################################################

ws.set_column("A:A", 25)
ws.set_column("B:D", 15)

########################################################################
# 8. Insert row manually (write below existing)
########################################################################

ws.write("A15", "Row 15")
ws.write("A16", "Row 16")
ws.write("A17", "Row 17")

########################################################################
# 9. Relative positioning
########################################################################

row = 20
col = 2

ws.write(row, col, "Current")
ws.write(row, col + 1, "Right")
ws.write(row, col - 1, "Left")
ws.write(row - 1, col, "Up")
ws.write(row + 1, col, "Down")

########################################################################
# 10. Write a row
########################################################################

ws.write_row("A23", [
    "ID",
    "Name",
    "Age",
    "Salary"
], bold)

########################################################################
# 11. Write a column
########################################################################

ws.write_column("F23", [
    "Apple",
    "Banana",
    "Orange",
    "Mango"
])

########################################################################
# 12. Rich text
########################################################################

red = workbook.add_format({"font_color": "red"})
blue = workbook.add_format({"font_color": "blue"})

ws.write_rich_string(
    "A30",
    red, "Red ",
    blue, "Blue ",
    "Normal"
)

########################################################################
# 13. Cell comments
########################################################################

ws.write("A32", "Hover Me")
ws.write_comment("A32", "This is a comment")

########################################################################
# 14. Cell formatting
########################################################################

ws.write("A34", "Yellow Cell", yellow)

########################################################################
# 15. Formula referencing nearby cells
########################################################################

ws.write("A36", 100)
ws.write("B36", 50)
ws.write_formula("C36", "=A36+B36")
ws.write_formula("D36", "=A36-B36")
ws.write_formula("E36", "=A36*B36")
ws.write_formula("F36", "=A36/B36")

########################################################################
# 16. Freeze pane
########################################################################

ws.freeze_panes(1, 1)

########################################################################
# 17. Autofilter
########################################################################

ws.write_row("A40", ["ID", "Name", "Age"])
ws.write_row("A41", [1, "John", 20])
ws.write_row("A42", [2, "Alice", 22])
ws.write_row("A43", [3, "Bob", 21])

ws.autofilter("A40:C43")

########################################################################
# 18. Data Validation
########################################################################

ws.data_validation(
    "E40",
    {
        "validate": "list",
        "source": ["Male", "Female"]
    }
)

########################################################################
# 19. Hide row / column
########################################################################

ws.set_row(45, None, None, {"hidden": True})
ws.write("A46", "Hidden Row")

ws.set_column("H:H", None, None, {"hidden": True})
ws.write("H1", "Hidden Column")

########################################################################
# 20. Named cell positions
########################################################################

ws.write("J2", "Top Right")
ws.write("J10", "Bottom Right")

workbook.close()