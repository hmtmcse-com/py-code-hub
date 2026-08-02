from pathlib import Path
import math
import xlsxwriter


class ExcelReport:

    def __init__(self, workbook, worksheet):
        self.wb = workbook
        self.ws = worksheet

        # Store format objects for reuse
        self.fmt_header = self.wb.add_format({
            "bold": True,
            "bg_color": "#D9EAD3",
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "text_wrap": True,
        })

        self.fmt_cell_text = self.wb.add_format({
            "border": 1,
            "valign": "top",
            "text_wrap": True,
        })

        self.fmt_cell_default = self.wb.add_format({
            "border": 1,
        })

        self.fmt_title = self.wb.add_format({
            "size": 18,
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "text_wrap": True,
        })

        self.fmt_subtitle = self.wb.add_format({
            "size": 13,
            "align": "center",
            "valign": "vcenter",
            "text_wrap": True,
        })

        self.fmt_report_name = self.wb.add_format({
            "size": 12,
            "bold": True,
            "align": "center",
            "valign": "vcenter",
        })

        # Track written table dimensions for auto-fitting and banner placement
        self.max_column = 0
        self.max_row = 0

    def setup_page(self, landscape=True):
        ws = self.ws

        ws.set_paper(9)  # 9 = A4 paper size in XlsxWriter
        if landscape:
            ws.set_landscape()
        else:
            ws.set_portrait()

        ws.fit_to_pages(1, 0)

        # Margins: left, right, top, bottom (in inches)
        ws.set_margins(
            left=0.25,
            right=0.25,
            top=0.35,
            bottom=0.35,
        )

        ws.center_horizontally()

    def banner(
            self,
            title,
            subtitle=None,
            report_name=None,
            logo=None,
            minimum_columns=8,
    ):
        ws = self.ws

        last_col = max(self.max_column, minimum_columns) - 1  # 0-indexed column

        # --------------------------------------------------------
        # Reserve logo area & row dimensions
        # --------------------------------------------------------
        row_heights = [30, 22, 22]

        # Increase Column A width slightly to give extra breathing room
        col_a_width_chars = 18
        ws.set_column(0, 0, col_a_width_chars)

        for idx, height in enumerate(row_heights):
            ws.set_row(idx, height)

        # Merge A1:A3 for logo (rows 0..2, col 0)
        ws.merge_range(0, 0, 2, 0, "", self.fmt_cell_default)

        # --------------------------------------------------------
        # Insert centered logo using scale options
        # --------------------------------------------------------
        if logo and Path(logo).exists():
            # Get dimensions of source image using PIL if available, or force scale
            try:
                from PIL import Image as PILImage
                with PILImage.open(logo) as img:
                    orig_w, orig_h = img.size
            except ImportError:
                # Default fallback assumption if PIL isn't installed
                orig_w, orig_h = 200, 200

            # Target box size inside A1:A3 in pixels (~60px to leave safe margins)
            target_size_px = 60.0

            # Calculate scale ratios
            scale_x = target_size_px / orig_w
            scale_y = target_size_px / orig_h
            scale = min(scale_x, scale_y)  # Maintain aspect ratio

            # Calculate actual pixel size after scaling
            scaled_w = orig_w * scale
            scaled_h = orig_h * scale

            # Approximate container dimensions (Col A width ~130px, Height ~98px)
            col_a_px = (col_a_width_chars * 7) + 5
            total_height_px = sum(h * (96 / 72) for h in row_heights)

            # Center offsets
            x_off = int(max((col_a_px - scaled_w) / 2, 5))
            y_off = int(max((total_height_px - scaled_h) / 2, 5))

            ws.insert_image(
                0,
                0,
                logo,
                {
                    "x_scale": scale,
                    "y_scale": scale,
                    "x_offset": x_off,
                    "y_offset": y_off,
                    "object_position": 1,  # Move and size with cells
                },
            )

        # --------------------------------------------------------
        # Title
        # --------------------------------------------------------
        chars_per_line = max(35, (last_col + 1) * 8)
        lines = math.ceil(len(title) / chars_per_line)
        title_height = max(row_heights[0], lines * 22)
        ws.set_row(0, title_height)

        ws.merge_range(0, 1, 0, last_col, title, self.fmt_title)

        # --------------------------------------------------------
        # Subtitle
        # --------------------------------------------------------
        if subtitle:
            ws.merge_range(1, 1, 1, last_col, subtitle, self.fmt_subtitle)

        # --------------------------------------------------------
        # Report name
        # --------------------------------------------------------
        if report_name:
            ws.merge_range(2, 1, 2, last_col, report_name, self.fmt_report_name)

        # Freeze panes & Repeat rows
        ws.freeze_panes(4, 0)
        ws.repeat_rows(0, 3)

    def add_table(self, headers, rows):
        ws = self.ws
        start_row = 4  # Row 5 (0-indexed)

        self.max_column = len(headers)

        # Header
        for col, header in enumerate(headers):
            ws.write(start_row, col, header, self.fmt_header)

        # Data
        for r_idx, row in enumerate(rows, start=start_row + 1):
            for c_idx, value in enumerate(row):
                if isinstance(value, str):
                    ws.write(r_idx, c_idx, value, self.fmt_cell_text)
                else:
                    ws.write(r_idx, c_idx, value, self.fmt_cell_default)

        self.max_row = start_row + len(rows)
        self.auto_width(headers, rows)

    def auto_width(self, headers, rows):
        # Calculate max string lengths per column
        col_widths = [len(str(h)) for h in headers]

        for row in rows:
            for idx, val in enumerate(row):
                col_widths[idx] = max(col_widths[idx], len(str(val)))

        for idx, length in enumerate(col_widths):
            # Clamp width between 10 and 35
            width = min(max(length + 2, 10), 35)
            ws.set_column(idx, idx, width)


# --------------------------------------------------
# Example
# --------------------------------------------------

wb = xlsxwriter.Workbook("production_report.xlsx")
ws = wb.add_worksheet()

report = ExcelReport(wb, ws)
report.setup_page(landscape=True)

headers = [
    "Roll",
    "Student Name",
    "Bangla",
    "English",
    "Math",
    "Science",
    "Religion",
    "ICT",
    "Total",
    "GPA",
    "Position",
]

rows = []
for i in range(1, 51):
    rows.append(
        [
            i,
            f"Student {i}",
            95,
            91,
            99,
            94,
            96,
            93,
            568,
            5.00,
            i,
        ]
    )

report.add_table(headers, rows)

report.banner(
    title="Government Bangla Fighter Higher Secondary School and College, Rangpur, Bangladesh. This is an intentionally very long title to demonstrate automatic wrapping while keeping the banner consistent across reports with different numbers of columns.",
    subtitle="Annual Examination 2026",
    report_name="Merit List",
    logo="logo.png",  # remove or change if unavailable
)

wb.close()
print("Done")