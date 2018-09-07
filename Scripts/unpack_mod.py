#! python3

import sys
import os.path
import shutil
import subprocess
import util
import convert_dds

import bitflag

def UnpackMod(origin, target):
	script_path = util.GetScriptPath()
	utilities_path = util.GetUtilitiesPath()
	bsarch = os.path.join(utilities_path, "bsarch.exe")
	mod_name = os.path.basename(origin)
	util.LogDebug("This is the origin: " + origin)
	util.LogDebug("This is the target: " + target)
	util.LogDebug("This is the mod name " + mod_name)
	util.LogInfo("Unpacking " + mod_name)

	def CopyFile(file, filename):
		newFileName = os.path.join(target, file)
		util.LogDebug(filename + "->" + newFileName)
		shutil.copy2(filename, newFileName)

	def UnpackBSA(file, filename):
		util.LogInfo("Unpack BSA " + file)
		commandLine = [bsarch, "unpack", filename, target]
		util.RunCommandLine(commandLine)

	BSAsToUnpack = []
	FilesToRename = []
	
	FilesToCopy = []
	for root, subdirs, files in os.walk(origin):
		for file in files:
			util.LogDebug("   Found <" + file + ">")
			filename = os.path.join(root, file)
			if file.endswith(".bsa"):
				BSAsToUnpack.append( (file, filename) )
			elif file.endswith(".esp") or file.endswith(".ini") or file.endswith(".esm"):
				newFileName = os.path.join(target, file)
				FilesToCopy.append( (filename, newFileName) )
			else:
				relativePath = root.replace(origin, target)
				newFileName = os.path.join(relativePath, file)
				FilesToCopy.append( (filename, newFileName) )
				
	util.LogInfo("Found {} BSAs & {} loose files".format(len(BSAsToUnpack), len(FilesToCopy)))
	for i in range(len(FilesToCopy)):
		fileToCopy = FilesToCopy[i]
		(filename, newFileName) = fileToCopy
		folderName = os.path.dirname(newFileName)
		util.LogDebug("Copying {}->{}, makedirs {}".format(filename, newFileName, folderName))
		os.makedirs(folderName, exist_ok=True)
		shutil.copy2(filename, newFileName)
		sys.stdout.write("Copied {}/{} \r".format(i+1, len(FilesToCopy)))
		sys.stdout.flush()
	sys.stdout.write("\n")
			
	for bsaToUnpack in BSAsToUnpack:
		(file, filename) = bsaToUnpack
		UnpackBSA(file, filename)		

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(origin + ".log")
	util.StartTimer()
	UnpackMod(origin, target)
	util.EndTimer()