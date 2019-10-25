#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Stella/AboodXD

# Supported formats:
#  -RGBA8
#  -RGB10A2
#  -RGB565
#  -RGB5A1
#  -RGBA4
#  -L8/R8
#  -L8A8/RG8
#  -BC1
#  -BC2
#  -BC3
#  -BC4U
#  -BC4S
#  -BC5U
#  -BC5S

# Feel free to include this in your own program if you want, just give credits. :)

"""dds.py: DDS reader and header generator."""

import struct
import util

try:
    import form_conv_cy as form_conv
except ImportError:
    import form_conv

def readDDS(f, SRGB):
    with open(f, "rb") as inf:
        inb = inf.read()

    if len(inb) < 0x80 or inb[:4] != b'DDS ':
        util.LogDebug("")
        util.LogDebug(f + " is not a valid DDS file!")
        return 0, 0, 0, b'', 0, [], 0, []

    width = struct.unpack("<I", inb[16:20])[0]
    height = struct.unpack("<I", inb[12:16])[0]

    fourcc = inb[84:88]

    if fourcc == b'DX10':
        util.LogDebug("")
        util.LogDebug("DX10 DDS files are not supported.")
        return 0, 0, 0, b'', 0, [], 0, []

    pflags = struct.unpack("<I", inb[80:84])[0]
    bpp = struct.unpack("<I", inb[88:92])[0] >> 3
    channel0 = struct.unpack("<I", inb[92:96])[0]
    channel1 = struct.unpack("<I", inb[96:100])[0]
    channel2 = struct.unpack("<I", inb[100:104])[0]
    channel3 = struct.unpack("<I", inb[104:108])[0]
    caps = struct.unpack("<I", inb[108:112])[0]

    if caps not in [0x1000, 0x401008]:
        util.LogDebug("")
        util.LogDebug("Invalid texture (caps[" + str(caps) + "] not in [0x1000, 0x401008]).")
        return 0, 0, 0, b'', 0, [], 0, []

    abgr8_masks = {0xff: 0, 0xff00: 1, 0xff0000: 2, 0xff000000: 3, 0: 5}
    bgr8_masks = {0xff: 0, 0xff00: 1, 0xff0000: 2, 0: 5}
    a2rgb10_masks = {0x3ff00000: 0, 0xffc00: 1, 0x3ff: 2, 0xc0000000: 3, 0: 5}
    bgr565_masks = {0x1f: 0, 0x7e0: 1, 0xf800: 2, 0: 5}
    a1bgr5_masks = {0x1f: 0, 0x3e0: 1, 0x7c00: 2, 0x8000: 3, 0: 5}
    abgr4_masks = {0xf: 0, 0xf0: 1, 0xf00: 2, 0xf000: 3, 0: 5}
    l8_masks = {0xff: 0, 0: 5}
    a8l8_masks = {0xff: 0, 0xff00: 1, 0: 5}

    compressed = False
    luminance = False
    rgb = False
    has_alpha = False

    if pflags == 4:
        compressed = True

    elif pflags == 0x20000 or pflags == 2:
        luminance = True

    elif pflags == 0x20001:
        luminance = True
        has_alpha = True

    elif pflags == 0x40:
        rgb = True

    elif pflags == 0x41:
        rgb = True
        has_alpha = True

    else:
        util.LogDebug("")
        util.LogDebug("Invalid texture.  pflags = " + str(pflags))
        return 0, 0, 0, b'', 0, [], 0, []

    format_ = 0

    if compressed:
        compSel = [0, 1, 2, 3]

        if fourcc == b'DXT1':
            format_ = 0x42
            bpp = 8

        elif fourcc == b'DXT3':
            format_ = 0x43
            bpp = 16

        elif fourcc == b'DXT5':
            format_ = 0x44
            bpp = 16

        elif fourcc in [b'BC4U', b'ATI1']:
            format_ = 0x49
            bpp = 8

        elif fourcc == b'BC4S':
            format_ = 0x4a
            bpp = 8

        elif fourcc in [b'BC5U', b'ATI2']:
            format_ = 0x4b
            bpp = 16

        elif fourcc == b'BC5S':
            format_ = 0x4c
            bpp = 16

        size = ((width + 3) >> 2) * ((height + 3) >> 2) * bpp

    else:
        if luminance:
            if has_alpha:
                if channel0 in a8l8_masks and channel1 in a8l8_masks and channel2 in a8l8_masks and channel3 in a8l8_masks and bpp == 2:
                    format_ = 0xd

                    compSel = [a8l8_masks[channel0], a8l8_masks[channel1], a8l8_masks[channel2], a8l8_masks[channel3]]

            else:
                if channel0 in l8_masks and channel1 in l8_masks and channel2 in l8_masks and channel3 in l8_masks and bpp == 1:
                    format_ = 1

                    compSel = [l8_masks[channel0], l8_masks[channel1], l8_masks[channel2], l8_masks[channel3]]

        elif rgb:
            if has_alpha:
                if bpp == 4:
                    if channel0 in abgr8_masks and channel1 in abgr8_masks and channel2 in abgr8_masks and channel3 in abgr8_masks:
                        format_ = 0x38 if SRGB else 0x25

                        compSel = [abgr8_masks[channel0], abgr8_masks[channel1], abgr8_masks[channel2], abgr8_masks[channel3]]

                    elif channel0 in a2rgb10_masks and channel1 in a2rgb10_masks and channel2 in a2rgb10_masks and channel3 in a2rgb10_masks:
                        format_ = 0x3d

                        compSel = [a2rgb10_masks[channel0], a2rgb10_masks[channel1], a2rgb10_masks[channel2], a2rgb10_masks[channel3]]

                elif bpp == 2:
                    if channel0 in a1bgr5_masks and channel1 in a1bgr5_masks and channel2 in a1bgr5_masks and channel3 in a1bgr5_masks:
                        format_ = 0x3b

                        compSel = [a1bgr5_masks[channel0], a1bgr5_masks[channel1], a1bgr5_masks[channel2], a1bgr5_masks[channel3]]

                    elif channel0 in abgr4_masks and channel1 in abgr4_masks and channel2 in abgr4_masks and channel3 in abgr4_masks:
                        format_ = 0x39

                        compSel = [abgr4_masks[channel0], abgr4_masks[channel1], abgr4_masks[channel2], abgr4_masks[channel3]]

            else:
                if channel0 in bgr8_masks and channel1 in bgr8_masks and channel2 in bgr8_masks and channel3 == 0 and bpp == 3: # Kinda not looking good if you ask me
                    format_ = 0x38 if SRGB else 0x25

                    compSel = [bgr8_masks[channel0], bgr8_masks[channel1], bgr8_masks[channel2], 3]

                if channel0 in bgr565_masks and channel1 in bgr565_masks and channel2 in bgr565_masks and channel3 in bgr565_masks and bpp == 2:
                    format_ = 0x3c

                    compSel = [bgr565_masks[channel0], bgr565_masks[channel1], bgr565_masks[channel2], bgr565_masks[channel3]]

        size = width * height * bpp

    if caps == 0x401008:
        numMips = struct.unpack("<I", inb[28:32])[0] - 1
        mipSize = get_mipSize(width, height, bpp, numMips, compressed)
    else:
        numMips = 0
        mipSize = 0

    if len(inb) < 0x80+size+mipSize:
        util.LogDebug("")
        util.LogDebug(f + " is not a valid DDS file!")
        return 0, 0, 0, b'', 0, [], 0, []

    if format_ == 0:
        util.LogDebug("")
        util.LogDebug("Unsupported DDS format!")
        return 0, 0, 0, b'', 0, [], 0, []

    
    data = inb[0x80:0x80+size+mipSize]

    if format_ in [0x25, 0x38] and bpp == 3:
        data = form_conv.rgb8torgbx8(data)
        bpp += 1
        size = width * height * bpp

    return width, height, format_, fourcc, size, compSel, numMips, data


def get_mipSize(width, height, bpp, numMips, compressed):
    size = 0
    for i in range(numMips):
        level = i + 1
        if compressed:
            size += ((max(1, width >> level) + 3) >> 2) * ((max(1, height >> level) + 3) >> 2) * bpp
        else:
            size += max(1, width >> level) * max(1, height >> level) * bpp
    return size


def generateHeader(num_mipmaps, w, h, format_, compSel, size, compressed):
    hdr = bytearray(128)

    luminance = False
    RGB = False

    has_alpha = True

    if format_ == 28:  # ABGR8
        RGB = True
        compSels = {0: 0x000000ff, 1: 0x0000ff00, 2: 0x00ff0000, 3: 0xff000000, 5: 0}
        fmtbpp = 4
        

    elif format_ == 24:  # A2RGB10
        RGB = True
        compSels = {0: 0x3ff00000, 1: 0x000ffc00, 2: 0x000003ff, 3: 0xc0000000, 5: 0}
        fmtbpp = 4

    elif format_ == 85:  # BGR565
        RGB = True
        compSels = {0: 0x0000001f, 1: 0x000007e0, 2: 0x0000f800, 3: 0, 5: 0}
        fmtbpp = 2
        has_alpha = False

    elif format_ == 86:  # A1BGR5
        RGB = True
        compSels = {0: 0x0000001f, 1: 0x000003e0, 2: 0x00007c00, 3: 0x00008000, 5: 0}
        fmtbpp = 2

    elif format_ == 115:  # ABGR4
        RGB = True
        compSels = {0: 0x0000000f, 1: 0x000000f0, 2: 0x00000f00, 3: 0x0000f000, 5: 0}
        fmtbpp = 2

    elif format_ == 61:  # L8
        luminance = True
        compSels = {0: 0x000000ff, 1: 0, 2: 0, 3: 0, 5: 0}
        fmtbpp = 1
        if compSel[3] != 0:
            has_alpha = False

    elif format_ == 49:  # A8L8
        luminance = True
        compSels = {0: 0x000000ff, 1: 0x0000ff00, 2: 0, 3: 0, 5: 0}
        fmtbpp = 2

    flags = 0x00000001 | 0x00001000 | 0x00000004 | 0x00000002

    caps = 0x00001000

    if num_mipmaps == 0:
        num_mipmaps = 1
    elif num_mipmaps != 1:
        flags |= 0x00020000
        caps |= 0x00000008 | 0x00400000

    if not compressed:
        flags |= 0x00000008

        a = False

        if compSel[0] != 0 and compSel[1] != 0 and compSel[2] != 0 and compSel[3] == 0: # ALPHA
            a = True
            pflags = 0x00000002

        elif luminance:  # LUMINANCE
            pflags = 0x00020000

        elif RGB:  # RGB
            pflags = 0x00000040

        else: # Not possible...
            return b''

        if has_alpha and not a:
            pflags |= 0x00000001

        size = w * fmtbpp

    else:
        flags |= 0x00080000
        pflags = 0x00000004

        if format_ == "BC1":
            fourcc = b'DXT1'
        elif format_ == "BC2":
            fourcc = b'DXT3'
        elif format_ == "BC3":
            fourcc = b'DXT5'
        elif format_ == "BC4U":
            fourcc = b'ATI1'
        elif format_ == "BC4S":
            fourcc = b'BC4S'
        elif format_ == "BC5U":
            fourcc = b'ATI2'
        elif format_ == "BC5S":
            fourcc = b'BC5S'

    hdr[0:0 + 4] = b'DDS '
    hdr[4:4 + 4] = 124 .to_bytes(4, 'little')
    hdr[8:8 + 4] = flags.to_bytes(4, 'little')
    hdr[12:12 + 4] = h.to_bytes(4, 'little')
    hdr[16:16 + 4] = w.to_bytes(4, 'little')
    hdr[20:20 + 4] = size.to_bytes(4, 'little')
    hdr[28:28 + 4] = num_mipmaps.to_bytes(4, 'little')
    hdr[76:76 + 4] = 32 .to_bytes(4, 'little')
    hdr[80:80 + 4] = pflags.to_bytes(4, 'little')

    if compressed:
        hdr[84:84 + 4] = fourcc
    else:
        hdr[88:88 + 4] = (fmtbpp << 3).to_bytes(4, 'little')

        hdr[92:92 + 4] = compSels[compSel[0]].to_bytes(4, 'little')
        hdr[96:96 + 4] = compSels[compSel[1]].to_bytes(4, 'little')
        hdr[100:100 + 4] = compSels[compSel[2]].to_bytes(4, 'little')
        hdr[104:104 + 4] = compSels[compSel[3]].to_bytes(4, 'little')

    hdr[108:108 + 4] = caps.to_bytes(4, 'little')

    return hdr
