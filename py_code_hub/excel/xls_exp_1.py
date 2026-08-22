import xlsxwriter

workbook = xlsxwriter.Workbook("report.xlsx")
worksheet = workbook.add_worksheet("Report")

# --------------------------------------------------
# Page setup - A4
# --------------------------------------------------
worksheet.set_paper(9)              # A4
worksheet.set_landscape()           # Use landscape for more columns
worksheet.fit_to_pages(1, 0)        # Fit all columns to 1 page wide

worksheet.set_margins(
    left=0.3,
    right=0.3,
    top=0.5,
    bottom=0.5,
)

# --------------------------------------------------
# Formats
# --------------------------------------------------
title_format = workbook.add_format({
    "bold": True,
    "font_size": 18,
    "align": "center",
    "valign": "vcenter",
})

subtitle_format = workbook.add_format({
    "font_size": 10,
    "align": "center",
    "valign": "vcenter",
})

header_format = workbook.add_format({
    "bold": True,
    "border": 1,
    "align": "center",
    "valign": "vcenter",
    "text_wrap": True,
})

cell_format = workbook.add_format({
    "border": 1,
    "valign": "top",
    "text_wrap": True,
})

# --------------------------------------------------
# Title
# --------------------------------------------------
worksheet.merge_range(
    "A1:F1",
    "Student Information Report Long enough to fit in size xyz",
    title_format,
)

# worksheet.set_row(0, 28)

# --------------------------------------------------
# Subtitle
# --------------------------------------------------
worksheet.merge_range(
    "A2:F2",
    "Academic Year: 2026 | Generated: 17 August 2026",
    subtitle_format,
)

# worksheet.set_row(1, 20)

# --------------------------------------------------
# Column headers
# --------------------------------------------------
headers = [
    "SL",
    "Student Name",
    "Father Name",
    "Class",
    "Roll",
    "Address",
]

header_row = 3

for col, header in enumerate(headers):
    worksheet.write(header_row, col, header, header_format)

# worksheet.set_row(header_row, 25)

# Repeat header when printing multiple pages vertically
# worksheet.repeat_rows(header_row, header_row)

# --------------------------------------------------
# Column widths
# --------------------------------------------------
# worksheet.set_column("A:A", 6)
# worksheet.set_column("B:B", 20)
# worksheet.set_column("C:C", 20)
# worksheet.set_column("D:D", 12)
# worksheet.set_column("E:E", 8)
# worksheet.set_column("F:F", 35)

# --------------------------------------------------
# Data
# --------------------------------------------------
data = [
    # [1, "Abdullah Al Mamun Abdullah Al Mamun", "Md. Rahman", "Class 10", 1, "Rangpur, Bangladesh"],
    # [2, "Mohammad Hasan", "Md. Karim", "Class 10", 2, "Dhaka, Bangladesh"],
    # [3, "Sabbir Ahmed", "Md. Salim", "Class 9", 3, "Dinajpur, Bangladesh"],
]

row = header_row + 1

for item in data:
    for col, value in enumerate(item):
        worksheet.write(row, col, value, cell_format)

    # worksheet.set_row(row, 30)
    row += 1

# --------------------------------------------------
# Print area
# --------------------------------------------------
worksheet.print_area(
    0,
    0,
    row - 1,
    len(headers) - 1,
)

# Center horizontally on page
worksheet.center_horizontally()

# --------------------------------------------------
# Footer
# --------------------------------------------------
worksheet.set_footer(
    "&LPage &P of &N&CStudent Report&R&F"
)

worksheet.autofit()

workbook.close()