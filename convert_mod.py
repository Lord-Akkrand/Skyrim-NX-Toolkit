#! python3

import sys
import re
import os.path
import shutil
import subprocess
import util
import unpack_mod, convert_path, pack_mod

import bitflag

def ConvertMod(origin, target, bsarch, has_sdk):
	script_path = bsarch.replace("bsarch.exe", "")
	targetData = target + r"\Data"
	mod_name = os.path.basename(origin)
	'''
	print("This is the origin: ", origin)
	print("This is the target: ", target)
	print("This is the target Data: ", targetData)
	print("has_sdk is " + str(has_sdk))
	print("This is the mod name " + mod_name)
	'''
	print("convert_mod.py 2.0")

	unpack_mod.UnpackMod(origin, target, bsarch)
		
	convert_path.ConvertPath(mod_name, target, script_path, has_sdk)

	pack_mod.PackMod(mod_name, target, bsarch)

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	bsarch = sys.argv[3]
	has_sdk = sys.argv[4]
	ConvertMod(origin, target, bsarch, has_sdk)