#!/usr/bin/env python3

import mido
import itertools
from time import time, sleep
from cv2 import VideoCapture, resize, CAP_PROP_POS_MSEC
from os import path
import numpy as np

# in_port = mido.open_input("Digital Keyboard:Digital Keyboard MIDI 1 24:0")
out_port = mido.open_output("Digital Keyboard:Digital Keyboard MIDI 1 24:0")

# file = mido.MidiFile("bad_apple.mid")
# track = mido.MidiTrack()
# file.tracks.append(track)

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
    # print("received: " + s, flush=True)

# in_port.callback = got_message
delta = 0
# bpm = 200

# def wait_beats(beats):
#     global delta
#     delta = int(file.ticks_per_beat * beats)

# def wait_secs(secs):
#     global delta
#     delta = int(file.ticks_per_beat * bpm * (secs / 60))

def send_bytes(b):
    global delta
    payload = [[(c >> 4) & 0xf, c & 0xf] for c in b]
    payload = list(itertools.chain(*payload))
    message = mido.Message("sysex", data=[0x43, 0x73, 0x01, 0x52, 0x19, 0x00, 0x00] + payload, time=delta)
    # print(message)
    delta = 0
    # track.append(message)
    out_port.send(message)

def send_str(s):
    send_bytes(bytes(s, "ascii"))

# code = 0x06002900
# ret = 0x6006b0c

# small brain = 884 bytes            <-- current solution
# big brain = 140 bytes (6x less)    <-- override cli handler
# genius = 92 bytes (9x less)        <-- pack 64 5-bit words into 40 8-bit words
# galaxy brain = 56 bytes (16x less) <-- override usb handler (dunno how)

def writes(addr, data):
    cmds = []
    for d in data:
        cmds.append(f"m/l {hex(addr)[2:]} {hex(d)[2:]}")
        addr += 4
    return cmds

def upload_program(filename):
    words = []

    with open(filename, "rb") as f:
        while True:
            chunk = f.read(4)
            if len(chunk) < 4 and len(chunk) > 1:
                chunk += bytes([0, 0, 0])
            if len(chunk) == 0:
                break
            word = (chunk[0] << 24) | (chunk[1] << 16) | (chunk[2] << 8) | chunk[3]
            words.append(word)
            if len(chunk) < 4:
                break

    for i, cmd in enumerate(writes(0x06002900, words)):
        # last_recv = ""
        send_str(cmd + "\r")
        print(i, cmd)
        # wait_secs(0.05)
        sleep(0.05)

def run_uploaded_program():
    send_str("m/l 06006b10 06002900\r")

send_str("\rlogin\r")
send_str("#0000\r")

upload_program("big_brain.bin")
run_uploaded_program()

cap = VideoCapture(path.join(path.dirname(__file__), "bad_apple.mp4"))
start = time()

# song_pos = 6.4

while cap.isOpened():
    # read frame
    ok, frame = cap.read()
    if not ok:
        break

    # drop frames (display is slower)
    pos = cap.get(CAP_PROP_POS_MSEC)
    if pos < (time() - start) * 1000:
        continue
    delay = (pos / 1000) - (time() - start)
    if delay > 0:
        sleep(delay)

    # resize to fit display
    assert frame.shape == (360, 480, 3)
    frame = resize(frame, (48, 35))
    frame = frame[13:21, 0:48]

    # draw frame
    framebuffer = [0] * 40
    for char in range(8):
        char_x, y = 0, 0
        for bit in range(5 * 8):
            x = (char * 6) + char_x
            if frame[y][x][0] < 128:
                framebuffer[(char * 5) + (bit // 8)] |= 1 << (7 - (bit % 8))
            char_x += 1
            if char_x == 5:
                char_x = 0
                y += 1

    # flip
    send_bytes(bytes(framebuffer))
    sleep(0.1)
    # wait_secs(0.1)
