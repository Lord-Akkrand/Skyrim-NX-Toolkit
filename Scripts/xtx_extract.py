#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# XTX Extractor
# Version 0.1
# Copyright © 2017 Stella/AboodXD

# This file is part of XTX Extractor.

# XTX Extractor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# XTX Extractor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""xtx_extract.py: Decode XTX images."""

import os
import struct
import sys
import time

import dds
import swizzle

formats = {0x00000025: 'NVN_FORMAT_RGBA8',
           0x00000038: 'NVN_FORMAT_RGBA8_SRGB',
           0x0000003d: 'NVN_FORMAT_RGB10A2',
           0x0000003c: 'NVN_FORMAT_RGB565',
           0x0000003b: 'NVN_FORMAT_RGB5A1',
           0x00000039: 'NVN_FORMAT_RGBA4',
           0x00000001: 'NVN_FORMAT_R8',
           0x0000000d: 'NVN_FORMAT_RG8',
           0x00000042: 'DXT1',
           0x00000043: 'DXT3',
           0x00000044: 'DXT5',
           0x00000049: 'BC4U',
           0x0000004a: 'BC4S',
           0x0000004b: 'BC5U',
           0x0000004c: 'BC5S'
           }

BCn_formats = [0x42, 0x43, 0x44, 0x49, 0x4a, 0x4b, 0x4c]

bpps = {0x25: 4, 0x38: 4, 0x3d: 4, 0x3c: 2, 0x3b: 2, 0x39: 2, 1: 1, 0xd: 2,
        0x42: 8, 0x43: 16,0x44: 16, 0x49: 8, 0x4a: 8, 0x4b: 16, 0x4c: 16}


g_arguments = None
		
class NvData:
    pass


class NvHeader(struct.Struct):
    def __init__(self):
        super().__init__('<4I')

    def data(self, data, pos):
        (self.magic,
         self.size_,
         self.majorVersion,
         self.minorVersion) = self.unpack_from(data, pos)


class NvBlockHeader(struct.Struct):
    def __init__(self):
        super().__init__('<2I2Q3I')

    def data(self, data, pos):
        (self.magic,
         self.size_,
         self.dataSize,
         self.dataOff,
         self.type_,
         self.id,
         self.typeIdx) = self.unpack_from(data, pos)


class NvTextureHeader(struct.Struct):
    def __init__(self):
        super().__init__('<Q8I')

    def data(self, data, pos):
        (self.imageSize,
         self.alignment,
         self.width,
         self.height,
         self.depth,
         self.target,
         self.format_,
         self.numMips,
         self.sliceSize) = self.unpack_from(data, pos)


def readNv(f):
    nv = NvData()

    pos = 0

    header = NvHeader()
    header.data(f, pos)

    if header.magic != 0x4E764644: # "NvFD"
        raise ValueError("Invalid file header!")

    if header.majorVersion == 1:
        texHeadBlkType = 2
        dataBlkType = 3
    else:
        raise ValueError("Unsupported XTX version!")

    pos += header.size

    block2 = False
    block3 = False

    images = 0
    imgInfo = 0

    nv.imageSize = []
    nv.alignment = []
    nv.width = []
    nv.height = []
    nv.depth = []
    nv.target = []
    nv.format = []
    nv.numMips = []
    nv.sliceSize = []
    nv.compSel = []
    nv.bpp = []
    nv.realSize = []

    nv.dataSize = []
    nv.data = []

    nv.mipOffsets = []

    while pos < len(f):  # Loop through the entire file, stop if reached the end of the file.
        block = NvBlockHeader()
        block.data(f, pos)

        if block.magic != 0x4E764248: # "NvBH"
            raise ValueError("Invalid block header!")

        pos += block.dataOff

        if block.type_ == texHeadBlkType:
            imgInfo += 1
            block2 = True

            texHead = NvTextureHeader()
            texHead.data(f, pos)

            pos += texHead.size

            if texHead.numMips > 17:
                print("Invalid number of mipmaps for image " + str(imgInfo - 1))
                print("")
                print("Exiting in 5 seconds...")
                time.sleep(5)
                sys.exit(1)

            mipOffsets = []
            for i in range(17):
                mipOffsets.append(f[i * 4 + 3 + pos] << 24 | f[i * 4 + 2 + pos] << 16 | f[i * 4 + 1 + pos] << 8 | f[i * 4 + pos])

            nv.mipOffsets.append(mipOffsets)
            
            pos += block.dataSize - texHead.size

            nv.imageSize.append(texHead.imageSize)
            nv.alignment.append(texHead.alignment)
            nv.width.append(texHead.width)
            nv.height.append(texHead.height)
            nv.depth.append(texHead.depth)
            nv.target.append(texHead.target)
            nv.format.append(texHead.format_)
            nv.numMips.append(texHead.numMips)
            nv.sliceSize.append(texHead.sliceSize)

            if texHead.format_ == 1:
                nv.compSel.append([0, 0, 0, 5])

            elif texHead.format_ == 0xd:
                nv.compSel.append([0, 0, 0, 1])

            elif texHead.format_ == 0x3c:
                nv.compSel.append([0, 1, 2, 5])

            else:
                nv.compSel.append([0, 1, 2, 3])

            bpp = bpps[texHead.format_] if texHead.format_ in formats else 0
            nv.bpp.append(bpp)

            if texHead.format_ in BCn_formats:
                nv.realSize.append(((texHead.width + 3) >> 2) * ((texHead.height + 3) >> 2) * bpp)
            else:
                nv.realSize.append(texHead.width * texHead.height * bpp)

        elif block.type_ == dataBlkType:
            images += 1
            block3 = True

            nv.dataSize.append(block.dataSize)
            nv.data.append(f[pos:pos + block.dataSize])
            pos += block.dataSize

        else:
            pos += block.dataSize

    if images != imgInfo:
        print("")
        print("Whoops, fail! XD")
        print("")
        print("Exiting in 5 seconds...")
        time.sleep(5)
        sys.exit(1)

    if block2:
        if not block3:
            print("")
            print("Image info was found but no Image data was found.")
            print("")
            print("Exiting in 5 seconds...")
            time.sleep(5)
            sys.exit(1)
    if not block2:
        if not block3:
            print("")
            print("No Image was found in this file.")
            print("")
            print("Exiting in 5 seconds...")
            time.sleep(5)
            sys.exit(1)
        elif block3:
            print("")
            print("Image data was found but no Image info was found.")
            print("")
            print("Exiting in 5 seconds...")
            time.sleep(5)
            sys.exit(1)

    nv.numImages = images

    return nv


def get_deswizzled_data(i, nv):
    numImages = nv.numImages
    numMips = nv.numMips[i]
    width = nv.width[i]
    height = nv.height[i]
    depth = nv.depth[i]
    format_ = nv.format[i]
    realSize = nv.realSize[i]
    data = nv.data[i][:realSize]
    bpp = nv.bpp[i]
    mipOffsets = nv.mipOffsets[i]

    if format_ in formats:
        if format_ in [0x25, 0x38]:
            format__ = 28
        elif format_ == 0x3d:
            format__ = 24
        elif format_ == 0x3c:
            format__ = 85
        elif format_ == 0x3b:
            format__ = 86
        elif format_ == 0x39:
            format__ = 115
        elif format_ == 0x1:
            format__ = 61
        elif format_ == 0xd:
            format__ = 49
        elif format_ == 0x42:
            format__ = "BC1"
        elif format_ == 0x43:
            format__ = "BC2"
        elif format_ == 0x44:
            format__ = "BC3"
        elif format_ == 0x49:
            format__ = "BC4U"
        elif format_ == 0x4a:
            format__ = "BC4S"
        elif format_ == 0x4b:
            format__ = "BC5U"
        elif format_ == 0x4c:
            format__ = "BC5S"

        if depth != 1:
            print("")
            print("Unsupported depth!")
            print("")
            if i != (numImages - 1):
                print("Continuing in 5 seconds...")
                time.sleep(5)
                return b'', b'', b''
            else:
                print("Exiting in 5 seconds...")
                time.sleep(5)
                sys.exit(1)

        if numMips - 1:
            print("")
            print("Processing " + str(numMips - 1) + " mipmaps:")

        result = []
        for level in range(numMips):
            if format_ in BCn_formats:
                size = ((max(1, width >> level) + 3) >> 2) * ((max(1, height >> level) + 3) >> 2) * bpp
            else:
                size = max(1, width >> level) * max(1, height >> level) * bpp

            mipOffset = mipOffsets[level]

            if level != 0:
                print(str(level) + ": " + str(max(1, width >> level)) + "x" + str(max(1, height >> level)))

                print(hex(mipOffset))

            data = nv.data[i][mipOffset:mipOffset + size]

            deswizzled = swizzle.deswizzle(max(1, width >> level), max(1, height >> level), format_, data)

            data = deswizzled[:size]

            result.append(data)

        hdr = dds.generateHeader(numMips, width, height, format__, nv.compSel[i], realSize, format_ in BCn_formats)

    else:
        print("")
        print("Unsupported texture format_: " + hex(format_))
        print("")
        if i != (numImages - 1):
            print("Continuing in 5 seconds...")
            time.sleep(5)
            hdr, result = b'', []
        else:
            print("Exiting in 5 seconds...")
            time.sleep(5)
            sys.exit(1)

    return hdr, result


def get_curr_mip_off_size(width, height, bpp, curr_level, compressed):
    off = 0

    for i in range(curr_level - 1):
        level = i + 1
        if compressed:
            off += ((max(1, width >> level) + 3) >> 2) * ((max(1, height >> level) + 3) >> 2) * bpp
        else:
            off += max(1, width >> level) * max(1, height >> level) * bpp

    if compressed:
        size = ((max(1, width >> curr_level) + 3) >> 2) * ((max(1, height >> curr_level) + 3) >> 2) * bpp
    else:
        size = max(1, width >> curr_level) * max(1, height >> curr_level) * bpp

    return off, size


def warn_color():
    print("")
    print("Warning: colors might mess up!!")


def writeNv(f, SRGB, n, numImages, numBlocks):
    width, height, format_, fourcc, dataSize, compSel, numMips, data = dds.readDDS(f, SRGB)

    if 0 in [width, dataSize] and data == []:
        print("")
        if n != (numImages - 1):
            print("Continuing in 5 seconds...")
            time.sleep(5)
            return b''
        else:
            print("Exiting in 5 seconds...")
            time.sleep(5)
            sys.exit(1)

    if format_ not in formats:
        print("")
        print("Unsupported DDS format!")
        print("")
        if n != (numImages - 1):
            print("")
            print("Continuing in 5 seconds...")
            time.sleep(5)
            return b''
        else:
            print("Exiting in 5 seconds...")
            time.sleep(5)
            sys.exit(1)

    if numMips > 16:
        print("")
        print("Invalid number of mipmaps for " + f)
        print("")
        if n != (numImages - 1):
            print("")
            print("Continuing in 5 seconds...")
            time.sleep(5)
            return b''
        else:
            print("Exiting in 5 seconds...")
            time.sleep(5)
            sys.exit(1)

    imageData = data[:dataSize]
    mipData = data[dataSize:]
    numMips += 1

    bpp = bpps[format_]

    alignment = 512

    if numMips - 1:
        print("")
        print("Processing " + str(numMips - 1) + " mipmaps:")

    swizzled_data = bytearray()
    offset = 0
    mipOffsets = []
    for i in range(numMips):
        if not i:
            data = imageData
        else:
            print(str(i) + ": " + str(max(1, width >> i)) + "x" + str(max(1, height >> i)))

            mipOffset, dataSize = get_curr_mip_off_size(width, height, bpp, i, format_ in BCn_formats)

            data = mipData[mipOffset:mipOffset+dataSize]

        mipOffsets.append(offset)

        offset += len(data)

        swizzled_data += swizzle.swizzle(max(1, width >> i), max(1, height >> i), format_, data)

    print("")
    print("// ----- NvTextureHeader Info ----- ")
    print("  imageSize       = " + str(offset))
    print("  alignment       = " + str(alignment))
    print("  width           = " + str(width))
    print("  height          = " + str(height))
    print("  depth           = 1")
    print("  target          = 1")
    print("  format          = " + formats[format_])
    print("  numMips         = " + str(numMips))
    print("  sliceSize       = " + str(offset))
    print("")
    print("  bits per pixel  = " + str(bpp * 8))
    print("  bytes per pixel = " + str(bpp))

    if format_ == 1:
        if compSel not in [[0, 0, 0, 5], [0, 5, 5, 5]]:
            warn_color()

    elif format_ == 0xd:
        if compSel not in [[0, 0, 0, 1], [0, 5, 5, 1]]:
            warn_color()

    elif format_ == 0x3c:
        if compSel != [0, 1, 2, 5]:
            warn_color()

    else:
        if compSel != [0, 1, 2, 3]:
            warn_color()

    block_head_struct = NvBlockHeader()
    tex_blk_head = block_head_struct.pack(0x4E764248, 0x24, 0x78, 0x24, 2, numBlocks, 0)

    numBlocks += 1

    tex_head_struct = NvTextureHeader()
    tex_head = tex_head_struct.pack(offset, alignment, width, height, 1, 1, format_, numMips, offset)

    image_blk_head = block_head_struct.pack(0x4E764248, 0x24, offset, 0x154, 3, numBlocks, 0)

    numBlocks += 1

    align_blk = b'\x00' * 0x130

    output = tex_blk_head + tex_head

    i = 0
    for offset in mipOffsets:
        output += offset.to_bytes(4, 'little')
        i += 1
    for z in range(17 - i):
        output += 0 .to_bytes(4, 'little')

    output += 0x700000004.to_bytes(12, 'little')
    output += image_blk_head
    output += align_blk
    output += swizzled_data

    return output, numBlocks


def printInfo():
    print("")
    print("Usage:")
    print("  xtx_extract [option...] input")
    print("")
    print("Options:")
    print(" -o <output>           Output file, if not specified, the output file will have the same name as the intput file")
    print("                       Will be ignored if the XTX has multiple images")
    print("")
    print("DDS to XTX options:")
    print(" -SRGB <n>             1 if the desired destination format is SRGB, else 0 (0 is the default)")
    print(" -multi <numImages>    number of images to pack into the XTX file (input file must be the first image, 1 is the default)")
    print("")
    print("Supported formats:")
    print(" - NVN_FORMAT_RGBA8")
    print(" - NVN_FORMAT_RGBA8_SRGB")
    print(" - NVN_FORMAT_RGB10A2")
    print(" - NVN_FORMAT_RGB565")
    print(" - NVN_FORMAT_RGB5A1")
    print(" - NVN_FORMAT_RGBA4")
    print(" - NVN_FORMAT_R8")
    print(" - NVN_FORMAT_RG8")
    print(" - DXT1")
    print(" - DXT3")
    print(" - DXT5")
    print(" - BC4U")
    print(" - BC4S")
    print(" - BC5U")
    print(" - BC5S")
    print("")
    print("Exiting in 5 seconds...")
    time.sleep(5)
    sys.exit(1)


def main():
    print("XTX Extractor v0.1")
    print("(C) 2017 Stella/AboodXD")

    input_ = g_arguments[-1]

    if not (input_.endswith('.xtx') or input_.endswith('.dds')):
        printInfo()

    toXTX = False

    if input_.endswith('.dds'):
        toXTX = True

    if "-o" in g_arguments:
        output_ = g_arguments[g_arguments.index("-o") + 1]
    else:
        output_ = os.path.splitext(input_)[0] + (".xtx" if toXTX else ".dds")

    if toXTX:
        if "-SRGB" in g_arguments:
            SRGB = int(g_arguments[g_arguments.index("-SRGB") + 1], 0)
        else:
            SRGB = 0

        multi = False
        if "-multi" in g_arguments:
            multi = True
            numImages = int(g_arguments[g_arguments.index("-multi") + 1], 0)

        if SRGB > 1:
            printInfo()

        if "-o" not in g_arguments and "-multi" in g_arguments:
            output_ = output_[:-5] + ".xtx"

        with open(output_, "wb+") as output:
            head_struct = NvHeader()
            head = head_struct.pack(0x4E764644, 16, 1, 1)

            output.write(head)

            numBlocks = 0

            if multi:
                input_ = input_[:-5]
                for i in range(numImages):
                    print("")
                    print('Converting: ' + input_ + str(i) + ".dds")
                    
                    data, numBlocks = writeNv(input_ + str(i) + ".dds", SRGB, i, numImages, numBlocks)
                    output.write(data)
            else:
                print("")
                print('Converting: ' + input_)

                data, numBlocks = writeNv(input_, SRGB, 0, 1, numBlocks)
                output.write(data)

            block_head_struct = NvBlockHeader()
            eof_blk_head = block_head_struct.pack(0x4E764248, 0x24, 0x18, 0x24, 5, numBlocks, 0)

            output.write(eof_blk_head)
            output.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

    else:
        print("")
        print('Converting: ' + input_)

        with open(input_, "rb") as inf:
            inb = inf.read()

        nv = readNv(inb)

        for i in range(nv.numImages):

            print("")
            print("// ----- NvTextureHeader Info ----- ")
            print("  imageSize       = " + str(nv.imageSize[i]))
            print("  alignment       = " + str(nv.alignment[i]))
            print("  width           = " + str(nv.width[i]))
            print("  height          = " + str(nv.height[i]))
            print("  depth           = " + str(nv.depth[i]))
            print("  target          = " + str(nv.target[i]))
            if nv.format[i] in formats:
                print("  format          = " + formats[nv.format[i]])
            else:
                print("  format          = " + hex(nv.format[i]))
            print("  numMips         = " + str(nv.numMips[i]))
            print("  sliceSize       = " + str(nv.sliceSize[i]))
            if nv.format[i] in formats:
                bpp = nv.bpp[i]
                print("")
                print("  bits per pixel  = " + str(bpp * 8))
                print("  bytes per pixel = " + str(bpp))

            if nv.numImages > 1:
                output_  = os.path.splitext(input_)[0] + str(i) + ".dds"

            hdr, result = get_deswizzled_data(i, nv)

            if hdr == b'' or result == []:
                pass
            else:
                with open(output_, "wb+") as output:
                    output.write(hdr)
                    for data in result:
                        output.write(data)

    print('')
    print('Finished converting: ' + input_)

def main_external(arguments):
	global g_arguments
	g_arguments = arguments
	main()

if __name__ == '__main__':
	main_external(sys.argv)
