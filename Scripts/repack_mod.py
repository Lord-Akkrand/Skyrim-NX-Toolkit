#! python3

import sys
import os.path
import shutil
import subprocess
import util
import logging
import unpack_mod, reconcile_hkx, convert_path, pack_mod
import inspect, os
import bitflag

def RepackMod(origin, target, oldrim):
	mod_name = os.path.basename(origin)
	'''
	util.LogDebug("This is the origin: " + origin)
	util.LogDebug("This is the target: " + target)
	util.LogDebug("This is the mod name " + mod_name)
	'''
	util.LogDebug("convert_mod.py 2.0")
	
	util.LogInfo("Convert Mod, create empty folder at target")
	
	util.CreateTarget(target)
	unpack_mod.UnpackMod(origin, target)
	pack_mod.PackMod(mod_name, target)

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	oldrim = None
	util.InitialiseLog(origin + ".log")
	util.StartTimer()
	RepackMod(origin, target, oldrim)
	util.EndTimer()