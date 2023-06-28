from lib.er302 import ER302
device = ER302('/dev/tty.usbserial-0001', 115200)
print('lets test!')
print(device.send_receive(0x10c,b'\0x01'))
print(device.select())