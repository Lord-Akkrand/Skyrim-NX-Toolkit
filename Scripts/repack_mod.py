#! python3

import sys
import os.path
import shutil
import subprocess
import util
import unpack_mod, reconcile_hkx, convert_path, pack_mod
import inspect, os
import bitflag

def RepackMod(origin, target):
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
	
def RepackMod_External(origin, target):
	util.InitialiseLog(origin + ".log")
	util.StartTimer()
	util.LogInfo("Skyrim-NX-Toolkit {} - repack_mod".format(util.GetToolkitVersion()))
	RepackMod(origin, target)
	util.EndTimer()

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(origin + ".log")
	util.StartTimer()
	RepackMod(origin, target)
	util.EndTimer()