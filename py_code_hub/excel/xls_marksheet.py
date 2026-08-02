import xlsxwriter

# Create a workbook and add a worksheet
workbook = xlsxwriter.Workbook("Student_Marksheet.xlsx")
worksheet = workbook.add_worksheet("Marksheet")

# --- Page Setup for Printing / PDF Export ---
worksheet.set_paper(9)  # A4 size
worksheet.set_portrait()
worksheet.fit_to_pages(1, 1)
worksheet.hide_gridlines(0)  # Ensure gridlines are visible

# --- Define Color Palette & Styles ---
# Primary: #1B365D (Dark Navy) | Subtitle: #4B6584 | Zebra: #F8FAFC | Pass Accent: #D4EDDA

title_fmt = workbook.add_format(
    {
        "bold": True,
        "font_name": "Arial",
        "font_size": 18,
        "font_color": "#1B365D",
        "align": "center",
        "valign": "vcenter",
    }
)

subtitle_fmt = workbook.add_format(
    {
        "bold": True,
        "font_name": "Arial",
        "font_size": 11,
        "font_color": "#4B6584",
        "align": "center",
        "valign": "vcenter",
    }
)

meta_label_fmt = workbook.add_format(
    {
        "bold": True,
        "font_name": "Arial",
        "font_size": 10,
        "font_color": "#1B365D",
        "align": "left",
    }
)

meta_val_fmt = workbook.add_format(
    {
        "font_name": "Arial",
        "font_size": 10,
        "font_color": "#2C3E50",
        "align": "left",
        "bottom": 1,
        "bottom_color": "#D1D8E0",
    }
)

header_fmt = workbook.add_format(
    {
        "bold": True,
        "font_name": "Arial",
        "font_size": 10,
        "font_color": "#FFFFFF",
        "bg_color": "#1B365D",
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "border_color": "#1B365D",
    }
)

cell_center = workbook.add_format(
    {
        "font_name": "Arial",
        "font_size": 10,
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "border_color": "#D1D8E0",
    }
)

cell_left = workbook.add_format(
    {
        "font_name": "Arial",
        "font_size": 10,
        "align": "left",
        "valign": "vcenter",
        "border": 1,
        "border_color": "#D1D8E0",
    }
)

cell_zebra = workbook.add_format(
    {
        "font_name": "Arial",
        "font_size": 10,
        "align": "center",
        "valign": "vcenter",
        "bg_color": "#F8FAFC",
        "border": 1,
        "border_color": "#D1D8E0",
    }
)

cell_left_zebra = workbook.add_format(
    {
        "font_name": "Arial",
        "font_size": 10,
        "align": "left",
        "valign": "vcenter",
        "bg_color": "#F8FAFC",
        "border": 1,
        "border_color": "#D1D8E0",
    }
)

total_label_fmt = workbook.add_format(
    {
        "bold": True,
        "font_name": "Arial",
        "font_size": 10,
        "font_color": "#1B365D",
        "align": "right",
        "valign": "vcenter",
        "border": 1,
        "border_color": "#D1D8E0",
        "bg_color": "#EAEFF5",
    }
)

total_val_fmt = workbook.add_format(
    {
        "bold": True,
        "font_name": "Arial",
        "font_size": 10,
        "font_color": "#1B365D",
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "border_color": "#D1D8E0",
        "bg_color": "#EAEFF5",
    }
)

pass_fmt = workbook.add_format(
    {
        "bold": True,
        "font_name": "Arial",
        "font_size": 10,
        "font_color": "#1E7E34",
        "bg_color": "#D4EDDA",
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "border_color": "#C3E6CB",
    }
)

# Signature line formatting (Top border acts as the sign line)
sig_line_fmt = workbook.add_format(
    {
        "top": 1,
        "top_color": "#2C3E50",
        "font_name": "Arial",
        "font_size": 10,
        "bold": True,
        "font_color": "#1B365D",
        "align": "center",
        "valign": "top",
    }
)

# --- Column Width Configuration ---
worksheet.set_column("A:A", 6)  # Sl No
worksheet.set_column("B:B", 24)  # Subject
worksheet.set_column("C:C", 14)  # Full Marks
worksheet.set_column("D:D", 14)  # Pass Marks
worksheet.set_column("E:E", 16)  # Marks Obtained
worksheet.set_column("F:F", 12)  # Grade
worksheet.set_column("G:G", 12)  # Status

# --- School Header Section ---
worksheet.merge_range("A2:G2", "EXCELLENCE INTERNATIONAL SCHOOL", title_fmt)
worksheet.merge_range(
    "A3:G3", "ANNUAL EXAMINATION ACADEMIC PROGRESS REPORT", subtitle_fmt
)
worksheet.merge_range("A4:G4", "Academic Year: 2025 - 2026", subtitle_fmt)

# --- Student Details Header ---
worksheet.write("A6", "Student Name:", meta_label_fmt)
worksheet.merge_range("B6:C6", "Alexander Wright", meta_val_fmt)

worksheet.write("E6", "Roll No:", meta_label_fmt)
worksheet.write("F6", "1024", meta_val_fmt)

worksheet.write("A7", "Class & Sec:", meta_label_fmt)
worksheet.merge_range("B7:C7", "Grade 10 - A", meta_val_fmt)

worksheet.write("E7", "Date of Birth:", meta_label_fmt)
worksheet.write("F7", "14/05/2010", meta_val_fmt)

# --- Marksheet Table Headers ---
headers = [
    "Sl.",
    "Subject",
    "Full Marks",
    "Pass Marks",
    "Marks Obtained",
    "Grade",
    "Status",
]
for col_idx, text in enumerate(headers):
    worksheet.write(9, col_idx, text, header_fmt)

# --- Marks Data ---
subjects_data = [
    (1, "English Language", 100, 33, 88, "A+", "PASS"),
    (2, "Mathematics", 100, 33, 95, "A+", "PASS"),
    (3, "Physics", 100, 33, 82, "A", "PASS"),
    (4, "Chemistry", 100, 33, 78, "A", "PASS"),
    (5, "Biology", 100, 33, 85, "A+", "PASS"),
    (6, "Computer Science", 100, 33, 92, "A+", "PASS"),
    (7, "Social Studies", 100, 33, 74, "B+", "PASS"),
]

start_row = 10
for i, row in enumerate(subjects_data):
    current_row = start_row + i
    is_even = i % 2 == 1
    c_fmt = cell_zebra if is_even else cell_center
    l_fmt = cell_left_zebra if is_even else cell_left

    worksheet.write(current_row, 0, row[0], c_fmt)
    worksheet.write(current_row, 1, row[1], l_fmt)
    worksheet.write(current_row, 2, row[2], c_fmt)
    worksheet.write(current_row, 3, row[3], c_fmt)
    worksheet.write(current_row, 4, row[4], c_fmt)
    worksheet.write(current_row, 5, row[5], c_fmt)
    worksheet.write(current_row, 6, row[6], pass_fmt)

# --- Totals & Summary Row ---
total_row = start_row + len(subjects_data)

worksheet.merge_range(
    total_row, 0, total_row, 1, "Grand Total / Overall", total_label_fmt
)
worksheet.write_formula(total_row, 2, f"=SUM(C11:C{total_row})", total_val_fmt)
worksheet.write_formula(total_row, 3, f"=SUM(D11:D{total_row})", total_val_fmt)
worksheet.write_formula(total_row, 4, f"=SUM(E11:E{total_row})", total_val_fmt)

worksheet.write(total_row, 5, "85.4%", total_val_fmt)
worksheet.write(total_row, 6, "PASSED", pass_fmt)

# --- Bottom 3 Signatures Section ---
# Placed 5 rows below the table for visual spacing
sig_row = total_row + 5

# 1. Class Teacher Signature (Columns A & B)
worksheet.merge_range(sig_row, 0, sig_row, 1, "Class Teacher", sig_line_fmt)

# 2. VP Academic Signature (Columns D & E)
worksheet.merge_range(sig_row, 3, sig_row, 4, "VP Academic", sig_line_fmt)

# 3. Principle Signature (Columns F & G)
worksheet.merge_range(sig_row, 5, sig_row, 6, "Principle", sig_line_fmt)

# Set custom row heights
worksheet.set_row(1, 25)  # Title
worksheet.set_row(9, 22)  # Table header
for r in range(10, total_row + 1):
    worksheet.set_row(r, 18)

workbook.close()