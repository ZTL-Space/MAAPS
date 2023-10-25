import time
import sys
import os
from bottle import route
import bottle
from bottle import response
from lib.acr122u import nfc
import math
import struct


##
## RFID
##
class RFID:
    def __init__(self):
        self.reader = None
        # self.reader.info()
        # self.reader.authentication(0x01, 0x61, 0x01)
    def read(self):
        self.reader = nfc.Reader()
        token_id, text = None, None
        for i in range(3):
            token_id, text = self.reader.read_no_block()
            if token_id is not None:
                text = text.strip()
                print("successful read", text)
                break
            time.sleep(1)
        return token_id, text

    def write(self, text):
        self.reader = nfc.Reader()
        
        token_id, output = None, None
        for i in range(3):
            token_id, output = self.reader.write_no_block(text)
            if token_id is not None:
                break
            time.sleep(1)
        return token_id, output


##
## WEB API
##
def btl_enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers[
            'Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, X-Test'
        if bottle.request.method != 'OPTIONS':
            return fn(*args, **kwargs)

    return _enable_cors


@route('/rfid/read/', method=['OPTIONS', 'GET'])
@btl_enable_cors
def route_rfid_read():
    token_id, text = rfid.read()
    if token_id is None:
        return ""
    return "%s\t%s" % (token_id, text)


@route('/rfid/write/<value>', method=['OPTIONS', 'GET'])
@btl_enable_cors
def route_rfid_write(value=""):
    if value != "":
        token_id, text = rfid.write(value)
        if token_id is not None:
            return "OK"
    return "Failed"


##
## Commandline
##
if __name__ == "__main__":
    rfid = RFID()

    if len(sys.argv) == 1:
         bottle.run(host='127.0.0.1', port=8080)
    else:
        if sys.argv[1] == "write":
            print("RFID TAG AUFLEGEN")
            print(rfid.write(sys.argv[2]))
        elif sys.argv[1] == "read":
            print("RFID TAG AUFLEGEN")
            print(rfid.read())
        else:
            print("Unknown Option '%s'" % sys.argv[1])
