import qrcode


def generate_qr(data: str, filename: str = "qrcode.png", border: int = 4) -> None:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=border,
    )

    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    image.save(filename)


if __name__ == "__main__":
    generate_qr(
        "https://example.com",
        "qrcode.png",
        border=1,
    )

    print("QR code generated successfully.")