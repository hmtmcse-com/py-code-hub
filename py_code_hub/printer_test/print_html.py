from pdf2image import convert_from_bytes
from weasyprint import HTML
from escpos.printer import Usb


def html_to_image(html_content):
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()
    images = convert_from_bytes(pdf_bytes)
    return images[0]


# Your HTML content
html_content = """
<html>
  <body>
    <h1>Hello Printer</h1>
    <p>This is printed from HTML.</p>
  </body>
</html>
"""

img = html_to_image(html_content)
printer = Usb(0x4b43, 0x3538, 0, out_ep=0x03)
printer.image(img)
printer.cut()
