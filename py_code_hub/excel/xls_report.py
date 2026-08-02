from pathlib import Path
import math
import xlsxwriter


class ExcelReport:

    def __init__(self, workbook, worksheet):
        self.wb = workbook
        self.ws = worksheet

        # Formats
        self.fmt_title = self.wb.add_format({
            "size": 16,
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "text_wrap": True,
        })

        self.fmt_subtitle = self.wb.add_format({
            "size": 12,
            "align": "center",
            "valign": "vcenter",
            "text_wrap": True,
        })

        self.fmt_report_name = self.wb.add_format({
            "size": 11,
            "bold": True,
            "align": "center",
            "valign": "vcenter",
        })

        self.fmt_section_header = self.wb.add_format({
            "bold": True,
            "size": 11,
            "bg_color": "#D9EAD3",
            "border": 1,
            "valign": "vcenter",
        })

        self.fmt_section_content = self.wb.add_format({
            "size": 10,
            "border": 1,
            "valign": "top",
            "text_wrap": True,
        })

        self.fmt_logo_cell = self.wb.add_format({
            "border": 1,
        })

    def setup_page(self, landscape=False):
        ws = self.ws

        ws.set_paper(9)  # 9 = A4 Paper size
        if landscape:
            ws.set_landscape()
        else:
            ws.set_portrait()

        # Force all content to fit within 1 page wide (unlimited height)
        ws.fit_to_pages(1, 0)

        # Set tight margins (in inches) to maximize A4 width
        ws.set_margins(
            left=0.3,
            right=0.3,
            top=0.4,
            bottom=0.4,
        )

        ws.center_horizontally()

    def banner(
        self,
        title,
        subtitle=None,
        report_name=None,
        logo=None,
        max_cols=8,
    ):
        ws = self.ws
        last_col = max_cols - 1  # 0-indexed column

        # Column A reservation for logo
        col_a_width_chars = 16
        ws.set_column(0, 0, col_a_width_chars)

        # Banner Row Heights
        row_heights = [30, 22, 22]
        for idx, height in enumerate(row_heights):
            ws.set_row(idx, height)

        # Merge A1:A3 for logo container
        ws.merge_range(0, 0, 2, 0, "", self.fmt_logo_cell)

        # --------------------------------------------------------
        # Logo Placement (safely contained in A1:A3)
        # --------------------------------------------------------
        if logo and Path(logo).exists():
            try:
                from PIL import Image as PILImage
                with PILImage.open(logo) as img:
                    orig_w, orig_h = img.size
            except ImportError:
                orig_w, orig_h = 200, 200

            target_size_px = 65.0

            scale = min(target_size_px / orig_w, target_size_px / orig_h)
            scaled_w = orig_w * scale
            scaled_h = orig_h * scale

            col_a_px = (col_a_width_chars * 7) + 5
            total_height_px = sum(h * (96 / 72) for h in row_heights)

            x_off = int(max((col_a_px - scaled_w) / 2, 2))
            y_off = int(max((total_height_px - scaled_h) / 2, 2))

            ws.insert_image(
                0,
                0,
                logo,
                {
                    "x_scale": scale,
                    "y_scale": scale,
                    "x_offset": x_off,
                    "y_offset": y_off,
                    "object_position": 1,
                },
            )

        # --------------------------------------------------------
        # Headers (Title, Subtitle, Report Name)
        # --------------------------------------------------------
        ws.merge_range(0, 1, 0, last_col, title, self.fmt_title)

        if subtitle:
            ws.merge_range(1, 1, 1, last_col, subtitle, self.fmt_subtitle)

        if report_name:
            ws.merge_range(2, 1, 2, last_col, report_name, self.fmt_report_name)

        ws.freeze_panes(4, 0)
        ws.repeat_rows(0, 3)

    def add_result_sections(self, sections, max_cols=8):
        """
        Adds full-width result summary sections like shown in the image.
        """
        ws = self.ws
        last_col = max_cols - 1
        current_row = 4  # Start below header (Row 5)

        for title, text_content in sections:
            # 1. Section Header Title Row
            ws.set_row(current_row, 24)
            ws.merge_range(
                current_row, 0, current_row, last_col,
                title, self.fmt_section_header
            )
            current_row += 1

            # 2. Content Row with text wrapping
            # Estimate dynamic row height based on content length across page
            approx_chars_per_line = max_cols * 15
            line_count = math.ceil(len(text_content) / approx_chars_per_line)
            content_row_height = max(35, line_count * 18)

            ws.set_row(current_row, content_row_height)
            ws.merge_range(
                current_row, 0, current_row, last_col,
                text_content, self.fmt_section_content
            )
            current_row += 2  # Leave 1 blank separator row


# --------------------------------------------------
# Example Usage & Output Generation
# --------------------------------------------------

wb = xlsxwriter.Workbook("a4_fitted_report.xlsx")
ws = wb.add_worksheet("Result Summary")

report = ExcelReport(wb, ws)

# Setup page for A4 Portrait print fitting
report.setup_page(landscape=False)

# Add Banner Header
report.banner(
    title="Government Bangla Fighter Higher Secondary School and College",
    subtitle="Annual Examination 2026",
    report_name="Tabulation & Result Summary",
    logo="logo.png",  # Will automatically adjust if file exists
    max_cols=8,
)

# Sample section data structured like your screenshot
result_sections = [
    (
        "Passed in all subject",
        "Roll:-323(3.42), Roll:1(3.67), Roll:1(5.0), Roll:2(4.33), Roll:3(4.42), Roll:3(3.67), Roll:4(3.42), Roll:4(3.58), Roll:5(3.75), Roll:5(4.33), Roll:5(2.33), Roll:6(3.67), Roll:6(3.67), Roll:7(2.58), Roll:7(3.83), Roll:7(4.75), Roll:8(3.92), Roll:8(None), Roll:9(3.75), Roll:9(4.58), Roll:10(3.83), Roll:10(4.42), Roll:11(2.5), Roll:12(4.17), Roll:12(2.75), Roll:12(3.92), Roll:13(3.0), Roll:13(3.92), Roll:14(2.92), Roll:14(3.83), Roll:15(3.75), Roll:15(3.83), Roll:16(4.42), Roll:17(3.92), Roll:19(None), Roll:19(4.08), Roll:19(3.33), Roll:20(2.92), Roll:21(2.17), Roll:21(3.5), Roll:22(2.83), Roll:22(3.67), Roll:23(3.92), Roll:24(4.08), Roll:26(4.08), Roll:26(3.92), Roll:26(2.0), Roll:27(4.0), Roll:27(3.0), Roll:28(4.17), Roll:28(3.5), Roll:28(3.17), Roll:29(3.75), Roll:29(3.58), Roll:31(3.33), Roll:31(3.92), Roll:31(2.33), Roll:33(2.83), Roll:34(3.67), Roll:35(2.75), Roll:36(3.17), Roll:37(2.0), Roll:38(3.17), Roll:38(2.83), Roll:39(3.25), Roll:39(3.25), Roll:40(3.83), Roll:40(3.0), Roll:41(2.17), Roll:41(4.67), Roll:41(3.67), Roll:42(2.5), Roll:42(3.58), Roll:43(3.08), Roll:44(3.75), Roll:44(2.92), Roll:45(2.58), Roll:46(3.17), Roll:46(3.33), Roll:47(2.0), Roll:47(3.08), Roll:48(2.17), Roll:49(3.42), Roll:49(3.42), Roll:50(5.0), Roll:50(3.42), Roll:50(3.0), Roll:52(3.33), Roll:53(3.25), Roll:54(3.58), Roll:55(3.67), Roll:58(2.5), Roll:58(3.58), Roll:58(3.25), Roll:59(3.25), Roll:59(3.17), Roll:60(3.67), Roll:60(3.33), Roll:61(3.83), Roll:62(3.92), Roll:65(3.25), Roll:66(3.42), Roll:66(4.33), Roll:68(3.42), Roll:69(2.75), Roll:69(3.08), Roll:70(2.75), Roll:71(2.5), Roll:72(2.5), Roll:73(2.58), Roll:74(2.0), Roll:74(3.58), Roll:76(3.08), Roll:76(4.08), Roll:76(2.42), Roll:77(3.75), Roll:78(3.75), Roll:78(2.92), Roll:79(2.83), Roll:80(2.83), Roll:80(3.83), Roll:81(3.57), Roll:81(2.36), Roll:82(3.83), Roll:82(2.9), Roll:82(2.14), Roll:83(3.08), Roll:84(3.42), Roll:84(3.92), Roll:85(3.14), Roll:85(3.0), Roll:85(2.92), Roll:86(3.25), Roll:87(3.75), Roll:88(2.83), Roll:89(4.0), Roll:90(3.0), Roll:91(3.25), Roll:92(3.92), Roll:93(3.75), Roll:93(3.83), Roll:94(2.92), Roll:95(3.67), Roll:95(3.0), Roll:96(3.17), Roll:97(3.58), Roll:97(5.0), Roll:98(4.08), Roll:99(4.25), Roll:100(4.2), Roll:101(3.75), Roll:102(2.58), Roll:102(3.67), Roll:103(3.17), Roll:103(4.83), Roll:104(2.58), Roll:104(3.75), Roll:105(4.0), Roll:106(4.0), Roll:107(3.5), Roll:108(3.5), Roll:109(3.58), Roll:112(3.33), Roll:113(2.58), Roll:113(3.92), Roll:114(3.33), Roll:115(3.75), Roll:115(3.83), Roll:116(3.33), Roll:117(2.92), Roll:118(3.0), Roll:121(3.42), Roll:121(3.33), Roll:122(3.83), Roll:122(2.75), Roll:123(2.92), Roll:124(2.83), Roll:126(2.75), Roll:127(2.67), Roll:127(3.17), Roll:128(3.33), Roll:128(3.33), Roll:129(2.92), Roll:129(3.67), Roll:130(3.0), Roll:130(3.83), Roll:131(3.25), Roll:132(3.92), Roll:132(2.83), Roll:133(3.0), Roll:134(3.33), Roll:135(None), Roll:136(3.0), Roll:137(3.2), Roll:138(2.92), Roll:141(3.17), Roll:142(3.75), Roll:143(2.92), Roll:144(3.25), Roll:147(3.75), Roll:147(3.08), Roll:148(3.25), Roll:148(4.42), Roll:149(3.75), Roll:150(3.75), Roll:150(3.42), Roll:151(3.17), Roll:151(3.25), Roll:152(2.67), Roll:153(4.33), Roll:154(3.75), Roll:154(2.57), Roll:155(3.75), Roll:156(3.5), Roll:157(3.17), Roll:159(4.17), Roll:160(4.33), Roll:161(3.83), Roll:162(3.75), Roll:163(4.0), Roll:164(4.08), Roll:165(3.33), Roll:166(2.67), Roll:168(3.58), Roll:169(3.33), Roll:172(3.0), Roll:173(3.0), Roll:175(4.58), Roll:177(3.58), Roll:178(3.42), Roll:179(3.5), Roll:180(3.42), Roll:181(3.25), Roll:183(3.42), Roll:184(3.0), Roll:186(3.0), Roll:187(3.42), Roll:188(3.08), Roll:189(3.5), Roll:191(3.42), Roll:193(None), Roll:195(4.0), Roll:196(3.92), Roll:197(2.83), Roll:198(3.17), Roll:199(2.83), Roll:201(3.75), Roll:202(4.83), Roll:203(3.33), Roll:204(3.92), Roll:205(3.17), Roll:206(2.67), Roll:209(3.83), Roll:212(4.25), Roll:215(3.25), Roll:216(3.5), Roll:221(3.58), Roll:222(4.42), Roll:223(4.75), Roll:224(4.17), Roll:225(4.43), Roll:226(3.83), Roll:227(3.5), Roll:228(3.5), Roll:229(3.42), Roll:230(4.25), Roll:231(3.67), Roll:232(4.08), Roll:233(4.08), Roll:234(3.92), Roll:235(3.75), Roll:236(3.08), Roll:237(3.42), Roll:238(4.17), Roll:239(4.08), Roll:240(3.83), Roll:241(3.58), Roll:242(3.67), Roll:243(3.25), Roll:245(3.83), Roll:246(3.75), Roll:247(3.83), Roll:248(3.75), Roll:249(5.0), Roll:250(3.75), Roll:251(5.0), Roll:253(4.08), Roll:254(4.0), Roll:255(4.17), Roll:256(3.92), Roll:257(4.58), Roll:258(4.08), Roll:262(3.67), Roll:263(3.25), Roll:264(4.58), Roll:265(4.0), Roll:266(4.5), Roll:267(3.08), Roll:268(3.25), Roll:269(3.25), Roll:270(3.42), Roll:271(3.42), Roll:272(3.58), Roll:282(3.42), Roll:283(4.0), Roll:284(3.0), Roll:287(3.58), Roll:288(2.67), Roll:289(2.67), Roll:290(3.67), Roll:292(4.25), Roll:293(3.42), Roll:294(4.08), Roll:295(5.0), Roll:296(3.75), Roll:297(3.25), Roll:298(3.75), Roll:299(3.42), Roll:300(3.17), Roll:302(3.5), Roll:303(3.25), Roll:304(3.5), Roll:305(3.83), Roll:306(3.83), Roll:307(3.67), Roll:308(3.83), Roll:309(3.92), Roll:311(3.83), Roll:312(4.25), Roll:314(3.33), Roll:315(3.83), Roll:316(3.4), Roll:317(4.17), Roll:318(4.67), Roll:319(3.42), Roll:320(3.75), Roll:321(2.75), Roll:322(2.92), Roll:323(3.17), Roll:325(2.92), Roll:326(4.25), Roll:327(4.17), Roll:328(3.58), Roll:330(3.17), Roll:334(3.58), Roll:335(4.0), Roll:336(3.92), Roll:337(3.67), Roll:338(3.25), Roll:339(2.75), Roll:340(3.83), Roll:341(3.08), Roll:342(2.92), Roll:343(3.83), Roll:345(4.33), Roll:346(3.25), Roll:348(3.92), Roll:349(4.08), Roll:350(3.25), Roll:351(4.33), Roll:352(3.5), Roll:353(3.92), Roll:354(3.92), Roll:358(3.92), Roll:362(3.0), Roll:363(4.17), Roll:364(3.75), Roll:365(3.75), Roll:366(3.83), Roll:367(3.33), Roll:368(3.42), Roll:369(4.08), Roll:370(4.42), Roll:372(3.58), Roll:373(3.83), Roll:374(3.58), Roll:375(4.0), Roll:377(5.0), Roll:378(4.92), Roll:379(4.58), Roll:380(3.42), Roll:381(4.08), Roll:382(3.33), Roll:383(3.83), Roll:384(3.5), Roll:385(3.75), Roll:386(3.92), Roll:387(4.0), Roll:388(3.67), Roll:389(3.33), Roll:390(3.0), Roll:391(3.0), Roll:392(4.08), Roll:393(3.58), Roll:394(3.75), Roll:397(3.42), Roll:398(3.58), Roll:399(3.17), Roll:400(3.83), Roll:402(3.42), Roll:403(3.42), Roll:404(3.0), Roll:405(3.5), Roll:406(3.33), Roll:408(3.58), Roll:409(3.5), Roll:410(3.58), Roll:411(3.0), Roll:412(3.17), Roll:414(4.33), Roll:415(3.25), Roll:417(4.0), Roll:418(3.25), Roll:420(3.08), Roll:423(3.83), Roll:425(3.58), Roll:426(3.75), Roll:427(4.0), Roll:428(3.0), Roll:430(None), Roll:431(3.25), Roll:433(3.25), Roll:435(2.92), Roll:438(3.5), Roll:439(4.0), Roll:440(3.75), Roll:441(3.33), Roll:442(3.67), Roll:443(4.42), Roll:444(3.75), Roll:445(4.0), Roll:446(3.42), Roll:447(4.33), Roll:448(3.25), Roll:451(3.92), Roll:452(3.08), Roll:453(3.33), Roll:454(3.33), Roll:455(3.33), Roll:456(3.5), Roll:457(3.92), Roll:458(3.42), Roll:459(3.42), Roll:460(4.33), Roll:461(3.42), Roll:462(3.5), Roll:463(4.0), Roll:464(3.5), Roll:465(3.58), Roll:466(3.5), Roll:468(3.83), Roll:469(3.92), Roll:470(3.67), Roll:472(4.0), Roll:475(4.17), Roll:476(3.25), Roll:477(3.17), Roll:479(2.75), Roll:480(2.92), Roll:482(2.92), Roll:486(3.33), Roll:489(4.33), Roll:490(4.42), Roll:491(3.42), Roll:492(3.42), Roll:493(3.08), Roll:496(3.33), Roll:497(3.17), Roll:498(3.25), Roll:499(3.25), Roll:502(3.17), Roll:503(3.0), Roll:504(2.67), Roll:505(3.75), Roll:507(3.0), Roll:509(3.75), Roll:510(4.17), Roll:511(3.67), Roll:512(3.58), Roll:513(4.0), Roll:514(3.25), Roll:515(4.58), Roll:516(3.75), Roll:517(4.08), Roll:518(3.25), Roll:519(3.33), Roll:520(3.75), Roll:521(3.25), Roll:522(3.92), Roll:523(3.75), Roll:524(3.17), Roll:526(4.33), Roll:527(3.0), Roll:528(4.0), Roll:529(3.58), Roll:530(3.5), Roll:531(3.67), Roll:532(4.25), Roll:534(3.5), Roll:537(3.67), Roll:538(4.17), Roll:539(3.75), Roll:540(3.83), Roll:541(3.5), Roll:542(3.33), Roll:543(3.75), Roll:544(3.17), Roll:545(3.67), Roll:546(3.33), Roll:547(3.42), Roll:548(3.83), Roll:549(3.42), Roll:550(4.08), Roll:551(3.17), Roll:552(3.58), Roll:553(3.42), Roll:557(3.58), Roll:560(3.33), Roll:562(3.33), Roll:563(3.25), Roll:564(3.17), Roll:565(3.92), Roll:566(3.92), Roll:568(3.5), Roll:572(4.0), Roll:573(3.08), Roll:575(3.5), Roll:577(3.25), Roll:580(3.43), Roll:587(3.43)"
    ),
    (
        "Failed in one subject",
        "Roll:1 [Marketing(CQ:12)], Roll:14 [English(CQ:18)], Roll:22 [Math(CQ:15)], Roll:45 [Accounting(CQ:19)]"
    ),
    (
        "Failed in two subjects",
        "Roll:-94 [Accounting(CQ:10), Finance(CQ:14)], Roll:88 [Bangla(CQ:12), ICT(CQ:08)]"
    ),
    (
        "Failed in more subjects",
        "Roll:-151 [Civic & Citizenship(CQ:05), History(CQ:11), Economics(CQ:09)], Roll:199 [Math(CQ:04), Physics(CQ:10), Chemistry(CQ:08), Biology(CQ:12)]"
    ),
]

# Add sections to sheet
report.add_result_sections(result_sections, max_cols=8)

wb.close()
print("Successfully generated a4_fitted_report.xlsx!")