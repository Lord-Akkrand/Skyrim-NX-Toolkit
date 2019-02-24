#! python3
#
# by Zappastuff - 02-19-19
#
# convert 64-bit SSE HKX to PS4 / SWITCH format
#
# DOESN'T WORK for these animation files:
#
# skeleton.hkx
# skeleton_female.hkx
# behaviors HKX (i.e: 0_master.hkx and 1hm_behavior.hkx) usually under a behaviors folder
# FNIS generated behavior files (you can always run FNIS 32 for Modders to recreate them in 32 bit)

import sys
import re
import os.path
import sizes
import util
import shutil

import subprocess

def ConvertHKX64_Internal(filename):
	util.LogDebug("ConvertHKX64 : " + filename)

	hkx64 = open(filename, "rb")
	payload = hkx64.read()
	hkx64.close()	

	magic = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

	found = payload.find(magic)

	# swap some fields in the AMD64 HKX header structure to make it PS4 compatible
	if found > 0:	
		hkxPS4 = open(filename, "wb")
		hkxPS4.write(payload[0:18])
		hkxPS4.write(b'\x01')
		hkxPS4.write(payload[19:found+16])
		hkxPS4.write(payload[found+20:found+80])
		hkxPS4.write(payload[found:found+4])
		hkxPS4.write(payload[found+80:])
		hkxPS4.close() 
	
	return True

def ConvertHKX64(target, filename):
	return ConvertHKX64_Internal(filename)
	
if __name__ == '__main__':
	filename = sys.argv[1]
	ConvertHKX64_Internal(filename)
