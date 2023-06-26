from rfid_er302 import ER302_RFID_Reader
import binascii
#reader = ER302_RFID_Reader('/dev/ttyUSB0', 115200)  #RaspberryPi usb
reader = ER302_RFID_Reader('/dev/tty.usbserial-0001', 115200)  #Windows usb VCP

#reader.DEBUG_MODE = True
# reader.MUTE_MODE = True
reader.set_key(b'\xFF\xFF\xFF\xFF\xFF\xFF')

#sound=reader.rf_beep(20)
for i in range(0,64,1):
    print("DATA BLOCK:"+str(i))
    card_data = reader.read_block(bytes(i))
    print(card_data)



reader.close()
