from rfid_er302 import ER302_RFID_Reader
from time import sleep

#reader = SL500_RFID_Reader('/dev/ttyUSB0',19200)  #RaspberryPi usb
#reader = SL500_RFID_Reader('COM3', 115200)  #Windows usb VCP

def main():
	try:
		reader = ER302_RFID_Reader('/dev/tty.usbserial-0001', 115200)
		#reader = SL500_RFID_Reader('/dev/ttyUSB0',115200)
	except:
		print('No RFID Reader')
		return	

	#print reader
	# reader.DEBUG_MODE = True
	# reader.MUTE_MODE = True
	reader.set_key(b'\xFF\xFF\xFF\xFF\xFF\xFF')


	try:
		card_data = reader.read_block(0)
	except:
		print('No RFID Card')
		return	

	print(card_data)
	reader.close()


if __name__ == '__main__':
	while(1):
		main()
		sleep(1) #1 second


