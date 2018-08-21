#! python3

import sys
import os.path
import shutil
import subprocess
import util
import logging
import convert_dds

import bitflag

def ConvertPath(mod_name, target):

	script_path = util.GetScriptPath()
	
	logging.info("Convert Path")
	logging.debug("This is the target: " + target)
	logging.debug("This is the mod name " + mod_name)
	
	FilesToConvert = []
	for root, subdirs, files in os.walk(target):
		if root != target:
			logging.debug("Walking folder " + root)
			for filename in files:
				if filename.lower().endswith(".dds"):
					file_path = os.path.join(root, filename)
					FilesToConvert.append(file_path)
	logging.info("Found {} dds files to convert".format(len(FilesToConvert)))
	
	for i in range(len(FilesToConvert)):
		file_path = FilesToConvert[i]
		convert_dds.ConvertDDS(target, file_path)
		sys.stdout.write("Converted {}/{} \r".format(i+1, len(FilesToConvert)))
		sys.stdout.flush()
	sys.stdout.write("\n")
	
if __name__ == '__main__':
	mod_name = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(target + ".log")
	util.StartTimer()
	ConvertPath(mod_name, target)
	util.EndTimer()