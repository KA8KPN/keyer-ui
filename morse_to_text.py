#!/usr/bin/python3

import copy

morse_table = [
    {'c':'A', 'lc':True, 's':'dD'},
    {'c':'B', 'lc':True, 's':"Dddd"},
    {'c':'C', 'lc':True, 's':"DdDd"},
    {'c':'D', 'lc':True, 's':"Ddd"},
    {'c':'E', 'lc':True, 's':"d"},
    {'c':'F', 'lc':True, 's':"ddDd"},
    {'c':'G', 'lc':True, 's':"DDd"},
    {'c':'H', 'lc':True, 's':"dddd"},
    {'c':'I', 'lc':True, 's':"dd"},
    {'c':'J', 'lc':True, 's':"dDDD"},
    {'c':'K', 'lc':True, 's':"DdD"},
    {'c':'L', 'lc':True, 's':"dDdd"},
    {'c':'M', 'lc':True, 's':"DD"},
    {'c':'N', 'lc':True, 's':"Dd"},
    {'c':'O', 'lc':True, 's':"DDD"},
    {'c':'P', 'lc':True, 's':"dDDd"},
    {'c':'Q', 'lc':True, 's':"DDdD"},
    {'c':'R', 'lc':True, 's':"dDd"},
    {'c':'S', 'lc':True, 's':"ddd"},
    {'c':'T', 'lc':True, 's':"D"},
    {'c':'U', 'lc':True, 's':"ddD"},
    {'c':'V', 'lc':True, 's':"dddD"},
    {'c':'W', 'lc':True, 's':"dDD"},
    {'c':'X', 'lc':True, 's':"DddD"},
    {'c':'Y', 'lc':True, 's':"DdDD"},
    {'c':'Z', 'lc':True, 's':"DDdd"},
    {'c':'0', 'lc':False, 's':"DDDDD"},
    {'c':'1', 'lc':False, 's':"dDDDD"},
    {'c':'2', 'lc':False, 's':"ddDDD"},
    {'c':'3', 'lc':False, 's':"dddDD"},
    {'c':'4', 'lc':False, 's':"ddddD"},
    {'c':'5', 'lc':False, 's':"ddddd"},
    {'c':'6', 'lc':False, 's':"Ddddd"},
    {'c':'7', 'lc':False, 's':"DDddd"},
    {'c':'8', 'lc':False, 's':"DDDdd"},
    {'c':'9', 'lc':False, 's':"DDDDd"},
    {'c':' ', 'lc':False, 's':"S"},
    {'c':'.', 'lc':False, 's':"dDdDdD"},
    {'c':',', 'lc':False, 's':"DDddDD"},
    {'c':'?', 'lc':False, 's':"ddDDdd"},
    {'c':'\'','lc':False,'s': "dDDDDd"},
    {'c':'!', 'lc':False, 's':"DdDdDD"},
    {'c':'/', 'lc':False, 's':"DddDd"},
    {'c':'(', 'lc':False, 's':"DdDDd"}, # Prosign KN
    {'c':')', 'lc':False, 's':"DdDDdD"},
    {'c':'&', 'lc':False, 's':"dDddd"}, # Prosign: AS
    {'c':':', 'lc':False, 's':"DDDddd"},
    {'c':';', 'lc':False, 's':"DdDdDd"},
    {'c':'=', 'lc':False, 's':"DdddD"}, # Prosign BT
    {'c':'+', 'lc':False, 's':"dDdDd"}, # Prosign AR
    {'c':'-', 'lc':False, 's':"DddddD"},
    {'c':'_', 'lc':False, 's':"ddDDdD"},
    {'c':'"', 'lc':False, 's':"dDddDd"},
    {'c':'$', 'lc':False, 's':"dddDddD"},
    {'c':'@', 'lc':False, 's':"dDDdDd"},
    {'c':'\\', 'lc':False, 's':"DDDDDD"} # Something that Anthony Good has defined as backslash, so I will use it, too, at least for now
    # {512, 0, "dddDdD"}, # Prosign SK
    # {513, 0, "dddddddd"}, # Error
    # {514, 0, "DdDdD"}, # WTF?  "Starting Signal"  according to Wikipedia
    # {515, 0, "dddDd"}, # WTF?  "Understood" according to Wikipedia
]

# Now, define the table used to decode morse.  The general thing to do is to create a table with a start symbol
# and then create two links, one for "dit" and one for "dah", pointing to other elements in the table.  I also
# define a character to include if this is the place you stop for a word space and I have to have an error symbol

morse_decode_table = None

def build_morse_decode_table(morse_table):
    global morse_decode_table
    morse_decode_table = {'dit':None, 'dah':None, 'char':None}
    for s in morse_table:
        entry = morse_decode_table
        target = s['c']
        for c in s['s']:
            if 'd' == c:
                if entry['dit'] is None:
                    entry['dit'] = copy.deepcopy({'dit':None, 'dah':None, 'char':None})
                entry = entry['dit']
            else:
                if entry['dah'] is None:
                    entry['dah'] = copy.deepcopy({'dit':None, 'dah':None, 'char':None})
                entry = entry['dah']
        entry['char'] = target

build_morse_decode_table(morse_table)

# print(morse_decode_table)

class MorseDecoder:
    def __init__(self):
        self.__decode_state = morse_decode_table

    # The key up and key down symbols, the significant ones from here, are
    def one_symbol(self, parts):
        decoded = None
        if 'u' == parts[0]:
            xmitter = int(parts[1])
            len = int(parts[2])
            if len > 20:
                decoded = self.__decode_state['char']
                if decoded is not None:
                    if len > 50:
                        decoded = decoded + ' '
                self.__decode_state = morse_decode_table
        elif 'd' == parts[0]:
            xmitter = int(parts[1])
            len = int(parts[2])
            if len > 20:
                self.__decode_state = self.__decode_state['dah']
            else:
                self.__decode_state = self.__decode_state['dit']
            if self.__decode_state is None:
                self.__decode_state = morse_decode_table

        return decoded
                

class MorseEncoder:
    def __init__(self, xmit_queue):
        self.xmit_queue = xmit_queue
        self.encode_table = {}
        for i in morse_table:
            self.encode_table[i['c']] = i['s']
            if i['lc']:
                self.encode_table[i['c'].lower()] = i['s']
        print(self.encode_table)

    def one_letter(self, xmitter, s):
        if s.isspace():
            self.xmit_queue.put(('u:%d:40\r\n' % xmitter).encode('ascii'))
        elif s in self.encode_table:
            p = self.encode_table[s]
            for i in p:
                if i.islower():
                    self.xmit_queue.put(('d:%d:10\r\n' % xmitter).encode('ascii'))
                    # print("Sent     the line '%s'" % ('d:%d:10' % xmitter))
                else:
                    self.xmit_queue.put(('d:%d:30\r\n' % xmitter).encode('ascii'))
                    # print("Sent     the line '%s'" % ('d:%d:30' % xmitter))
                self.xmit_queue.put(('u:%d:10\r\n' % xmitter).encode('ascii'))
                # print("Sent     the line '%s'" % ('u:%d:10' % xmitter))
            self.xmit_queue.put(('u:%d:20\r\n' % xmitter).encode('ascii'))
            # print("Sent     the line '%s'" % ('u:%d:20' % xmitter))
        else:
            print("Character %s not found" % s)
