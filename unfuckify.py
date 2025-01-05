#!/usr/bin/env python3

with open("flash_ex_fucked.bin", "rb") as i:
    with open("flash_ex.bin", "wb") as o:
        while True:
            b = i.read(4)
            if len(b) == 0:
                break
            b = bytes([b[3], b[2], b[1], b[0]])
            o.write(b)
