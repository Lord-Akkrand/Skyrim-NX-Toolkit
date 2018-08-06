#! python3

import sys
import os.path
import shutil
import subprocess
import util
import logging
import unpack_mod, convert_path, pack_mod
import inspect, os
import bitflag

def ConvertMod(origin, target, has_sdk):
	targetData = target + r"\Data"
	mod_name = os.path.basename(origin)
	'''
	logging.debug("This is the origin: " + origin)
	logging.debug("This is the target: " + target)
	logging.debug("This is the target Data: " + targetData)
	logging.debug("has_sdk is " + str(has_sdk))
	logging.debug("This is the mod name " + mod_name)
	'''
	logging.debug("convert_mod.py 2.0")
	
	logging.info("Convert Mod")
	
	unpack_mod.UnpackMod(origin, target)
		
	convert_path.ConvertPath(mod_name, target, has_sdk)

	pack_mod.PackMod(mod_name, target)

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	has_sdk = sys.argv[3]
	util.InitialiseLog(origin + ".log")
	ConvertMod(origin, target, has_sdk)