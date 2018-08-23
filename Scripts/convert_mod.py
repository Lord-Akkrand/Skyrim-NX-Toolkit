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

def ConvertMod(origin, target, oldrim):
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
	if oldrim:
		reconcile_hkx.ReconcileHKX(target, oldrim)
		
	convert_path.ConvertPath(mod_name, target)

	pack_mod.PackMod(mod_name, target)

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	oldrim = None
	if len(sys.argv) > 2:
		oldrim = sys.argv[3]
	util.InitialiseLog(origin + ".log")
	util.StartTimer()
	ConvertMod(origin, target, oldrim)
	util.EndTimer()