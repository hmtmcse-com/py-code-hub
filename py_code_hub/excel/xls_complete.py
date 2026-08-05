import xlsxwriter
from datetime import datetime

workbook = xlsxwriter.Workbook("xlsxwriter_demo.xlsx")

worksheet = workbook.add_worksheet("Demo")

############################################################
# Formats
############################################################

title = workbook.add_format({
    "bold": True,
    "font_size": 18,
    "align": "center",
    "valign": "vcenter",
    "bg_color": "#4472C4",
    "font_color": "white"
})

header = workbook.add_format({
    "bold": True,
    "bg_color": "#D9EAD3",
    "border": 1,
    "align": "center"
})

text = workbook.add_format({
    "border": 1
})

money = workbook.add_format({
    "border": 1,
    "num_format": '#,##0.00'
})

date = workbook.add_format({
    "border": 1,
    "num_format": "dd-mmm-yyyy"
})

percent = workbook.add_format({
    "border": 1,
    "num_format": "0.00%"
})

wrap = workbook.add_format({
    "text_wrap": True,
    "border": 1
})

red = workbook.add_format({
    "font_color": "red",
    "bold": True
})

green = workbook.add_format({
    "font_color": "green",
    "bold": True
})

rotate = workbook.add_format({
    "rotation": 45,
    "border": 1
})

############################################################
# Merge Title
############################################################

worksheet.merge_range("A1:H2", "XlsxWriter Complete Example", title)

############################################################
# Width & Height
############################################################

worksheet.set_column("A:A", 8)
worksheet.set_column("B:B", 25)
worksheet.set_column("C:H", 18)

worksheet.set_row(0, 30)
worksheet.set_row(1, 30)

############################################################
# Freeze Pane
############################################################

worksheet.freeze_panes(3, 0)

############################################################
# Headers
############################################################

headers = [
    "ID",
    "Name",
    "Salary",
    "Join Date",
    "Bonus %",
    "Department",
    "Score",
    "Status"
]

worksheet.write_row(2, 0, headers, header)

############################################################
# Data
############################################################

rows = [
    [1, "John", 50000, datetime(2022,1,10), 0.10, "IT", 95],
    [2, "Alice", 30000, datetime(2023,4,5), 0.15, "HR", 60],
    [3, "Bob", 45000, datetime(2020,6,18), 0.08, "Sales", 82],
    [4, "David", 25000, datetime(2024,2,1), 0.20, "Finance", 45],
]

start = 3

for r, row in enumerate(rows):

    worksheet.write_number(start+r,0,row[0],text)
    worksheet.write(start+r,1,row[1],text)
    worksheet.write_number(start+r,2,row[2],money)
    worksheet.write_datetime(start+r,3,row[3],date)
    worksheet.write_number(start+r,4,row[4],percent)
    worksheet.write(start+r,5,row[5],text)
    worksheet.write_number(start+r,6,row[6],text)

    worksheet.write_formula(
        start+r,
        7,
        f'=IF(G{start+r+1}>=80,"PASS","FAIL")',
        text
    )

############################################################
# Formula
############################################################

worksheet.write("J4","Total Salary",header)
worksheet.write_formula("K4","=SUM(C4:C7)",money)

worksheet.write("J5","Average")
worksheet.write_formula("K5","=AVERAGE(C4:C7)",money)

############################################################
# Conditional Formatting
############################################################

worksheet.conditional_format(
    "G4:G7",
    {
        "type":"cell",
        "criteria":">=",
        "value":80,
        "format":green
    }
)

worksheet.conditional_format(
    "G4:G7",
    {
        "type":"cell",
        "criteria":"<",
        "value":80,
        "format":red
    }
)

############################################################
# Data Validation
############################################################

worksheet.data_validation(
    "F4:F20",
    {
        "validate":"list",
        "source":["IT","HR","Sales","Finance"]
    }
)

############################################################
# Comments
############################################################

worksheet.write_comment(
    "B4",
    "Employee Name"
)

############################################################
# Hyperlink
############################################################

worksheet.write_url(
    "J8",
    "https://www.python.org",
    string="Python Website"
)

############################################################
# Rich Text
############################################################

bold = workbook.add_format({"bold":True})
blue = workbook.add_format({"font_color":"blue"})

worksheet.write_rich_string(
    "J10",
    bold,
    "Bold ",
    blue,
    "Blue ",
    "Normal"
)

############################################################
# Image
############################################################

# Uncomment if image exists
# worksheet.insert_image(
#     "J12",
#     "logo.png",
#     {
#         "x_scale":0.5,
#         "y_scale":0.5
#     }
# )

############################################################
# Table
############################################################

worksheet.add_table(
    "A3:H7",
    {
        "style":"Table Style Medium 9",
        "columns":[
            {"header":"ID"},
            {"header":"Name"},
            {"header":"Salary"},
            {"header":"Join Date"},
            {"header":"Bonus"},
            {"header":"Department"},
            {"header":"Score"},
            {"header":"Status"}
        ]
    }
)


############################################################
# Outline
############################################################

worksheet.set_row(4,None,None,{"level":1})
worksheet.set_row(5,None,None,{"level":1})

############################################################
# Hide Row
############################################################

worksheet.set_row(6,None,None,{"hidden":True})

############################################################
# Hide Column
############################################################

worksheet.set_column("I:I",None,None,{"hidden":True})

############################################################
# Named Range
############################################################

workbook.define_name(
    "SalaryRange",
    "=Demo!$C$4:$C$7"
)

############################################################
# Sparkline
############################################################

worksheet.add_sparkline(
    "L4",
    {
        "range":"G4:G7"
    }
)

############################################################
# Chart
############################################################

chart = workbook.add_chart({"type":"column"})

chart.add_series({
    "name":"Salary",
    "categories":"=Demo!$B$4:$B$7",
    "values":"=Demo!$C$4:$C$7"
})

chart.set_title({"name":"Employee Salary"})

worksheet.insert_chart("J15",chart)

############################################################
# Print
############################################################

worksheet.set_landscape()
worksheet.fit_to_pages(1, 0)
worksheet.repeat_rows(0,2)

worksheet.set_header("&CCompany Report")
worksheet.set_footer("&LGenerated by XlsxWriter&RPage &P of &N")

############################################################
# Protection
############################################################

worksheet.protect()

############################################################
# Zoom
############################################################

worksheet.set_zoom(120)

############################################################
# Selection
############################################################

worksheet.set_selection("A4")

############################################################
# Tab Color
############################################################

worksheet.set_tab_color("green")

############################################################
# Page Break
############################################################

worksheet.set_h_pagebreaks([20])

############################################################

workbook.close()