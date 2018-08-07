#! python3

import sys
import os.path
import shutil
import subprocess
import util
import logging
import convert_dds

import bitflag

def UnpackMod(origin, target):
	script_path = util.GetScriptPath()
	utilities_path = util.GetUtilitiesPath()
	bsarch = os.path.join(utilities_path, "bsarch.exe")
	targetData = target + r"\Data"
	mod_name = os.path.basename(origin)
	logging.debug("This is the origin: " + origin)
	logging.debug("This is the target: " + target)
	logging.debug("This is the target Data: " + targetData)
	logging.debug("This is the mod name " + mod_name)
	logging.info("Unpacking " + mod_name)

	def CopyFile(file, filename):
		newFileName = targetData + "\\" + file
		logging.debug(filename + "->" + newFileName)
		shutil.copy2(filename, newFileName)

	def UnpackBSA(file, filename):
		logging.info("Unpack BSA " + file)
		commandLine = [bsarch, "unpack", filename, targetData]
		util.RunCommandLine(commandLine)

	BSAsToUnpack = []
	FilesToRename = []
		
	for file in os.listdir(origin):
		logging.debug("   Found <" + file + ">")
		filename = os.path.join(origin, file)
		if file.endswith(".bsa"):
			BSAsToUnpack.append( (file, filename) )
		elif file.endswith(".esp") or file.endswith(".ini"):
			newFileName = os.path.join(targetData, mod_name + file[-4:])
			shutil.copy2(filename, newFileName)
			
	for bsaToUnpack in BSAsToUnpack:
		(file, filename) = bsaToUnpack
		UnpackBSA(file, filename)		

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(origin + ".log")
	UnpackMod(origin, target)