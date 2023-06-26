from pyembedded.rfid_module.rfid import RFID
rfid = RFID(port='/dev/tty.usbserial-0001', baud_rate=115200)
print(rfid.get_id())