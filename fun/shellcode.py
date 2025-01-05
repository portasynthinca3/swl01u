#!/usr/bin/env python3

import mido
import itertools
from time import sleep

# in_port = mido.open_input("Digital Keyboard:Digital Keyboard MIDI 1 24:0")
out_port = mido.open_output("Digital Keyboard:Digital Keyboard MIDI 1 24:0")

file = mido.MidiFile("toccata.mid")
track = mido.MidiTrack()
file.tracks.append(track)

def got_message(message):
    if message.dict()["type"] != "sysex":
        return
    data = message.dict()["data"]
    if len(data) < 9:
        return
    payload = data[7:]
    # print(payload)
    s = ""
    for hi, lo in zip(payload[0::2], payload[1::2]):
        c = chr((hi << 4) | lo)
        if c == '\r':
            c = '\n'
        s += c
    print("received: " + s, flush=True)

# in_port.callback = got_message
delta = 0

def wait_beats(beats):
    global delta
    delta = int(file.ticks_per_beat * beats)

def send_str(s):
    global delta
    payload = [[(ord(c) >> 4) & 0xf, ord(c) & 0xf] for c in s]
    payload = list(itertools.chain(*payload))
    message = mido.Message("sysex", data=[0x43, 0x73, 0x01, 0x52, 0x19, 0x00, 0x00] + payload, time=delta)
    delta = 0
    track.append(message)
    # out_port.send(message)

# code = 0x06002900
# ret = 0x6006b0c

def writes(addr, data):
    cmds = []
    for d in data:
        cmds.append(f"m/l {hex(addr)[2:]} {hex(d)[2:]}")
        addr += 4
    return cmds

def say(string):
    ints = []

    for i in range(0, len(string), 4):
        chunk = string[i : i + 4]
        i = 0
        offs = 24
        for c in chunk:
            i |= ord(c) << offs
            offs -= 8
        ints.append(i)

    cmds = writes(0x06002918, [
        *ints,
        0,
    ])
    cmds.append("m/l 06006b10 06002900")

    for cmd in cmds:
        send_str(cmd + "\r")

send_str("login\r")
send_str("#0000\r")
for cmd in writes(0x06002900, [
    0xe59f1008,
    0xe28f000c,
    0xe59fe004,
    0xe12fff11,
    0x02086ed5,
    0x0202207d,
]):
    send_str(cmd + "\r")

meme = """Location
40.1825N
44.5133W
        
IPv6 ::1
        
I am rap
idly app
roaching
your loc
ation.  
        
!       

!!      

!!!     

!!!!    

!!!!!   

!!!!!!  

!!!!!!! 



HIDE    
"""

for s in meme.split("\n"):
    say(s)
    wait_beats(0.5)

file.save("toccata2.mid")
