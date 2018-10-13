#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

def FuzMend(filename):

    header_len = 16
    header_content = b'\x46\x55\x5A\x45\x01\x00\x00\x00'
    
    try:
    with open(filename + ".lip", "rb") as lip_file:
            lip_data = lip_file.read()
            lip_len = len(lip_data)
    except FileNotFoundError:
        lip_len = 0        
                
    lip_pad = (lip_len + header_len) % 4
    if lip_pad != 0:
        lip_pad = 4 - lip_pad
        
    with open(filename + ".mcadpcm", "rb") as voice_file:
        voice_data = voice_file.read()
        voice_start = lip_len + lip_pad + header_len

    with open(filename + ".fuz", "wb") as fuz_file:
        fuz_file.write(header_content)
        fuz_file.write(lip_len.to_bytes(4, byteorder='little', signed=False))
        fuz_file.write(voice_start.to_bytes(4, byteorder='little', signed=False))
        if lip_len != 0:
          fuz_file.write(lip_data)
        fuz_file.write(b'\x00' * lip_pad)
        fuz_file.write(voice_data)
    
if __name__ == '__main__':
    filename = sys.argv[1]