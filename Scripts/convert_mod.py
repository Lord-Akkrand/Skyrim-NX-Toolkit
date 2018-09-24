#! python3

import sys
import os.path
import shutil
import subprocess
import util
import unpack_mod, reconcile_hkx, convert_path, pack_mod
import inspect, os
import bitflag

def ConvertMod(origin, target, oldrim):
	mod_name = os.path.basename(origin)
	'''
	util.LogDebug("This is the origin: " + origin)
	util.LogDebug("This is the target: " + target)
	util.LogDebug("This is the mod name " + mod_name)
	'''
	util.LogDebug("convert_mod.py 2.0")
	toolkit_path = util.GetToolKitPath()
	util.LogInfo("Convert Mod, ToolkitPath is {}".format(toolkit_path))
	
	util.LogInfo("Convert Mod, create empty folder at target")
	
	util.CreateTarget(target)
	unpack_mod.UnpackMod(origin, target)
	if oldrim:
		reconcile_hkx.ReconcileHKX(target, oldrim)
		
	convert_path.ConvertPath(mod_name, target)

	pack_mod.PackMod(mod_name, target)

def ConvertMod_External(origin, target, oldrim):
	print("<{}>".format(origin))
	util.InitialiseLog(origin + ".log")
	util.StartTimer()
	util.LogInfo("Skyrim-NX-Toolkit {} - convert_mod".format(util.GetToolkitVersion()))
	ConvertMod(origin, target, oldrim)
	util.EndTimer()
	
if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	oldrim = None
	if len(sys.argv) > 2:
		oldrim = sys.argv[3]
	ConvertMod_External(origin, target, oldrim)