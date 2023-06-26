import serial
import time

class ER302_RFID_Reader(object):

    BAUD_4800 = 4800
    BAUD_9600 = 9600
    BAUD_14400 = 14400
    BAUD_19200 = 19200
    BAUD_28800 = 28800
    BAUD_38400 = 38400
    BAUD_57600 = 57600
    BAUD_115200 = 115200
    LED_OFF = b'\x00'
    LED_BLUE = b'\x01'
    LED_RED = b'\x02'
    LED_BOTHON = b'\x03'
    TYPE_A = b'A' 

    RF_OFF = b'\x00'
    RF_ON = b'\x01'

    REQ_STD = b'\x26'
    REQ_ALL = b'\x52'

    KEY_A = b'\x60'
    KEY_B = b'\x61'

    DEBUG_MODE = False
    MUTE_MODE = False

    def __init__(self, port, baudrate):
        super(ER302_RFID_Reader, self).__init__()
        self.ser = serial.Serial(port, baudrate)
        self.rf_init_com()
        self.rf_init_device_number()
        self.rf_get_device_number()
        self.rf_init_type(self.TYPE_A)
        self.rf_antenna_sta()

    def info(self):
        print(self.ser)
        print(self.BAUD_115200)

    def debug(self, source):
        if self.DEBUG_MODE:
            if isinstance(source, list):
                output = []
                for i in range(0, len(source)):
                    output.insert(i, hex(source[i]))
            else:
                output = source
            print(output)
        else:
            return

    def xor_strings(self, b1, b2):
        parts = []
        for b1, b2 in zip(b1, b2):
            parts.append(bytes([b1 ^ b2]))
        return b''.join(parts)

    def read_response(self):
        all_output = []
        output = b''
        i = 0
        output = self.ser.read()
        while output != b'':
            if i == 0:
                pass
            else:
                output = self.ser.read()
            if (i == 8) and (output != b'\x00'):
                return False
            if output != b'':
                all_output.insert(i, output)
            i += 1
        self.ser.flushOutput()
        return all_output

    def send_request(self, dev_id, cmd_code, param):
        length = len(param) + 5
        ver = b'\x00'
        buf = bytearray
        buf.insert(0, b'\xAA')  # Command head
        buf.insert(1, b'\xBB')
        buf.insert(2, bytes([length]))  # Length
        buf.insert(3, b'\x00')
        buf.insert(4, dev_id[0])  # Device ID
        buf.insert(5, dev_id[1])
        buf.insert(6, cmd_code[0])  # Command code
        buf.insert(7, cmd_code[1])
        k = 0
        for i in range(8, 8 + len(param)):
            buf.insert(i, param[k])
            k += 1
        for i in range(3, len(buf)):
            ver = self.xor_strings(ver, buf[i])
        buf.insert(len(buf), ver)
        self.debug(buf)
        self.ser.write(buf)
        self.ser.flushInput()

    def rf_init_com(self):
        self.send_request([b'\x00', b'\x00'], [b'\x01', b'\x01'], [self.BAUD_115200])
        result = self.read_response()
        self.debug(result)
        return result

    def rf_get_model(self):
        self.send_request([b'\x00', b'\x00'], [b'\x04', b'\x01'], [])
        result = self.read_response()
        self.debug(result)
        return result

    def rf_init_device_number(self):
        self.send_request([b'\x00', b'\x00'], [b'\x02', b'\x01'], [b'\x11', b'\x12'])
        result = self.read_response()
        self.debug(result)
        return result

    def rf_get_device_number(self):
        self.send_request([b'\x00', b'\x00'], [b'\x03', b'\x01'], [])
        result = self.read_response()
        self.debug(result)
        return result

    def rf_beep(self, time):
        if not self.MUTE_MODE:
            self.send_request([b'\x00', b'\x00'], [b'\x06', b'\x01'], [bytes([time])])
            result = self.read_response()
            self.debug(result)
            return result

    def rf_light(self, color):
        self.send_request([b'\x00', b'\x00'], [b'\x07', b'\x01'], [color])
        result = self.read_response()
        self.debug(result)
        return result

    def rf_init_type(self, type):
        self.send_request([b'\x00', b'\x00'], [b'\x08', b'\x01'], [type])
        result = self.read_response()
        self.debug(result)
        return result

    def rf_antenna_sta(self):
        self.send_request([b'\x00', b'\x00'], [b'\x0c', b'\x01'], [self.RF_OFF])
        result = self.read_response()
        self.debug(result)
        return result

    def rf_request(self):
        self.send_request([b'\x00', b'\x00'], [b'\x01', b'\x02'], [b'\x52'])
        result = self.read_response()
        self.debug(result)
        return result

    def rf_anticoll(self):
        self.send_request([b'\x00', b'\x00'], [b'\x02', b'\x02'], [])
        result = self.read_response()
        self.debug(result)
        return result

    def rf_select(self, card_id):
        self.send_request([b'\x00', b'\x00'], [b'\x03', b'\x02'], card_id)
        result = self.read_response()
        self.debug(result)
        return result

    def rf_M1_authentication2(self, block, key):
        param = [b'\x60', bytes([block]), key[0], key[1], key[2], key[3], key[4], key[5]]
        self.send_request([b'\x00', b'\x00'], [b'\x07', b'\x02'], param)
        result = self.read_response()
        self.debug(result)
        return result

    def rf_read(self, block):
        self.send_request([b'\x00', b'\x00'], [b'\x08', b'\x02'], [bytes([block])])
        result = self.read_response()
        if result:
            self.debug(result)
            output = ''
            for i in range(9, len(result) - 1):
                output += str(result[i].hex())
            return output
        else:
            return 'Reading block is failed'

    def rf_M1_write(self, block, data):
        param = [bytes([block]), data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8],
                data[9], data[10], data[11], data[12], data[13], data[14], data[15]]
        self.send_request([b'\x00', b'\x00'], [b'\x09', b'\x02'], param)
        result = self.read_response()
        self.debug(result)
        return result

    def rf_M1_InitValue(self, block, data):
        param = [bytes([block]), data[0], data[1], data[2], data[3]]
        self.send_request([b'\x00', b'\x00'], [b'\x0a', b'\x02'], param)
        result = self.read_response()
        self.debug(result)
        return result

    def rf_M1_DecrementValue(self, block, data):
        param = [bytes([block]), data[0], data[1], data[2], data[3]]
        self.send_request([b'\x00', b'\x00'], [b'\x0c', b'\x02'], param)
        result = self.read_response()
        self.debug(result)
        return result

    def rf_M1_IncrementValue(self, block, data):
        param = [bytes([block]), data[0], data[1], data[2], data[3]]
        self.send_request([b'\x00', b'\x00'], [b'\x0d', b'\x02'], param)
        result = self.read_response()
        self.debug(result)
        return result

    ############## UL COMMANDS ######################
    def rf_UL_anticoll2(self):
        self.send_request([b'\x00', b'\x00'], [b'\x12', b'\x02'], [])
        result = self.read_response()  # Get 7 bytes long uid
        self.debug(result)
        return result

    def rf_UL_write(self, block, data):
        param = [bytes([block]), data[0], data[1], data[2], data[3]]
        self.send_request([b'\x00', b'\x00'], [b'\x13', b'\x02'], param)
        result = self.read_response()
        self.debug(result)
        return result

    #####################################

    def read_block(self, block):
        self.rf_light(self.LED_RED)
        if self.rf_request():
            result = self.rf_anticoll()
            if result:
                card_id = [result[9], result[10], result[11], result[12]]
                if self.rf_select(card_id):
                    if self.rf_M1_authentication2(block, self.key) != False:
                        self.rf_beep(1)
                        self.rf_light(self.LED_BLUE)
                        return self.rf_read(block)
                    else:
                        self.rf_beep(20)
                        self.rf_light(self.LED_RED)
                        return 'Authentication failed'
        else:
            self.rf_beep(20)
            self.rf_light(self.LED_RED)
            return 'Read block failured.'

    def set_key(self, key):
        self.key = key

    def close(self):
        self.ser.close()
