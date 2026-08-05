from xlsxwriter import Workbook

workbook = Workbook("self-practice.xlsx")
active_sheet = workbook.add_worksheet("Cells")


headers = ["ID", "Name", "Status"]
for i, header in enumerate(headers):
    active_sheet.write(0, i, header)

workbook.close()