from rfid_er302 import ER302_RFID_Reader

#reader = ER302_RFID_Reader('/dev/ttyUSB0', 115200)  #RaspberryPi usb
reader = ER302_RFID_Reader('/dev/tty.usbserial-0001', 115200)  #Windows usb VCP
#reader.DEBUG_MODE = True
# reader.MUTE_MODE = True
#reader.set_key('\xFF\xFF\xFF\xFF\xFF\xFF')

sound=reader.rf_beep(0)

card_type = reader.rf_request()
card_M1_uid =  reader.rf_anticoll()
#card_type = ''.join([byte.hex() for byte in card_type])
#card_type = reader.rf_request()
# card_UL_uid =  reader.rf_UL_anticoll2()


print( card_type)
UUID = ''.join([byte.hex() for byte in card_M1_uid])
print(UUID)
# print(b''.join(card_M1_uid).decode('utf-8'))

# print(card_UL_uid)


reader.close()
