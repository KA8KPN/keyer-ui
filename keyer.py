#!/usr/bin/python3

from sys import stdout
import serial
# import io
from morse_to_text import MorseDecoder

port = serial.Serial('/dev/ttyUSB0', 115200, timeout=30)
# sio = io.TextIOWrapper(io.BufferedRWPair(port, port))
decoder = MorseDecoder()

while True:
    line = port.readline().decode('ascii').strip()
    if "" == line:
        break
    else:
        (c, error) = decoder.one_symbol(line)
        if not error:
            stdout.write(c)
        else:
            print("\n***ERROR***")
