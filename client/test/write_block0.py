from rfid_er302 import ER302_RFID_Reader

#reader = ER302_RFID_Reader('/dev/ttyUSB0', 115200)  #RaspberryPi usb
reader = ER302_RFID_Reader('/dev/tty.usbserial-0001', 115200)  #Windows usb VCP

reader.DEBUG_MODE = True
# reader.MUTE_MODE = True
reader.set_key(b'\xFF\xFF\xFF\xFF\xFF\xFF')

#sound=reader.rf_beep(20)
str = "TEST"
data = str.encode('utf-8')
while len(data) < 16:
            data += b"\x00"
print(data)
byte_array = []
for byte in data:
    byte_array.append(chr(byte).encode())

print("Write:")
print(byte_array)
card_data = reader.rf_M1_write(b'4',byte_array)

print(card_data)


reader.close()
