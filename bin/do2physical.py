#!/usr/bin/env python3

import os
import sys

kMap = {0x00: 0x00,
        0x01: 0x07,
        0x02: 0x0E,
        0x03: 0x06,
        0x04: 0x0D,
        0x05: 0x05,
        0x06: 0x0C,
        0x07: 0x04,
        0x08: 0x0B,
        0x09: 0x03,
        0x0A: 0x0A,
        0x0B: 0x02,
        0x0C: 0x09,
        0x0D: 0x01,
        0x0E: 0x08,
        0x0F: 0x0F}

infile = sys.argv[1]
outfile = infile+'.tmp'
with open(infile, 'rb') as f, open(outfile, 'wb') as g:
    for track in range(0, 0x23):
        sectors = [bytes(256)] * 0x10
        for dos_sector in range(0, 0x10):
            sectors[kMap[dos_sector]] = f.read(256)
        g.write(b"".join(sectors))
os.rename(outfile, infile)
