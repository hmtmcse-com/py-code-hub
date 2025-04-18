from barcode import Code128
from barcode.writer import SVGWriter


class CustomSVGWriter(SVGWriter):
    pass


# Custom writer options
options = {
    'module_width': 0.2,  # Width of each barcode module
    'module_height': 15.0,  # Height of each barcode module
    'quiet_zone': 1.0,  # Quiet zone around the barcode
    'font_size': 6,  # Size of the text
    'text_distance': 5.0,  # Distance between barcode and text
    'background': 'white',  # Background color
    'foreground': 'black',  # Foreground color (bars and text)
    'center_text': True,  # Center the text below barcode
    'write_text': True
}

# Create barcode with custom options
barcode = Code128('PYTHON-123', writer=CustomSVGWriter())

# Save with custom filename
filename = barcode.save('custom_barcode', options)

print(f"Custom barcode saved as {filename}.svg")
