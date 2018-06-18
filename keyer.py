#!/usr/bin/python3

import tkinter
import tkinter.ttk
import tkinter.scrolledtext
import threading

from sys import stdout
import serial
# import io
from morse_to_text import MorseDecoder

class mainWindow(tkinter.ttk.Frame):
    def __init__(self, top, **kwargs):
        super().__init__(top)
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=(tkinter.N, tkinter.W, tkinter.E, tkinter.S))
        self.ta = tkinter.scrolledtext.ScrolledText(self)
        self.ta.grid(row=0, column=0)
        self.bind_all('<Alt-Key-q>', self.getout)
        self.bind_all('<Key>', self.getout)

    def addChar(self, c):
        self.ta.insert("end", c)

    def getout(self, event):
        print("Char:   '%s'" % event.char)
        print("Keysym: '%s'" % event.keysym)
        print("State:  '%s'" % event.state)
        # 0x08 & event.state is ALT
        if (0 != 0x08 & event.state) and ('q' == event.char):
            quit()

class commThread(threading.Thread):
    def __init__(self, threadId, port, decoder, window):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.port = port
        self.window = window
        self.continueThread = True
        self.decoder = decoder

    def endThread(self):
        self.continueThread = False

    def run(self):
        while self.continueThread:
            line = self.port.readline().decode('ascii').strip()
            if "" == line:
                # break
                pass
            else:
                c = self.decoder.one_symbol(line)
                if c is not None:
                    self.window.addChar(c)
                    # stdout.write(c)
                    # stdout.flush()

top = tkinter.Tk()
top.title = "Memory Keyer"
frame = mainWindow(top, padding="3 3 12 12")

port = serial.Serial('/dev/ttyUSB0', 115200, timeout=30)
# sio = io.TextIOWrapper(io.BufferedRWPair(port, port))
decoder = MorseDecoder()

thread1 = commThread(1, port, decoder, frame)
thread1.start()

top.mainloop()

thread1.endThread()
thread1.join()
