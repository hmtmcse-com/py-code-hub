from escpos.printer import Usb


def print_document():
    p = Usb(0x4b43, 0x3538, 0, out_ep=0x03)  # (vendor_id, product_id, interface, in_ep, out_ep)
    p.set(align='center', font='a', width=2, height=2)
    p.text("Hello from HS-K24!\n")
    p.set(align='left', font='a', width=1, height=1)
    p.text("Thank you for your purchase!\n")
    p.cut()


print_document()
