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
	
	for root, subdirs, files in os.walk(target):
		if root != target:
			logging.debug("Walking folder " + root)
			for filename in files:
				if filename.lower().endswith(".dds"):
					file_path = os.path.join(root, filename)
					logging.debug("ModConverting " + file_path)
					convert_dds.ConvertDDS(target, file_path)


if __name__ == '__main__':
	mod_name = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(target + ".log")
	ConvertPath(mod_name, target)