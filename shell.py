#!/usr/bin/env python3

import asyncio
import mido
import itertools
from threading import Thread
import readchar

in_port = mido.open_input("Digital Keyboard:Digital Keyboard MIDI 1 24:0")
out_port = mido.open_output("Digital Keyboard:Digital Keyboard MIDI 1 24:0")

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
    print(s, end="", flush=True)

in_port.callback = got_message

def send_str(s):
    payload = [[(ord(c) >> 4) & 0xf, ord(c) & 0xf] for c in s]
    payload = list(itertools.chain(*payload))
    out_port.send(mido.Message("sysex", data=[0x43, 0x73, 0x01, 0x52, 0x19, 0x00, 0x00] + payload))

def poll_input():
    while True:
        key = readchar.readchar()
        if key:
            if key == '\n':
                key = '\r'
            elif key == chr(3):
                return
            send_str(key)

async def main():
    t = Thread(target=poll_input)
    t.run()
    t.join()

asyncio.run(main())
