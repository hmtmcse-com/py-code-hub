import barcode
from barcode import Code128
from barcode import get
from barcode.writer import ImageWriter


# pip install python-barcode Pillow

'''
Measurement Data:

Height = module_height + text_distance + font_size

module_height = 15.0
text_distance = 5.0
font_size = 10

Height ≈ 15 + 5 + 10 = 30 mm

'''

print("Available Barcode List")
print(barcode.PROVIDED_BARCODES)
print("-----------------------------------")


def generate_barcode(data, filename="barcode.png"):
    barcode = Code128(data, writer=ImageWriter())
    barcode.save(f"tmp/{filename.replace('.png', '')}")  # auto adds .png
    print(f"Barcode saved as {filename}")


generate_barcode("123456789012", "example_barcode.png")


def generate_barcode_with_option(code: str, filename: str):
    # Generate the barcode and save it as a PNG
    barcode_writer = ImageWriter()
    options = {
        'module_width': 0.4,  # Width of a single barcode module  mm
        'module_height': 5.0,  # Height of the barcode mm
        'font_size': 10,
        'text_distance': 5.0,  # From Code to text
        'quiet_zone': 1.5,  # Blank space on either side,
        'write_text': False  # No text = less height
    }

    barcode_class = get('ean13', code, writer=barcode_writer)
    full_filename = barcode_class.save(f"tmp/{filename}", options)


def code128_barcode_with_option(code, filename="barcode.png"):
    barcode = Code128(code, writer=ImageWriter())
    options = {
        'module_width': 0.12,  # Width of a single barcode module  mm
        'module_height': 3.0,  # Height of the barcode mm
        'font_size': 6,
        'text_distance': 2.5,  # From Code to text
        'quiet_zone': 0.75,  # Blank space on either side,
        'write_text': True  # No text = less height
    }
    barcode.save(f"tmp/{filename.replace('.png', '')}", options)  # auto adds .png
    print(f"Barcode saved as {filename}")


# Example usage
generate_barcode_with_option(
    code="590123412345",  # 12-digit EAN-13 code
    filename="my_barcode",
)

code128_barcode_with_option(
    code="PD25040007",
    filename="code128_barcode_with_option",
)

