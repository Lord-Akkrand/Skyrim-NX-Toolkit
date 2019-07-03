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

	with open(filename, "rb") as hkx64:
		payload = hkx64.read()	

	header_location = payload.find(b'\x00' * 15 + b'\x80' + b'\x00' * 48)
	is_skeleton_container = payload.find(b'hkaSkeleton') > 0
	is_behavior_container = payload.find(b'hkbBehavior') > 0

	# it should not happen here as convert_path already doing some checks
	if is_behavior_container or is_skeleton_container:
		util.LogInfo("Warning, cannot convert {} because <{}>".format(filename, 'SSE hkx animation'))
		return False

	# swap some fields in the AMD64 HKX header structure to make it PS4 compatible
	if header_location > 0:
		is_project_data = payload.find(b'hkbProjectData')
		offset = 72 if is_project_data > 0 else 76
		with open(filename, "wb") as hkxPS4:
			hkxPS4.write(payload[0:18])
			hkxPS4.write(b'\x01')
			hkxPS4.write(payload[19:header_location+16])
			hkxPS4.write(payload[header_location+20:header_location+offset])
			hkxPS4.write(payload[header_location:header_location+4])
			hkxPS4.write(payload[header_location+offset:])
	
	return True

def ConvertHKX64(target, filename):
	return ConvertHKX64_Internal(filename)
	
def ConvertHKX64Async(target, filename, ret):
	retVal = ConvertHKX64(target, filename)
	ret[retVal] = retVal

if __name__ == '__main__':
	filename = sys.argv[1]
	ConvertHKX64_Internal(filename)
