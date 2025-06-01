from pdf2image import convert_from_bytes
from weasyprint import HTML
from escpos.printer import Usb


def html_to_image(html_content):
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()
    images = convert_from_bytes(pdf_bytes)
    images[0].save("output.png", "PNG")
    return images[0]


# Your HTML content
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Queue Token</title>
    <style>
        @page {
            size: 80mm 40mm;
            margin: 0;
        }

        body {
            width: 80mm;
            height: 40mm;
            margin: 0;
            text-align: center;
            border: 2px black solid;
        }

        body {
            padding: 10px;
        }

        .token-number {
            font-size: 80px;
            font-weight: bold;
        }

        p {
            margin: 1px;
        }
        h2 {
            margin: 3px;
        }
    </style>
</head>
<body>
<!--<h2>Welcome to BFE</h2>-->
<div class="token">
<!--    <p>Your Token Number:</p>-->
    <div class="token-number" id="tokenNumber">001</div>
</div>
</body>
</html>
"""

img = html_to_image(html_content)
# printer = Usb(0x4b43, 0x3538,  out_ep=0x03)
# printer.image(img)
# printer.cut()
