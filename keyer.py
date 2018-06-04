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
        c = decoder.one_symbol(line)
        if c is not None:
            stdout.write(c)
            stdout.flush()
