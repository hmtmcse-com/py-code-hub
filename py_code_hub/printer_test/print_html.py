from weasyprint import HTML
from escpos.printer import Usb
from PIL import Image
import io


def html_to_image(html_content):
    html = HTML(string=html_content)
    pdf_stream = io.BytesIO(html.write_pdf())
    return Image.open(pdf_stream)


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
