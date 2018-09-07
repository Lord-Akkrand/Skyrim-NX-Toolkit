#! python3

import sys
import os.path
import shutil
import subprocess
import util
import convert_dds

import bitflag

def MakeTest(origin, target):
	script_path = util.GetScriptPath()
	
	util.LogDebug("This is the origin: " + origin)
	util.LogDebug("This is the target: " + target)
	
	FoldersToCreate = []
	FilesToCreate = []
	util.CreateTarget(target)
	
	util.LogDebug("Target Created")
		
	for root, subdirs, files in os.walk(origin):
		if root != origin:
			FoldersToCreate.append(root)
			util.LogDebug("Adding folder ({})".format(root))
		for filename in files:
			file_path = os.path.join(root, filename)
			FilesToCreate.append(file_path)
			util.LogDebug("Adding file ({})".format(file_path))
	for folderToCreate in FoldersToCreate:
		util.LogDebug("About to add folder ({})".format(folderToCreate))
		newFolderName = folderToCreate.replace(origin, target)
		util.LogDebug("New folder name is ({})".format(newFolderName))
		os.mkdir(newFolderName)
		
	for fileToCreate in FilesToCreate:
		util.LogDebug("About to add file ({})".format(fileToCreate))
		newFileName = fileToCreate.replace(origin, target)
		util.LogDebug("New filename is ({})".format(newFileName))
		with open(newFileName, "w") as myFile:
			myFile.write("TESTFILE")

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(origin + ".log")
	util.StartTimer()
	MakeTest(origin, target)
	util.EndTimer()