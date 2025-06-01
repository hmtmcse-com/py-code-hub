from escpos.printer import Usb


def print_document():
    printer = Usb(0x4b43, 0x3538, 0, 0x81, 0x03)
    printer.text('\x1b\x40')
    printer.text('\x1b\x64\x00')
    printer.text("\n" + "This is test print" + "\n")
    printer.cut('\x1d\x64')


print_document()
