from barcode import Code128
from barcode.writer import ImageWriter
from barcode.writer import SVGWriter


def create_barcode_with_text(data, filename, text_on_top="", bottom_margin=5):
    # Create barcode object
    code = Code128(data, writer=ImageWriter())

    # Customize writer options
    options = {
        'module_width': 0.2,  # Width of each barcode bar
        'module_height': 5.0,  # Height of barcode bars
        'quiet_zone': 6.5,  # Quiet zone (white space) around the barcode
        'font_size': 4.5,  # Font size for the text
        'text_distance': 2.0,  # Distance between barcode and text
        'write_text': True,  # Disable default text below barcode
        'background': 'white',  # Background color
        'foreground': 'black',  # Bar color
        'format': 'PNG',  # Image format
        'dpi': 300,  # Dots per inch
    }

    # Save the barcode with custom options
    code.save(f"tmp/{filename}", options=options)

    # If you want to add text on top, you'll need to use PIL to modify the image
    from PIL import Image, ImageDraw, ImageFont
    import os

    # Open the generated barcode image
    img_path = f"tmp/{filename}.png"
    img = Image.open(img_path)

    # Create a new image with space for text on top
    font = ImageFont.load_default()  # You can load a specific font here
    text_height = 20  # Adjust based on your text size needs

    new_img = Image.new('RGB',
                        (img.width, img.height + text_height - bottom_margin),
                        'white')

    # Paste the barcode image at the bottom of the new image
    new_img.paste(img, (0, text_height))

    # Draw the text on top
    draw = ImageDraw.Draw(new_img)
    text_width = draw.textlength(text_on_top, font=font)
    draw.text(((img.width - text_width) / 2, 0),
              text_on_top,
              font=font,
              fill='black')

    # Save the final image
    new_img.save(img_path)
    file_path = f"tmp/{filename}.png"

    if os.path.exists(file_path):
        os.remove(file_path)  # Remove the original barcode image
    new_img.save(file_path)  # Save the modified version

    return img_path


# Example usage
create_barcode_with_text("123456789", "my_barcode", "Product ID", bottom_margin=10)
