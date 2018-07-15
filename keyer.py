#!/usr/bin/python3

import tkinter
import tkinter.ttk
import tkinter.scrolledtext
import threading
import queue
import time

from sys import stdout
import serial
# import io
from morse_to_text import MorseDecoder, MorseEncoder

class mainWindow(tkinter.ttk.Frame):
    def __init__(self, top, encoder, **kwargs):
        self.encoder = encoder
        self.xmit_queue = xmit_queue
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
        if (16 == 0xfe & event.state):
            self.encoder.one_letter(1, event.char)


class xmitThread(threading.Thread):
    def __init__(self, threadId, port, xmit_queue):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.port = port
        self.continueThread = True
        self.xmit_queue = xmit_queue
        self.xon = True

    def endThread(self):
        self.continueThread = False

    def run(self):
        while self.continueThread:
            if self.xon:
                item = self.xmit_queue.get()
                self.port.write(item)
                print("Sent     the line '%s'" % item)
            else:
                time.sleep(0.1)

    def pause(self):
        print("Pausing")
        self.xon = False

    def resume(self):
        print("Resuming")
        self.xon = True


class recvThread(threading.Thread):
    def __init__(self, threadId, port, decoder, xmitter, window):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.port = port
        self.window = window
        self.continueThread = True
        self.decoder = decoder
        self.xmitter = xmitter

    def endThread(self):
        self.continueThread = False

    def run(self):
        while self.continueThread:
            line = self.port.readline().decode('ascii').strip()
            if "" == line:
                # break
                pass
            elif 'xoff:0' == line:
                self.xmitter.pause()
            elif 'xon:0' == line:
                self.xmitter.resume()
            else:
                print("Received the line '%s'" % line)

                c = self.decoder.one_symbol(line)
                if c is not None:
                    self.window.addChar(c)
                    # stdout.write(c)
                    # stdout.flush()

port = serial.Serial('/dev/ttyUSB0', 115200, timeout=30, xonxoff=True)
# sio = io.TextIOWrapper(io.BufferedRWPair(port, port))

xmit_queue = queue.Queue()
decoder = MorseDecoder()
encoder = MorseEncoder(xmit_queue)

top = tkinter.Tk()
top.title = "Memory Keyer"
frame = mainWindow(top, encoder, padding="3 3 12 12")

thread1 = xmitThread(1, port, xmit_queue)
thread1.start()
thread2 = recvThread(1, port, decoder, thread1, frame)
thread2.start()

top.mainloop()

port.close()

thread2.endThread()
thread2.join()
thread1.endThread()
thread1.join()
