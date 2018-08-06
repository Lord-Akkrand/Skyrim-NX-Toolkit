#! python3

import sys
import re
import os.path
import shutil
import subprocess
import util
import convert_dds

import bitflag

def UnpackMod(origin, target, bsarch):
	script_path = bsarch.replace("bsarch.exe", "")
	targetData = target + r"\Data"
	mod_name = os.path.basename(origin)
	'''
	print("This is the origin: ", origin)
	print("This is the target: ", target)
	print("This is the target Data: ", targetData)
	print("This is the mod name " + mod_name)
	'''
	print("unpack_mod.py 2.0")

	def CopyFile(file, filename):
		newFileName = targetData + "\\" + file
		print(filename + "->" + newFileName)
		shutil.copy2(filename, newFileName)

	def UnpackBSA(file, filename):
		commandLine = '"' + bsarch + '" unpack "' + filename + '" "' + targetData + '"'
		print("Command Line:\n" + str(commandLine))
		p = subprocess.Popen(commandLine, shell=True)
		(output, err) = p.communicate()
		p_status = p.wait()

	BSAsToUnpack = []
	FilesToRename = []
		
	for file in os.listdir(targetData):
		print("   Found " + file)
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
	bsarch = sys.argv[3]
	UnpackMod(origin, target, bsarch)