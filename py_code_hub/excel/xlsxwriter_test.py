# First install: pip install XlsxWriter
import xlsxwriter

# Create workbook
workbook = xlsxwriter.Workbook('xlsxwriter_colors.xlsx')
worksheet = workbook.add_worksheet()

# Define color formats
red_format = workbook.add_format({'bg_color': 'red', 'bold': True})
green_format = workbook.add_format({'bg_color': 'green', 'bold': True})
blue_format = workbook.add_format({'bg_color': 'blue', 'bold': True, 'font_color': 'white'})
yellow_format = workbook.add_format({'bg_color': 'yellow', 'bold': True})

# Write data with colors
worksheet.write('A1', 'RED BACKGROUND', red_format)
worksheet.write('A2', 'GREEN BACKGROUND', green_format)
worksheet.write('A3', 'BLUE BACKGROUND', blue_format)
worksheet.write('A4', 'YELLOW BACKGROUND', yellow_format)

# More colors with hex codes
colors_hex = [
    ('A5', 'ORANGE', '#FFA500'),
    ('A6', 'PURPLE', '#800080'),
    ('A7', 'PINK', '#FFC0CB'),
    ('A8', 'GRAY', '#808080'),
]

for cell, text, color in colors_hex:
    fmt = workbook.add_format({'bg_color': color, 'bold': True})
    worksheet.write(cell, text, fmt)

workbook.close()
print("Created 'xlsxwriter_colors.xlsx' - This should definitely work!")