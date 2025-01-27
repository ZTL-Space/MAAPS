import smartcard.System
from smartcard.util import toHexString
from smartcard.ATR import ATR
import math
from . import utils, option, error
DEFAULT_KEYS = [
    [0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
    [0xa0, 0xa1, 0xa2, 0xa3, 0xa4, 0xa5],
    [0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5],
    [0x4d, 0x3a, 0x99, 0xc3, 0x51, 0xdd],
    [0x1a, 0x98, 0x2c, 0x7e, 0x45, 0x9a],
    [0xaa, 0xab, 0xac, 0xad, 0xae, 0xaf],
    [0xd3, 0xf7, 0xd3, 0xf7, 0xd3, 0xf7],
    [0xaa, 0xbb, 0xdd, 0xcc, 0xee, 0xff],
]

class Reader:
    def __init__(self):
        """create an ACR122U object
        doc available here: http://downloads.acs.com.hk/drivers/en/API-ACR122U-2.02.pdf"""
        self.reader_name, self.connection = self.instantiate_reader()
        self.load_authentication_data(0x01,DEFAULT_KEYS[1])
        self.load_authentication_data(0x00,DEFAULT_KEYS[1])

    @staticmethod
    def instantiate_reader():
        readers = smartcard.System.readers()

        if len(readers) == 0:
            raise error.NoReader("No readers available")

        reader = readers[0]
        c = reader.createConnection()

        try:
            c.connect()
        except:
            raise error.NoCommunication(
                "The reader has been deleted and no communication is now possible. Smartcard error code : 0x7FEFFF97"
                "\nHint: try to connect a card to the reader")
        
        return reader, c

    def command(self, mode, arguments=None):
        """send a payload to the reader

        Format:
            CLA INS P1 P2 P3 Lc Data Le

        The Le field (optional) indicates the maximum length of the response.
        The Lc field indicates the length of the outgoing data.

        Mandatory:
            CLA INS P1 P2

        Attributes:
            mode: key value of option.options or option.alias
            arguments: replace `-1` in the payload by arguments

        Returns:
            return the data or sw1 sw2 depending on the request"""
        mode = option.alias.get(mode) or mode
        payload = option.options.get(mode)

        if not payload:
            raise error.OptionOutOfRange("Option do not exist\nHint: try to call help(nfc.Reader().command) to see all options")

        payload = utils.replace_arguments(payload, arguments)
        result = self.connection.transmit(payload)

        if len(result) == 3:
            data, sw1, sw2 = result
        else:
            data, n, sw1, sw2 = result

        if [sw1, sw2] == option.answers.get("fail"):
            #return "ERROR"
            raise error.InstructionFailed(f"Instruction {mode} failed")

        elif [sw1, sw2] != option.answers.get("success"):
            return sw1, sw2
        else:
            print(f"success: {mode}")

        if data:
            return data
        

    def custom(self, payload):
        """send a custom payload to the reader

        Format:
            CLA INS P1 P2 P3 Lc Data Le"""
        result = self.connection.transmit(payload)

        if len(result) == 3:
            data, sw1, sw2 = result
        else:
            data, n, sw1, sw2 = result

        if [sw1, sw2] == option.answers.get("fail"):
            raise error.InstructionFailed(f"Payload {payload} failed")

    def get_uid(self):
        """get the uid of the card"""
        return self.command("get_uid")

    def firmware_version(self):
        """get the firmware version of the reader"""
        return self.command("firmware_version")

    def load_authentication_data(self, key_location, key_value):
        """load the authentication key

        Attributes:
            key location : 0x00 ~ 0x01
            key value : 6 bytes

        Example:
            E.g. 0x01, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]"""
        self.command("load_authentication_data", [key_location, key_value])

    def authentication(self, block_number, key_type, key_location):
        """authentication with the key in `load_authentication_data`

        Attributes:
            block number : 1 byte
            key type A/B : 0x60 ~ 0x61
            key location : 0x00 ~ 0x01

        Example:
            E.g. 0x00, 0x61, 0x01"""
        self.command("authentication", [block_number, key_type, key_location])

    def read_binary_blocks(self, block_number, number_of_byte_to_read):
        """read n bytes in the card at the block_number index

        Attributes:
            block number : 1 byte
            number of Bytes to read : 1

        Example:
            E.g. 0x00, 0x02"""
        return self.command("read_binary_blocks", [block_number, number_of_byte_to_read])

    def update_binary_blocks(self, block_number, number_of_byte_to_update, block_data):
        """update n bytes in the card with block_data at the block_number index

        Attributes:
            block number : 1 byte
            number of Bytes to update : 1-16 bytes
            block data : 4-16 bytes

        Examples:
            0x01, 0x10, [0x00, 0x01, 0x02, 0x03, 0x04, 0x05
            0x07, 0x08, 0x09, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15]"""
        self.command("update_binary_blocks",[block_number, number_of_byte_to_update, block_data]
        )

    def create_value_block(self, block_number, value):
        """Create value block at given block number with given 4-byte signed long integer value

        Attributes:
            block number : 1 byte
            value : 4 bytes, signed long integer

        Example:
            0x02, [0xFF, 0xFF, 0xFF, 0xFC] : 4 byte signed long integer value -4 at block 2
        """
        self.command("create_value_block", [block_number, value])

    def increment_value_block(self, block_number, value):
        """Increment value block at given block number with given 4-byte signed long integer value

        Attributes:
            block number : 1 byte
            value : 4 bytes, signed long integer

        Example:
            0x02, [0x00, 0x00, 0x00, 0x01] : increment stored value at value block 2 by 1
        """
        self.command("increment_value_block", [block_number, value])

    def decrement_value_block(self, block_number, value):
        """Decrement value block at given block number with given 4byte signed long integer value

        Attributes:
            block number : 1 byte
            value : 4 bytes, signed long integer

        Example:
            0x02, [0x00, 0x00, 0x00, 0x01] : decrement stored value at value block 2 by 1
        """
        self.command("decrement_value_block", [block_number, value])

    def read_value_block(self, block_number):
        """Read value block at given block number

        Attributes:
            block number : 1 byte (0-63)

        Example:
            0x01"""
        return self.command("read_value_block", [block_number])

    def restore_value_block(self, source_block_number, target_block_number):
        """Copies a value from a value block to another value block

        Attributes:
            source_block_number : 1 byte, source block number (0-63)
            target_block_number : 1 byte, target block number (0-63)

        Example:
            0x01, 0x02"""
        self.command("restore_value_block", [
                     source_block_number, target_block_number])

    def led_control(self, led_state, t1, t2, number_of_repetition, link_to_buzzer):
        """control led state

        Attributes:
            led state control : 0x00 - 0x0F
            T1 led Duration
            T2 led Duration
            number of repetition
            link to buzzer

        Example:
            0x05, 0x01, 0x01, 0x01, 0x01"""
        self.command("led_control", [led_state, t1, t2, number_of_repetition, link_to_buzzer])

    def get_picc_version(self):
        """get the PICC version of the reader"""
        return self.command("get_picc_version")

    def set_picc_version(self, picc_value):
        """set the PICC version of the reader

        Attributes:
            PICC value: 1 byte, default is 0xFF

        Example:
            0xFF"""
        self.command("set_picc_version", [picc_value])

    def buzzer_sound(self, poll_buzzer_status):
        """set the buzzer sound state

        Attributes:
            poll buzz status : 0x00 ~ 0xFF

        Example:
            0x00"""
        self.command("buzzer_sound", [poll_buzzer_status])

    def read_no_block(self,startblock = 0x08):
        self.authentication(startblock, 0x60, 0x00)
        position = startblock
        number= 32
        # uuid = [f"{byte:02X}" for byte in self.get_uid()]
        uuid = int.from_bytes(self.get_uid(), byteorder='big')
        result = []
        while number >= 16:
            result.extend(self.read_binary_blocks( position, 16))
            number -= 16
            position += 1
        try:
            encoded = bytes(result).decode('utf-8').replace('\x00','')
        except:
            encoded = result
        return  uuid, encoded
    
    def write_no_block(self, data, startblock = 0x08):
        self.authentication(startblock, 0x60, 0x00)
        data = bytes(data, 'utf-8')
        # uuid = [f"{byte:02X}" for byte in self.get_uid()]
        uuid = int.from_bytes(self.get_uid(), byteorder='big')
        for i in range(0, len(data), 16):
            start = math.floor((i) / 16)+startblock
            data_part = data[i: i + 16]
            while len(data_part) < 16:
                data_part += bytes([0])
            length = len(data_part)
            # if start
            # print("Position: ",start)
            # print("Number: ",length)
            # print("Data: ",data_part)
            if start >= startblock+3:
                raise error.InstructionFailed(f"OUT OF BLOCK ")
            result = self.update_binary_blocks(start,length,data_part)
        return uuid, result
    
    def set_timeout(self, timeout_parameter):
        """set the timeout of the reader

        Attributes:
            timeout parameter : 0x00 ~ 0x01 - 0xFE ~ 0xFF : (0,  5 second unit, infinite), default is 0xFF

        Example:
            0x01"""
        self.command("set_timeout", [timeout_parameter])

    def info(self):
        """print the type of the card on the reader"""
        atr = ATR(self.connection.getATR())
        historical_byte = toHexString(atr.getHistoricalBytes(), 0)
        print(historical_byte)
        print(historical_byte[-17:-12])
        card_name = historical_byte[-17:-12]
        name = option.cards.get(card_name, "")
        print(f"Card Name: {name}\n\tT0 {atr.isT0Supported()}\n\tT1 {atr.isT1Supported()}\n\tT1 {atr.isT15Supported()}")

    @staticmethod
    def print_data(data):
        print(f"data:\n\t{data}"
              f"\n\t{utils.int_list_to_hexadecimal_list(data)}"
              f"\n\t{utils.int_list_to_string_list(data)}")

    @staticmethod
    def print_sw1_sw2(sw1, sw2):
            print(f"sw1 : {sw1} {hex(sw1)}\n"
                  f"sw2 : {sw2} {hex(sw2)}")
