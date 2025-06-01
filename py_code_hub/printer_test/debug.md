
```bash
lsusb # find the code
# Output
# Bus 001 Device 005: ID 4b43:3538 HSPOS HS-K24

# Find In Out
lsusb -vvv -d 4b43:3538
# p = Usb(0x4b43, 0x3538, 0, 0x81, 0x03) 

```