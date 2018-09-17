#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Stella/AboodXD

def toGX2rgb5a1(data):
    new_data = bytearray(len(data))

    for i in range(len(data) // 2):
        pixel = (data[2*i] << 8) | data[2*i+1]

        red = (pixel >> 10) & 0x1F
        green = (pixel >> 5) & 0x1F
        blue = pixel & 0x1F
        alpha = (pixel >> 15) & 1

        new_pixel = (red << 11) | (green << 6) | (blue << 1) | alpha

        new_data[2*i:2*i+2] = new_pixel.to_bytes(2, "big")

    return bytes(new_data)


def toDDSrgb5a1(data):
    new_data = bytearray(len(data))

    for i in range(len(data) // 2):
        pixel = (data[2*i] << 8) | data[2*i+1]

        red = (pixel >> 11) & 0x1F
        green = (pixel >> 6) & 0x1F
        blue = (pixel >> 1) & 0x1F
        alpha = pixel & 1

        new_pixel = (red << 10) | (green << 5) | blue | (alpha << 15)

        new_data[2*i:2*i+2] = new_pixel.to_bytes(2, "big")

    return bytes(new_data)


def toGX2rgba4(data):
    new_data = bytearray(len(data))

    for i in range(len(data) // 2):
        pixel = (data[2*i] << 8) | data[2*i+1]

        red = (pixel >> 8) & 0xF
        green = (pixel >> 4) & 0xF
        blue = pixel & 0xF
        alpha = (pixel >> 12) & 0xF

        new_pixel = (red << 12) | (green << 8) | (blue << 4) | alpha

        new_data[2*i:2*i+2] = new_pixel.to_bytes(2, "big")

    return bytes(new_data)


def toDDSrgba4(data):
    new_data = bytearray(len(data))

    for i in range(len(data) // 2):
        pixel = (data[2*i] << 8) | data[2*i+1]

        red = (pixel >> 12) & 0xF
        green = (pixel >> 8) & 0xF
        blue = (pixel >> 4) & 0xF
        alpha = pixel & 0xF

        new_pixel = (red << 8) | (green << 4) | blue | (alpha << 12)

        new_data[2*i:2*i+2] = new_pixel.to_bytes(2, "big")

    return bytes(new_data)


def rgb8torgbx8(data):
    new_data = bytearray((len(data) // 3) * 4)

    for i in range(len(data) // 3):
        pixel = (data[3*i] << 16) | (data[3*i+1] << 8) | data[3*i+2]

        new_pixel = (pixel << 8) | 255

        new_data[4*i:4*i+4] = new_pixel.to_bytes(4, "big")

    return bytes(new_data)
