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

def ConvertMod(origin, target):
	mod_name = os.path.basename(origin)
	'''
	logging.debug("This is the origin: " + origin)
	logging.debug("This is the target: " + target)
	logging.debug("This is the mod name " + mod_name)
	'''
	logging.debug("convert_mod.py 2.0")
	
	logging.info("Convert Mod, create empty folder at target")
	
	util.CreateTarget(target)
	unpack_mod.UnpackMod(origin, target)
		
	convert_path.ConvertPath(mod_name, target)

	pack_mod.PackMod(mod_name, target)

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(origin + ".log")
	util.StartTimer()
	ConvertMod(origin, target)
	util.EndTimer()