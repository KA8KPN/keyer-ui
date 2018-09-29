#!/usr/bin/python3

import tkinter
import tkinter.ttk
import tkinter.scrolledtext
import threading
import queue
import time
import json

from sys import stdout
import serial
# import io
from morse_to_text import MorseDecoder, MorseEncoder

class MemoryButton(tkinter.ttk.Button):
    def __init__(self, master, **kwargs):
        super(MemoryButton, self).__init__(master, **kwargs)
        # print(self.text)

    def save_config(self):
        pass

    def restore_config(self, config):
        pass

class MemoryButtons(tkinter.ttk.Frame):
    def __init__(self, master, startCount, numButtons, **kwargs):
        super(MemoryButtons, self).__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.buttons = []
        for i in range(numButtons):
            b = MemoryButton(self, text="F%d"%(i+startCount))
            self.rowconfigure(i, weight=1)
            b.grid(column=0, row=i, padx=2, pady=2, sticky=(tkinter.N, tkinter.S))
            self.buttons.append(b)

    def save_config(self):
        pass

    def restore_config(self, config):
        pass

class TopBar(tkinter.ttk.Frame):
    def __init__(self, master, **kwargs):
        super(TopBar, self).__init__(master, **kwargs)
        self.left = tkinter.ttk.Label(self, text="Paddle Mode:  Iambic-A")
        self.right = tkinter.ttk.Frame(self, relief="ridge")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.left.grid(padx=2, column=0, row=0, sticky=(tkinter.W))
        self.right.grid(padx=2, column=1, row=0, sticky=(tkinter.E))
        self.wpmPlus = tkinter.ttk.Button(self.right, text="+")
        self.wpmMinus = tkinter.ttk.Button(self.right, text="-")
        self.wpm = tkinter.ttk.Label(self.right, text="18 WPM")
        self.wpmPlus.grid(column=2, row=0)
        self.wpm.grid(column=1, row=0)
        self.wpmMinus.grid(column=0, row=0)

    def save_config(self):
        pass

    def restore_config(self, config):
        pass

class TransmitterButton(tkinter.ttk.Button):
    def __init__(self, master, which, stylename, **kwargs):
        super(TransmitterButton, self).__init__(master, **kwargs)
        self.master = master
        self.which = which
        self.stylename = stylename
        self.bind('<Button-1>', self.clicked)
        self.selected = False

    def save_config(self):
        return self.selected

    def restore_config(self, config):
        if config:
            self.clicked(None)

    def picked(self):
        style.configure(self.stylename, background='lightgreen')
        style.map(self.stylename, background=[('active', 'lightgreen')])
        # self.master.select(which)
        self.selected = True
        pass

    def not_picked(self):
        style.map(self.stylename, background=[('active', 'red')])
        style.configure(self.stylename, background='red')
        self.selected = False
        pass

    def clicked(self, foo):
        self.master.select(self.which)

class TransmitterButtons(tkinter.ttk.Frame):
    def __init__(self, master, **kwargs):
        super(TransmitterButtons, self).__init__(master, **kwargs)
        self.selected_button = None
        self.buttons = []
        global style
        style = tkinter.ttk.Style()
        for i in range(4):
            stylename = "xmit_button%d.TButton" % i
            style.configure(stylename, foreground='black', background='red', relief='sunken')
            style.map(stylename, background=[('active', 'red')], relief=[('active', 'raised')])
            self.buttons.append(TransmitterButton(self, i, stylename, text="Transmitter\n%d" % (i+1), style=stylename))
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.buttons[0].grid(padx=10, pady=10, column=0, row=0, sticky=(tkinter.N, tkinter.S, tkinter.E, tkinter.W))
        self.buttons[1].grid(padx=10, pady=10, column=1, row=0, sticky=(tkinter.N, tkinter.S, tkinter.E, tkinter.W))
        self.buttons[2].grid(padx=10, pady=10, column=0, row=1, sticky=(tkinter.N, tkinter.S, tkinter.E, tkinter.W))
        self.buttons[3].grid(padx=10, pady=10, column=1, row=1, sticky=(tkinter.N, tkinter.S, tkinter.E, tkinter.W))
        # self.buttons[self.selected_button].picked()

    def save_config(self):
        response = []
        for button in self.buttons:
            response.append(button.save_config())
        return response

    def restore_config(self, config):
        # This is tricky.  I have to configure the buttons with what's in the config as long as there isn't more config than buttons
        max = len(config)
        count = 0
        for button in self.buttons:
            if count < max:
                button.restore_config(config[count])
            count = count + 1
        pass

    def select(self, which):
        # print("Changing the active from %d to %d" % (self.selected_button, which))
        if which != self.selected_button:
            if self.selected_button is not None:
                self.buttons[self.selected_button].not_picked()
            self.buttons[which].picked()
            self.selected_button = which


# NOTE:  The display I want to configure for is 1024x600 pixels
class mainWindow(tkinter.ttk.Frame):
    def __init__(self, top, encoder, **kwargs):
        self.encoder = encoder
        self.xmit_queue = xmit_queue
        super().__init__(top)
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=(tkinter.N, tkinter.W, tkinter.E, tkinter.S))
        self.left = MemoryButtons(self, 1, 6)
        self.right = MemoryButtons(self, 7, 6)
        self.left.grid(row=0, column=0, rowspan=3, sticky=(tkinter.N, tkinter.S))
        self.right.grid(row=0, column=2, rowspan=3, sticky=(tkinter.N, tkinter.S))
        self.topBar = TopBar(self)
        self.topBar.grid(row=0, column=1, sticky=(tkinter.W, tkinter.E))
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        self.xmitters = TransmitterButtons(self, relief="groove")
        self.xmitters.rowconfigure(0, weight=1)
        self.xmitters.grid(pady=5, row=1, column=1, sticky=(tkinter.N, tkinter.S, tkinter.E, tkinter.W))
        self.ta = tkinter.scrolledtext.ScrolledText(self, width=100, height=6)
        self.ta.grid(row=2, column=1)
        self.bind_all('<Alt-Key-q>', self.getout)
        self.bind_all('<Key>', self.getout)

    def addChar(self, c):
        self.ta.insert("end", c)

    def getout(self, event):
        # print("Char:   '%s'" % event.char)
        # print("Keysym: '%s'" % event.keysym)
        # print("State:  '%s'" % event.state)
        # 0x08 & event.state is ALT
        if (0 != 0x08 & event.state) and ('q' == event.char):
            quit()
        if (16 == 0xfe & event.state):
            self.encoder.one_letter(1, event.char)

    def save_config(self):
        # The transmitters and the top bar and the left and right memory buttons have configurations
        # start with the transmitters
        config = {}
        config['xmitters'] = self.xmitters.save_config()
        return config

    def restore_config(self, config):
        self.xmitters.restore_config(config['xmitters'])

    def active_xmitter(self, xmitter):
        self.active_xmitter = xmitter

# Note:  If I'm going to allow the system to drive multiple transmitters
# simultaneously, I'm going to have to work out a mechanism for dealing
# with multiple transmit queues, one per transmitter
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
                self.acknowledged = False
                self.port.write(item)
                # print("Sent     the line '%s'" % item)
                while not self.acknowledged:
                    time.sleep(0.01)
            else:
                time.sleep(0.1)

    def pause(self, xmitter):
        # print("Pausing transmitter %d" % xmitter)
        self.xon = False

    def resume(self, xmitter):
        # print("Resuming transmitter %d" % xmitter)
        self.xon = True

    # Means the receiver got the message
    def acknowledge(self):
        # print("message acknowledged")
        self.acknowledged = True


class recvThread(threading.Thread):
    def __init__(self, threadId, port, decoder, xmitter, window):  # Add the config
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
            line = self.port.readline().decode('ascii').strip().split(':')
            # print("Received the line '%s'" % ':'.join(line))
            # print("The first part is '%s'" % line[0])
            if "" == line[0]:
                # break
                pass
            elif 'a' == line[0]:
                self.xmitter.acknowledge()
            elif 'xon' == line[0]:
                # print("Receiver attempting to resume the transmitter")
                self.xmitter.resume(int(line[1]))
            elif 'xoff' == line[0]:
                # print("Receiver attempting to pause the transmitter")
                self.xmitter.pause(int(line[1]))
            else:
                # print("Received the line '%s'" % line)

                c = self.decoder.one_symbol(line)
                if c is not None:
                    self.window.addChar(c)
                    # stdout.write(c)
                    # stdout.flush()

import argparse

parser = argparse.ArgumentParser(description="Telegraph Keyer User Interface")
parser.add_argument("--ui", help="Run the UI without trying to talk to a keyer", action='store_true')
parser.add_argument("--serial", nargs='?', help="The serial port to use to talk to the dongle", default="/dev/ttyUSB0")

args = parser.parse_args()

if not args.ui:
    port = serial.Serial(args.serial, 115200, timeout=30, xonxoff=True)
    # sio = io.TextIOWrapper(io.BufferedRWPair(port, port))

xmit_queue = queue.Queue()
decoder = MorseDecoder()
encoder = MorseEncoder(xmit_queue)

top = tkinter.Tk()
top.title = "Memory Keyer"
frame = mainWindow(top, encoder, padding="3 3 12 12")

try:
    with open('keyer_conf.json', 'r') as cfile:
        frame.restore_config(json.load(cfile))
except FileNotFoundError as e:
    pass

if not args.ui:
    thread1 = xmitThread(1, port, xmit_queue)
    thread1.start()
    thread2 = recvThread(1, port, decoder, thread1, frame)
    thread2.start()

top.mainloop()

if not args.ui:
    port.close()

    thread2.endThread()
    thread2.join()
    thread1.endThread()
    thread1.join()

with open('keyer_conf.json', 'w') as cfile:
    json.dump(frame.save_config(), cfile)
