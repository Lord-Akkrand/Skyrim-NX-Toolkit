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
	targetData = target + r"\Data"
	'''
	logging.debug("This is the target: " + target)
	logging.debug("This is the target Data: " + targetData)
	logging.debug("This is the mod name " + mod_name)
	'''
	logging.info("Convert Path")
	
	for root, subdirs, files in os.walk(targetData):
		if root != targetData:
			logging.debug("Walking folder " + root)
			for filename in files:
				if filename.lower().endswith(".dds"):
					file_path = os.path.join(root, filename)
					logging.debug("ModConverting " + file_path)
					convert_dds.ConvertDDS(targetData, file_path)


if __name__ == '__main__':
	mod_name = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(target + ".log")
	ConvertPath(mod_name, target)