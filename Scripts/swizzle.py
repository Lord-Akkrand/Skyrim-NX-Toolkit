# Original algorithm by gdkchan
# Ported and improved (a tiny bit) by Stella/AboodXD

BCn_formats = [0x42, 0x43, 0x44, 0x49, 0x4a, 0x4b, 0x4c]

bpps = {0x25: 4, 0x38: 4, 0x3d: 4, 0x3c: 2, 0x3b: 2, 0x39: 2, 1: 1, 0xd: 2,
        0x42: 8, 0x43: 16,0x44: 16, 0x49: 8, 0x4a: 8, 0x4b: 16, 0x4c: 16}

xBases = {1: 4, 2: 3, 4: 2, 8: 1, 16: 0}

padds = {1: 64, 2: 32, 4: 16, 8: 8, 16: 4}


def roundSize(size, pad):
    mask = pad - 1
    if size & mask:
        size &= ~mask
        size +=  pad

    return size


def pow2RoundUp(v):
    v -= 1

    v |= (v+1) >> 1
    v |= v >>  2
    v |= v >>  4
    v |= v >>  8
    v |= v >> 16

    return v + 1


def isPow2(v):
    return v and not v & (v - 1)


def countZeros(v):
    numZeros = 0

    for i in range(32):
        if v & (1 << i):
            break

        numZeros += 1

    return numZeros


def deswizzle(width, height, format_, data):
    pos_ = 0

    bpp = bpps[format_]

    origin_width = width
    origin_height = height

    if format_ in BCn_formats:
        origin_width = (origin_width + 3) // 4
        origin_height = (origin_height + 3) // 4

    xb = countZeros(pow2RoundUp(origin_width))
    yb = countZeros(pow2RoundUp(origin_height))

    hh = pow2RoundUp(origin_height) >> 1;

    if not isPow2(origin_height) and origin_height <= hh + hh // 3 and yb > 3:
        yb -= 1

    width = roundSize(origin_width, padds[bpp])

    result = bytearray(data)

    xBase = xBases[bpp]

    for y in range(origin_height):
        for x in range(origin_width):
            pos = getAddr(x, y, xb, yb, width, xBase) * bpp

            if pos_ + bpp <= len(data) and pos + bpp <= len(data):
                result[pos_:pos_ + bpp] = data[pos:pos + bpp]

            pos_ += bpp

    return result


def swizzle(width, height, format_, data):
    pos_ = 0

    bpp = bpps[format_]

    origin_width = width
    origin_height = height

    if format_ in BCn_formats:
        origin_width = (origin_width + 3) // 4
        origin_height = (origin_height + 3) // 4

    xb = countZeros(pow2RoundUp(origin_width))
    yb = countZeros(pow2RoundUp(origin_height))

    hh = pow2RoundUp(origin_height) >> 1;

    if not isPow2(origin_height) and origin_height <= hh + hh // 3 and yb > 3:
        yb -= 1

    width = roundSize(origin_width, padds[bpp])

    result = bytearray(data)

    xBase = xBases[bpp]

    for y in range(origin_height):
        for x in range(origin_width):
            pos = getAddr(x, y, xb, yb, width, xBase) * bpp

            if pos + bpp <= len(data) and pos_ + bpp <= len(data):
                result[pos:pos + bpp] = data[pos_:pos_ + bpp]

            pos_ += bpp

    return result


def getAddr(x, y, xb, yb, width, xBase):
    xCnt    = xBase
    yCnt    = 1
    xUsed   = 0
    yUsed   = 0
    address = 0

    while (xUsed < xBase + 2) and (xUsed + xCnt < xb):
        xMask = (1 << xCnt) - 1
        yMask = (1 << yCnt) - 1

        address |= (x & xMask) << xUsed + yUsed
        address |= (y & yMask) << xUsed + yUsed + xCnt

        x >>= xCnt
        y >>= yCnt

        xUsed += xCnt
        yUsed += yCnt

        xCnt = max(min(xb - xUsed, 1), 0)
        yCnt = max(min(yb - yUsed, yCnt << 1), 0)

    address |= (x + y * (width >> xUsed)) << (xUsed + yUsed)

    return address
