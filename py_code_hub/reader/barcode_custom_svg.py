from barcode import Code128
from barcode.writer import SVGWriter, create_svg_object, SIZE, _set_attributes, COMMENT, pt2mm


class CustomSVGWriter(SVGWriter):
    top_text = None
    text_align = "middle"
    barcode_start_x = None
    barcode_y = None
    margin_top = None
    actual_margin_top = None
    top_text_distance: float = 0.5
    top_text_height: float = 0.0

    '''
    This methods copied from SVGWriter for generate top text
    we have to change the height width for print the barcode
    '''
    def parent_init(self, width, height):
        self._document = create_svg_object(self.with_doctype)
        self._root = self._document.documentElement
        attributes = {
            "width": SIZE.format(width),
            "height": SIZE.format(height),
        }
        _set_attributes(self._root, **attributes)
        if COMMENT:
            self._root.appendChild(self._document.createComment(COMMENT))
        # create group for easier handling in 3rd party software
        # like corel draw, inkscape, ...
        group = self._document.createElement("g")
        attributes = {"id": "barcode_group"}
        _set_attributes(group, **attributes)
        self._group = self._root.appendChild(group)
        background = self._document.createElement("rect")
        attributes = {
            "width": "100%",
            "height": "100%",
            "style": f"fill:{self.background}",
        }
        _set_attributes(background, **attributes)
        self._group.appendChild(background)

    def _init(self, code):
        width, height = self.calculate_size(len(code[0]), len(code))
        self.actual_margin_top = self.margin_top
        if self.top_text:
            self.top_text_height = pt2mm(self.font_size) + self.top_text_distance
            self.margin_top += self.top_text_height
            height += self.top_text_height
        self.parent_init(width=width, height=height)

    def _create_text_element(self, xpos, ypos, text, text_align="middle"):
        element = self._document.createElement("text")
        attributes = {
            "x": SIZE.format(xpos),
            "y": SIZE.format(ypos),
            "style": "fill:{};font-size:{}pt;text-anchor:{};".format(
                self.foreground,
                self.font_size,
                text_align
            ),
        }
        _set_attributes(element, **attributes)
        text_element = self._document.createTextNode(text)
        element.appendChild(text_element)
        self._group.appendChild(element)

    def _create_module(self, xpos, ypos, width, color):
        if not self.barcode_start_x:
            self.barcode_start_x = xpos
        self.barcode_y = ypos
        super()._create_module(xpos=xpos, ypos=ypos, width=width, color=color)


    '''
    Overwrite this method due to human text alignment,
    '''

    def _create_text(self, xpos, ypos):
        barcodetext = self.human if self.human != "" else self.text
        if self.text_align == "start":
            xpos = self.barcode_start_x
        if self.top_text:
            top_ypos = self.margin_top - self.top_text_distance
            self._create_text_element(text=self.top_text, xpos=xpos, ypos=top_ypos, text_align=self.text_align)

        for subtext in barcodetext.split("\n"):
            self._create_text_element(xpos=xpos, ypos=ypos, text=subtext, text_align=self.text_align)
            ypos += pt2mm(self.font_size) + self.text_line_distance


# Custom writer options
options = {
    'module_width': 0.2,  # Width of each barcode module
    'module_height': 8.0,  # Height of each barcode module
    'quiet_zone': 1,  # Quiet zone around the barcode
    'font_size': 6,  # Size of the text
    'text_distance': 2.8,  # Distance between barcode and text
    'background': 'white',  # Background color
    'foreground': 'black',  # Foreground color (bars and text)
    'center_text': True,  # Center the text below barcode
    'write_text': True,
    'margin_bottom': 0,
    'margin_top': 0,
    # 'human': "Human Readable Text",
    'text_align': 'start',  # middle and start
    'top_text': "My Top Text",
    'top_text_distance': 1,
}

# Create barcode with custom options
barcode = Code128('PYTHON-123', writer=CustomSVGWriter())

# Save with custom filename
filename = barcode.save(f"tmp/svg-custom", options)

print(f"Custom barcode saved as {filename}.svg")
