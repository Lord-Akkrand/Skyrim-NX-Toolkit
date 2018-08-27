#! python3

import sys
import os.path
import shutil
import subprocess
import util
import logging
import convert_dds
import convert_hkx

import bitflag

def ConvertPath(mod_name, target):

	script_path = util.GetScriptPath()
	
	util.LogInfo("Convert Path")
	util.LogDebug("This is the target: " + target)
	util.LogDebug("This is the mod name " + mod_name)
	
	has_havoc = util.HasHavokBPP()
	
	ConvertListDDS = []
	ConvertListHKX = []
	for root, subdirs, files in os.walk(target):
		if root != target:
			util.LogDebug("Walking folder " + root)
			for filename in files:
				if filename.lower().endswith(".dds"):
					file_path = os.path.join(root, filename)
					ConvertListDDS.append(file_path)
				elif filename.lower().endswith(".hkx"):
					file_path = os.path.join(root, filename)
					ConvertListHKX.append(file_path)
					
	util.LogInfo("Found {} dds files to convert".format(len(ConvertListDDS)))
	if has_havoc: util.LogInfo("Found {} hkx files to convert".format(len(ConvertListHKX)))
	
	for i in range(len(ConvertListDDS)):
		file_path = ConvertListDDS[i]
		convert_dds.ConvertDDS(target, file_path)
		sys.stdout.write("Converted {}/{} DDS \r".format(i+1, len(ConvertListDDS)))
		sys.stdout.flush()
	sys.stdout.write("\n")
	
	if has_havoc:
		for i in range(len(ConvertListHKX)):
			file_path = ConvertListHKX[i]
			convert_hkx.ConvertHKX(file_path)
			sys.stdout.write("Converted {}/{} HKX \r".format(i+1, len(ConvertListHKX)))
			sys.stdout.flush()
		sys.stdout.write("\n")
	
if __name__ == '__main__':
	mod_name = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(target + ".log")
	util.StartTimer()
	ConvertPath(mod_name, target)
	util.EndTimer()