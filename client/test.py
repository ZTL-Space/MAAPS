from lib.acr122u import nfc
import math
import struct

from lib.acr122u import utils, option, error
reader = nfc.Reader()
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
reader.load_authentication_data(0x00, DEFAULT_KEYS[1])
reader.authentication(0x08, 0x60, 0x00)
# reader.get_uid()
# reader.info()
# reader.get_picc_version()

def write_txt(r, position, data):
    data = bytes(data, 'ascii')
    
    for i in range(0, len(data), 16):
        start = math.floor((i) / 16)+position
        data_part = data[i: i + 16]
        while len(data_part) < 16:
            data_part += bytes([0])
        length = len(data_part)
        # if start
        # print("Position: ",start)
        # print("Number: ",length)
        # print("Data: ",data_part)
        if start >= position+3:
            raise error.InstructionFailed("OUT OF BLOCK ")
        r.update_binary_blocks(start,length,data_part)

def write(r, position, number, data):
    while number >= 16:
        write_16(r, position, 16, data)
        number -= 16
        position += 1

def write_16(r, position, number, data):
    r.update_binary_blocks(position, number, data)


def read(r, position, number):
    result = []
    while number >= 16:
        result.extend(read_16(r, position, 16))
        number -= 16
        position += 1
    return result

def test_keys(r, sector=0, keys=DEFAULT_KEYS):
        """Testet ein Array potenzieller Schlüssel, um den richtigen zu finden.

        Schlüsselwort-Argumente:
        sector -- der Sektorindex (Standard: 0)
        keys -- die zu testenden Schlüssel (Standard: DEFAULT_KEYS)

        """
        for key in keys:
            try:
                print(r.authentication(sector, 0x60, 0x01))
                print("WORKING A", [f"{byte:02X}" for byte in key])
                print("READ: ", [f"{byte:02X}" for byte in read(reader, 0x01, 0x20)])
            except:
                print('A-')    

        for key in keys:
            try:
                r.load_authentication_data(0x01,key)
                print(r.authentication(sector, 0x61, 0x01))
                print("WORKING B",[f"{byte:02X}" for byte in key])
                print("READ: ", [f"{byte:02X}" for byte in read(reader, 0x01, 0x20)])
            except:
                print('B-')    

def read_16(r, position, number):
    return r.read_binary_blocks(position, number)




text = "U:Exel;4097b441dd060ae7ce72"
#print( write_txt(reader,0x01,text))
#write(reader, 0x02, 0x20, [0x00 for i in range(0,16)])
read_data = read(reader, 0x08, 0x20)
reader.print_data(read_data)
# print(bytes(read_data[1]).decode('ascii'))
# print(read_data())
#test_keys(reader,0x00)    
# print("READ: ", read(reader, 0x01, 0x20))
