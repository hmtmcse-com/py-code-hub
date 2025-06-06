import time
from pdf2image import convert_from_bytes
from weasyprint import HTML
from escpos.printer import Usb


def html_to_image(html_content):

    start = time.time()
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()
    end = time.time()
    duration = end - start
    print(f"Generate PDF: {duration:.6f}")

    start = time.time()
    images = convert_from_bytes(pdf_bytes)
    end = time.time()
    duration = end - start
    print(f"Image Convert: {duration:.6f}")

    images[0].save("output.png", "PNG")
    return images[0]


# Your HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Token</title>


    <style>

        * {
            margin: 0;
            padding: 0;
        }


        .token-container {
            width: 47mm;
            height: 33mm;
            text-align: center;
            border: 2px solid #000;
        }

        .token-container .token-heading {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
            line-height: 1;
        }

       .token-container .token-subtitle {
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 8px;
        }

        .token-container .token-no {
            font-size: 38px;
            font-weight: bold;
            line-height: 1;
        }


        @media print {
            @page {
                size: 48mm 35mm;
                margin: 0 !important;
                padding: 0 !important;
            }

            * {
                margin: 0;
                padding: 0;
            }

        }
    </style>
</head>
<body>

<div class="token-container">
    <h1 class="token-heading">Wellcome to BFE</h1>
    <p class="token-subtitle">Your Token No</p>
    <div class="token-no">
        T001
    </div>
</div>

</body>
</html>
"""


def print_to_printer(img):
    start = time.time()

    printer = Usb(0x4b43, 0x3538, out_ep=0x03, in_ep=0x81)
    printer.set(align='center')

    printer.text("<<=== BEFORE IMAGE ===============>>\n")
    printer.image(img)
    printer.text("<<================ AFTER IMAGE ===>>\n")
    printer.cut()
    end = time.time()
    duration = end - start
    print(f"End Print: {duration:.6f}")


img = html_to_image(html_content)
print_to_printer(img)
