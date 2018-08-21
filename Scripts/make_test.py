#! python3

import sys
import os.path
import shutil
import subprocess
import util
import logging
import convert_dds

import bitflag

def MakeTest(origin, target):
	script_path = util.GetScriptPath()
	
	logging.debug("This is the origin: " + origin)
	logging.debug("This is the target: " + target)
	
	FoldersToCreate = []
	FilesToCreate = []
	util.CreateTarget(target)
	
	logging.debug("Target Created")
		
	for root, subdirs, files in os.walk(origin):
		if root != origin:
			FoldersToCreate.append(root)
			logging.debug("Adding folder ({})".format(root))
		for filename in files:
			file_path = os.path.join(root, filename)
			FilesToCreate.append(file_path)
			logging.debug("Adding file ({})".format(file_path))
	for folderToCreate in FoldersToCreate:
		logging.debug("About to add folder ({})".format(folderToCreate))
		newFolderName = folderToCreate.replace(origin, target)
		logging.debug("New folder name is ({})".format(newFolderName))
		os.mkdir(newFolderName)
		
	for fileToCreate in FilesToCreate:
		logging.debug("About to add file ({})".format(fileToCreate))
		newFileName = fileToCreate.replace(origin, target)
		logging.debug("New filename is ({})".format(newFileName))
		with open(newFileName, "w") as myFile:
			myFile.write("TESTFILE")

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(origin + ".log")
	util.StartTimer()
	MakeTest(origin, target)
	util.EndTimer()