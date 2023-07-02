##!/usr/bin/python

import datetime
import os
import sys
import struct
from functools import reduce
import serial

# Command header
HEADER = b'\xAA\xBB'
# \x00\x00 according to API reference but only works with YHY632
# \xFF\xFF works for both.
RESERVED = b'\x00\x00'

# Serial commands
CMD_SET_BAUDRATE = 0x0101
CMD_SET_NODE_NUMBER = 0x0102
CMD_READ_NODE_NUMBER = 0x0103
CMD_READ_FW_VERSION = 0x0104
CMD_BEEP = 0x0106
CMD_LED = 0x0107
CMD_RFU = 0x0108  # Unused according to API reference
CMD_WORKING_STATUS = 0x0108  # Unused according to API reference
CMD_ANTENNA_POWER = 0x010C
# Request a type of card
#     data = 0x52: request all Type A card In field,
#     data = 0x26: request idle card
CMD_MIFARE_REQUEST = 0x0201
CMD_MIFARE_ANTICOLISION = 0x0202  # 0x04 -> <NUL> (00)     [4cd90080]-cardnumber
CMD_MIFARE_SELECT = 0x0203  # [4cd90080] -> 0008
CMD_MIFARE_HALT = 0x0204
CMD_MIFARE_AUTH2 = 0x0207  # 60[sector*4][key]
CMD_MIFARE_READ_BLOCK = 0x0208  # [block_number]
CMD_MIFARE_WRITE_BLOCK = 0x0209
CMD_MIFARE_INITVAL = 0x020A
CMD_MIFARE_READ_BALANCE = 0x020B
CMD_MIFARE_DECREMENT = 0x020C
CMD_MIFARE_INCREMENT = 0x020D
CMD_MIFARE_UL_SELECT = 0x0212

# Default keys
DEFAULT_KEYS = (
    b'\x00\x00\x00\x00\x00\x00',
    b'\xa0\xa1\xa2\xa3\xa4\xa5',
    b'\xb0\xb1\xb2\xb3\xb4\xb5',
    b'\x4d\x3a\x99\xc3\x51\xdd',
    b'\x1a\x98\x2c\x7e\x45\x9a',
    b'\xFF'*6,
    b'\xd3\xf7\xd3\xf7\xd3\xf7',
    b'\xaa\xbb\xcc\xdd\xee\xff'
)

# Error codes
ERR_BAUD_RATE = 1
ERR_PORT_OR_DISCONNECT = 2
ERR_GENERAL = 10
ERR_UNDEFINED = 11
ERR_COMMAND_PARAMETER = 12
ERR_NO_CARD = 13
ERR_REQUEST_FAILURE = 20
ERR_RESET_FAILURE = 21
ERR_AUTHENTICATE_FAILURE = 22
ERR_READ_BLOCK_FAILURE = 23
ERR_WRITE_BLOCK_FAILURE = 24
ERR_READ_ADDRESS_FAILURE = 25
ERR_WRITE_ADDRESS_FAILURE = 26

# Mifare types
TYPE_MIFARE_UL = 0x4400
TYPE_MIFARE_1K = 0x0400
TYPE_MIFARE_4K = 0x0200
TYPE_MIFARE_DESFIRE = 0x4403
TYPE_MIFARE_PRO = 0x0800


class ER302:
    """Driver for Ehuoyan's YHY523U module"""

    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.status = False
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(self.port, baudrate=self.baudrate, timeout=0.2, stopbits=1)

    # def build_command(self, cmd, data):
    #     """Build a serial command.

    #     Keyword arguments:
    #     cmd -- the serial command
    #     data -- the argument of the command

    #     """
    #     length = 2 + 2 + 1 + len(data)

    #     body_raw = RESERVED + struct.pack('<H', cmd) + data
    #     body = b''
    #     for b in body_raw:
    #         body += bytes([b])
    #         if b == 0xAA:
    #             body += b'\x00'

    #     body_int = list(map(ord, body))
    #     checksum = reduce(lambda x, y: x ^ y, body_int)

    #     return HEADER + struct.pack('<H', length) + body + struct.pack('B', checksum)
    def calculate_xor_checksum(self, byte_array):
        checksum = 0
        for byte in byte_array:
            checksum ^= byte
        return checksum
    
    def build_command(self, cmd, data,checksum_req = True):
        """Build a serial command.

        Keyword arguments:
        cmd -- the serial command
        data -- the argument of the command

        """
        length = 2 + 2 + 1 + len(data)

        body_raw = RESERVED + struct.pack('<H', cmd) + data
        # print("RAW: ",body_raw)
        body = b''
        for b in body_raw:
             body += struct.pack('B',b)
             print(struct.pack('B',b))
             if b == 0xAA:
                 body += b'\x00'
        print("body: ",body)
        body_int = list(body)
        checksum = self.calculate_xor_checksum(body)
        if checksum_req:
            send_buffer = HEADER + struct.pack('<H', length) + body + struct.pack('B', checksum)
        else:
            send_buffer = HEADER + struct.pack('<H', length) + body 
            
        print("SEND: ",send_buffer)
        return send_buffer

    def get_n_bytes(self, n, handle_AA=False):
        """Read n bytes from the device.

        Keyword arguments:
        n -- the number of bytes to read
        handle_AA -- True to handle \xAA byte differently, False otherwise

        """
        buffer = bytearray()
        while True:
            received = self.ser.read()
            # print("REC: ",received.hex())
            # print('receive buff:',to_hex(buffer))
            if handle_AA:
                 if buffer.find(b'\xAA\x00') >= 0:
                     buffer = buffer.replace(b'\xAA\x00', b'\xAA')
                 if received[0] == 0x00 and buffer[-1:] == 0xAA:
                     received = received[1:]
            buffer += received

            if len(buffer) >= n:
                return buffer

    def send_command(self, cmd, data):
        """Send a serial command to the device.

        Keyword arguments:
        cmd -- the serial command
        data -- the argument of the command

        """
        #print("SEND cmd,data:",to_hex(cmd),to_hex(data))
        buffer = self.build_command(cmd, data)
        # print("SEND buffer:",to_hex(buffer))
        self.ser.write(buffer)
        self.ser.flush()

    # def receive_data(self):
    #     """Receive data from the device."""
    #     buffer = b''

    #     # Receive junk bytes
    #     prev_byte = b'\x00'
    #     while True:
    #         cur_byte = self.ser.read(1)
    #         if prev_byte + cur_byte == HEADER:
    #             # Header found, breaking
    #             break
    #         prev_byte = cur_byte

    #     length = struct.unpack('<H', self.get_n_bytes(2))[0]
    #     packet = self.get_n_bytes(length, True)

    #     reserved, command = struct.unpack('<HH', packet[:4])
    #     data = packet[4:-1]
    #     checksum = ord(packet[-1])

    #     packet_int = list(map(ord, packet[:-1]))
    #     checksum_calc = reduce(lambda x, y: x ^ y, packet_int)
    #     if data[0] == 0x00:
    #         if checksum != checksum_calc:
    #             raise Exception("bad checksum")
    #     return command, data
    def receive_data(self):
        """Receive data from the device."""
        buffer = b''

        # Receive junk bytes
        prev_byte = b'\x00'
        while True:
            cur_byte = self.ser.read(1)
            # print(cur_byte)
            if prev_byte + cur_byte == HEADER:
                # Header found, breaking
                break
            prev_byte = cur_byte

        length = struct.unpack('<H', self.get_n_bytes(2))[0]
        # print('receive lenght:',length)
        packet = self.get_n_bytes(length,True)
        
        print('receive packet:',to_hex(packet))
        reserved, command = struct.unpack('<HH', packet[:4])
        data = packet[4:-1]
        checksum = packet[-1]  # No need for ord() conversion
        # print('receive data:',to_hex(data))
        # print('receive checksum:',checksum)
        packet_int = list(packet[:-1])  # Remove map(ord, ...)
        checksum_calc = reduce(lambda x, y: x ^ y, packet_int)
        if data[0] == 0x00:
            if checksum != checksum_calc:
                raise Exception("bad checksum")
        return command, data


    def send_receive(self, cmd, data):
        """Send a serial command to the device and receive the answer.

        Keyword arguments:
        cmd -- the serial command
        data -- the argument of the command

        """
        self.send_command(cmd, data)
        cmd_received, data_received = self.receive_data()
        if cmd_received != cmd:
            raise Exception("the command in answer is bad!")
        else:
            return data_received[0], data_received[1:]


    def select(self):
        """Wählt eine Mifare-Karte aus. (Erforderlich vor jeder Lese- / Schreiboperation)
        Gibt den Typ und die Seriennummer einer Mifare-Karte zurück.

        """
        status, card_type = self.send_receive(CMD_MIFARE_REQUEST, b'\x52')
        if status != 0:
            raise Exception("Keine Karte gefunden")

        status, serial = self.send_receive(CMD_MIFARE_ANTICOLISION, b'\x04')
        if status != 0:
            raise Exception("Fehler bei der Antikollision")

        card_type = struct.unpack('>H', card_type)[0]
        if card_type == TYPE_MIFARE_UL:
            status, serial = self.send_receive(CMD_MIFARE_UL_SELECT, '')
        else:
            status, serial = self.send_receive(CMD_MIFARE_SELECT, serial)
        if status != 0:
            raise Exception("Fehler bei SELECT")
        return card_type, serial

    def halt(self):
        """Stoppt das Gerät."""
        status, data = self.send_receive(CMD_MIFARE_HALT, b'')
        return status, data

    def read_sector(self, sector=0, keyA=b'\xff'*6, blocks=(0,1,2,)):
        """Liest einen Sektor einer Mifare-Karte aus.

        Schlüsselwort-Argumente:
        sector -- der Sektorindex (Standard: 0)
        keyA -- der Schlüssel A
        blocks -- die zu lesenden Blöcke im Sektor

        """
        self.send_receive(CMD_MIFARE_AUTH2, b'\x60' +  int_tohex(sector *4) + keyA)
        results = ''
        for block in blocks:
            status, data = self.send_receive(CMD_MIFARE_READ_BLOCK, int_tohex(sector * 4 + block))
            if status != 0:
                raise Exception("Fehlercode: %d" % status)
            results += data
        return results

    def write_block(self, sector=0, keyA=b'\xff'*6, block=0, data=b'\x00'*16):
        """Schreibt in einen Block einer Mifare-Karte.

        Schlüsselwort-Argumente:
        sector -- der Sektorindex (Standard: 0)
        keyA -- der Schlüssel A
        block -- der zu beschreibende Block im Sektor (Standard: 0)
        data -- der zu schreibende Datenstring

        """
        self.send_receive(CMD_MIFARE_AUTH2, b'\x60' + int_tohex(sector *4) + keyA)
        status, result = self.send_receive(CMD_MIFARE_WRITE_BLOCK,int_tohex(sector *4 + block) + data)
        if status != 0:
            raise Exception("Fehlercode: %d" % status)
        return result

    def dump(self, keyA=b'\xff'*6):
        """Dump einer Mifare-Karte.

        Schlüsselwort-Argumente:
        keyA -- der Schlüssel A

        """
        self.select()
        for sector in range(0, 16):
            print("Sektor %d" % sector)
            try:
                print(to_hex(self.read_sector(sector, keyA)))
            except:
                pass

    def dump_access_conditions(self, keyA=b'\xff'*6):
        """Dump der Zugriffsbedingungen (AC) einer Mifare-Karte.

        Schlüsselwort-Argumente:
        sector -- der Sektorindex (Standard: 0)
        keyA -- der Schlüssel A

        """
        self.select()
        for sector in range(0, 16):
            try:
                ac = buffer(self.read_sector(sector, keyA, (3,)), 6, 3)
                print("ACs für Sektor %d:" % sector, to_hex(ac))
            except:
                print("Zugriffsbedingungen für Sektor %d konnten nicht gelesen werden" % sector)

    def get_fw_version(self):
        """Gibt die Firmware-Version des Geräts zurück."""
        status, data = self.send_receive(CMD_READ_FW_VERSION, b'\x00')
        return data

    def get_node_number(self):
        """Gibt die Knotennummer des Geräts zurück."""
        status, data = self.send_receive(CMD_READ_NODE_NUMBER, b'\x00')
        return data

    def set_node_number(self, number):
        """Setzt die Knotennummer des Geräts.

        Schlüsselwort-Argumente:
        number -- die Knotennummer

        """
        status, data = self.send_receive(CMD_SET_NODE_NUMBER, struct.pack('<H', number))
        return data

    def beep(self, delay=10):
        """Lässt das Gerät piepen.

        Schlüsselwort-Argumente:
        delay -- die Piep-Dauer in Millisekunden (Standard: 10)

        """
        status, data = self.send_receive(CMD_BEEP, struct.pack('<H', delay))
        if status == 0:
            return 1
        else:
            return 0


    def set_led(self, led='off'):
        """Schaltet die LED des Geräts ein.

        Schlüsselwort-Argumente:
        led -- die zu beleuchtende LED, kann sein: 'red', 'blue', 'both' oder 'off' (Standard: 'off')

        """
        if led == 'red':
            data = b'\x02'
        elif led == 'blue':
            data = b'\x01'
        elif led == 'both':
            data = b'\x03'
        else:
            data = b'\x00'
        return self.send_receive(CMD_LED, data)[0]

    def set_baudrate(self, rate=19200):
        """Setzt die Baudrate des Geräts.

        Schlüsselwort-Argumente:
        rate -- die Baudrate (Standard: 19200)

        """
        if rate == 19200:
            data = b'\x03'
        elif rate == 28800:
            data = b'\x04'
        elif rate == 38400:
            data = b'\x05'
        elif rate == 57600:
            data = b'\x06'
        elif rate == 115200:
            data = b'\x07'
        else:
            data = b'\x01'
        return self.send_receive(CMD_SET_BAUDRATE, data)[0] == 0

    def init_balance(self, sector=0, keyA='\xff'*6, block=0, amount=1):
        """Initialisiert einen Kontostand auf einer Mifare-Karte.

        Schlüsselwort-Argumente:
        sector -- der Sektorindex (Standard: 0)
        keyA -- der Schlüssel A
        block -- der zu beschreibende Block im Sektor (Standard: 0)
        amount -- der anfängliche Kontostand (Standard: 1)

        """
        self.send_receive(CMD_MIFARE_AUTH2, b'\x60' + chr(sector * 4) + keyA)
        status, result = self.send_receive(CMD_MIFARE_INITVAL, chr(sector * 4 + block) + struct.pack("I", amount))
        if status != 0:
            raise Exception("Fehlercode: %d" % status)
        return result

    def read_balance(self, sector=0, keyA='\xff'*6, block=0):
        """Liest einen Kontostand.

        Schlüsselwort-Argumente:
        sector -- der Sektorindex (Standard: 0)
        keyA -- der Schlüssel A
        block -- der zu lesende Block im Sektor (Standard: 0)

        """
        self.send_receive(CMD_MIFARE_AUTH2, b'\x60' + int_tohex(sector * 4) + keyA)
        status, result = self.send_receive(CMD_MIFARE_READ_BALANCE, int_tohex(sector * 4 + block))
        if status != 0:
            raise Exception("Fehlercode: %d" % status)
        return result

    def decrease_balance(self, sector=0, keyA=b'\xff'*6, block=0, amount=1):
        """Verringert einen Kontostand um einen Betrag.

        Schlüsselwort-Argumente:
        sector -- der Sektorindex (Standard: 0)
        keyA -- der Schlüssel A
        block -- der zu beschreibende Block im Sektor (Standard: 0)
        amount -- der zu verringernde Betrag (Standard: 1)

        """
        self.send_receive(CMD_MIFARE_AUTH2, b'\x60' + int_tohex(sector * 4) + keyA)
        status, result = self.send_receive(CMD_MIFARE_DECREMENT, int_tohex(sector * 4 + block) + struct.pack("I", amount))
        if status != 0:
            raise Exception("Fehlercode: %d" % status)
        return result

    def increase_balance(self, sector=0, keyA=b'\xff'*6, block=0, amount=1):
        """Erhöht einen Kontostand um einen Betrag.

        Schlüsselwort-Argumente:
        sector -- der Sektorindex (Standard: 0)
        keyA -- der Schlüssel A
        block -- der zu beschreibende Block im Sektor (Standard: 0)
        amount -- der zu erhöhende Betrag (Standard: 1)

        """
        self.send_receive(CMD_MIFARE_AUTH2, b'\x60' + int_tohex(sector * 4) + keyA)
        status, result = self.send_receive(CMD_MIFARE_INCREMENT, int_tohex(sector * 4 + block) + struct.pack("I", amount))
        if status != 0:
            raise Exception("Fehlercode: %d" % status)
        return result

    def test_keys(self, sector=0, keys=DEFAULT_KEYS):
        """Testet ein Array potenzieller Schlüssel, um den richtigen zu finden.

        Schlüsselwort-Argumente:
        sector -- der Sektorindex (Standard: 0)
        keys -- die zu testenden Schlüssel (Standard: DEFAULT_KEYS)

        """
        for key in keys:
            self.select()
            status, data = self.send_receive(CMD_MIFARE_AUTH2, b'\x60' + (sector * 4).to_bytes(byteorder='big') + key)
            if status == 0:
                print("Schlüssel A gefunden:", to_hex(key))
                break
            else:
                print("Ungültiger Schlüssel A:", to_hex(key))

        for key in keys:
            self.select()
            status, data = self.send_receive(CMD_MIFARE_AUTH2, b'\x61' + (sector * 4).to_bytes(byteorder='big') + key)
            if status == 0:
                print("Schlüssel B gefunden:", to_hex(key))
                break
            else:
                print("Ungültiger Schlüssel B:", to_hex(key))

def int_tohex(n, minlen=0):
    """ Convert integer to bytearray with optional minimum length. 
    """
    #b = bytes([n])
    #b = n.to_bytes( byteorder='big')
    b = struct.pack('<H', n)
    # b = pack('bhl', n)
    # print("input:",n)
    # print("output:",b)
    return b

def to_hex(cmd):
    """Gibt die hexadezimale Version eines seriellen Befehls zurück.

    Schlüsselwort-Argumente:
    cmd -- der serielle Befehl

    """
    hex_values = [f"{byte:02X}" for byte in cmd]

    # Formatierung im gewünschten Format
    formatted_output = " ".join(hex_values)
    return formatted_output
    #return ' '.join([hex(ord(c))[2:].zfill(2) for c in cmd])

    
#if __name__ == '__main__':

    # Erstellen des Geräts
    # device = YHY523U('/dev/tty.usbserial-0001', 115200)
    # print('lets test!')
    #device.select()
    # device.set_node_number(b'\x51\x52')
    # Einschalten der blauen LED
    #device.set_led('red')
    # Piepen für 10 ms
    #device.beep(10)
    # Einschalten beider LEDs
    # device.set_led('blue')
    
    # Drucken der Firmware-Version
    # print(device.get_fw_version())

    # Versuch, die Karte mit verschiedenen hexadezimalen Schlüsseln A auszulesen
    # device.dump()
    # device.dump(b'\xA0\xA1\xA2\xA3\xA4\xA5')
    # device.dump(b'\x8f\xd0\xa4\xf2\x56\xe9')
    # # Versuch, die Karte mit \xFF\xFF\xFF\xFF\xFF\xFF auszulesen
    

    # # Versuch, die Zugriffsbedingungen der Karte mit \xFF\xFF\xFF\xFF\xFF\xFF auszulesen
    # # device.select()
    # device.dump_access_conditions()

    # # Drucken des Kartentyps und der Seriennummer
    # card_type, serial = device.select()
    # print("Kartentyp:", card_type, "- Seriennummer:", to_hex(serial))

    # Drucken des Speicherinhalts der Blöcke 0 und 1 des Sektors 0
    # mit dem Schlüssel A \xFF\xFF\xFF\xFF\xFF\xFF
    # device.select()
    # print(to_hex(device.read_sector(0, b'\xff\xff\xff\xff\xff\xff', (0,1))))
    # Lesen des Sektors: 2, Blöcke: 0, 1
    # device.select()
    # print(to_hex(device.read_sector(2, b'\xA0\xA1\xA2\xA3\xA4\xA5', (0,1,))))

    # Schleife zum Lesen von Karten
    # import time
    # while 1:
    #     try:
    #         card_type, serial = device.select()
    #         print("Kartentyp:", card_type, "- Seriennummer:", to_hex(serial))
    #     except KeyboardInterrupt:
    #         raise KeyboardInterrupt
    #     except:
    #         pass
    #     time.sleep(0.1)

    # Lesen-Schreiben-Lesen-Schreiben-Lesen
    # Lesen des Sektors: 4, Blöcke: 2, 3
    # device.select()
    # print(to_hex(device.read_sector(4, b'\xA0\xA1\xA2\xA3\xA4\xA5', (2, 3))))
    # device.write_block(4, b'\xA0\xA1\xA2\xA3\xA4\xA5', 2, b'\x01\x23\x45\x67'*4)
    # print(to_hex(device.read_sector(4, b'\xA0\xA1\xA2\xA3\xA4\xA5', (2, 3))))
    # device.write_block(4, b'\xA0\xA1\xA2\xA3\xA4\xA5', 2, b'\x00'*16)
    # print(to_hex(device.read_sector(4, b'\xA0\xA1\xA2\xA3\xA4\xA5', (2, 3))))

    # Lesen-Schreiben-Lesen-Schreiben-Lesen-Schreiben-Lesen
    # Spielen mit einem Kontostand im Sektor: 7, Block: 1
    #device.select()
    # print("Kontostand:", struct.unpack("4b", device.read_balance(7, b'\xff'*6, 1)))
    # device.init_balance(7, b'\xff'*6, 1, 42)
    # print("Kontostand:", struct.unpack("4b", device.read_balance(7, b'\xff'*6, 1)))
    # device.decrease_balance(7, b'\xff'*6, 1, 3)
    # print("Kontostand:", struct.unpack("4b", device.read_balance(7, b'\xff'*6, 1)))
    # device.increase_balance(7, b'\xff'*6, 1, 2)
    # print("Kontostand:", struct.unpack("4b", device.read_balance(7, b'\xff'*6, 1)))

    # Testen eines Satzes von Standard-Schlüsseln
    # device.test_keys()

    # Weitere Tests
    #print(device.send_receive(CMD_WORKING_STATUS, b'\x01\x01'))
