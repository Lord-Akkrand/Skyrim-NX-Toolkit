#! python3

import inspect, os

import sys
import os.path
import shutil
import subprocess
import util
import logging
import convert_dds

import bitflag

def UnpackMod(origin, target):
	script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	bsarch = os.path.join(script_path, "bsarch.exe")
	targetData = target + r"\Data"
	mod_name = os.path.basename(origin)
	'''
	logging.debug("This is the origin: " + origin)
	logging.debug("This is the target: " + target)
	logging.debug("This is the target Data: " + targetData)
	logging.debug("This is the mod name " + mod_name)
	'''
	logging.info("Unpack Mod")

	def CopyFile(file, filename):
		newFileName = targetData + "\\" + file
		logging.debug(filename + "->" + newFileName)
		shutil.copy2(filename, newFileName)

	def UnpackBSA(file, filename):
		commandLine = [bsarch, "unpack", filename, targetData]
		util.RunCommandLine(commandLine)
		'''
		commandLine = '"' + bsarch + '" unpack "' + filename + '" "' + targetData + '"'
		logging.debug("Command Line:\n" + str(commandLine))
		p = subprocess.Popen(commandLine, shell=True)
		(output, err) = p.communicate()
		p_status = p.wait()
		'''

	BSAsToUnpack = []
	FilesToRename = []
		
	for file in os.listdir(targetData):
		logging.debug("   Found " + file)
		filename = os.path.join(targetData, file)
		if file.endswith(".bsa"):
			BSAsToUnpack.append( (file, filename) )
		elif file.endswith(".esp") or file.endswith(".ini"):
			newFileName = os.path.join(targetData, mod_name + file[-4:])
			FilesToRename.append( (filename, newFileName) )
			
	for bsaToUnpack in BSAsToUnpack:
		(file, filename) = bsaToUnpack
		UnpackBSA(file, filename)
		os.remove(filename)
		
	for fileToRename in FilesToRename:
		(filename, newFileName) = fileToRename
		os.rename(filename, newFileName)

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(origin + ".log")
	UnpackMod(origin, target)