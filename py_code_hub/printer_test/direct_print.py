from escpos import *


def print_document():
    p = printer.Usb(0x4b43, 0x3538, 0, 0x81, 0x02)  # (vendor_id, product_id, interface, in_ep, out_ep)
    p.set(align='center', font='a', width=2, height=2)
    p.text("Hello from HS-K24!\n")
    p.set(align='left', font='a', width=1, height=1)
    p.text("Thank you for your purchase!\n")
    p.cut()


print_document()
