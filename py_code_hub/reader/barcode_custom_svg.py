from barcode import Code128
from barcode.writer import SVGWriter


class CustomSVGWriter(SVGWriter):
    top_text = None

    def _init(self, code):
        print(self.top_text)
        super()._init(code)

    # def _create_module(self, xpos, ypos, width, color):
    #     print(f"Create Module {xpos}")
    #
    # def _create_text(self, xpos, ypos):
    #     print("Create Text")


# Custom writer options
options = {
    'module_width': 0.4,  # Width of each barcode module
    'module_height': 8.0,  # Height of each barcode module
    'quiet_zone': 0.5,  # Quiet zone around the barcode
    'font_size': 4.5,  # Size of the text
    'text_distance': 2.5,  # Distance between barcode and text
    'background': 'white',  # Background color
    'foreground': 'black',  # Foreground color (bars and text)
    'center_text': True,  # Center the text below barcode
    'write_text': True,
    'margin_bottom': 50,
    'margin_top': 10,
    'human': "Human Readable Text \n abc \n cef",
    'top_text': "My Top Text",
}

# Create barcode with custom options
barcode = Code128('PYTHON-123', writer=CustomSVGWriter())

# Save with custom filename
filename = barcode.save(f"tmp/svg-custom", options)

print(f"Custom barcode saved as {filename}.svg")
