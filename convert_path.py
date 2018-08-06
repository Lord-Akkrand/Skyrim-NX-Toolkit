#! python3

import sys
import re
import os.path
import shutil
import subprocess
import util
import convert_dds

import bitflag

def ConvertPath(mod_name, target, script_path, has_sdk):
	targetData = target + r"\Data"
	'''
	print("This is the target: ", target)
	print("This is the target Data: ", targetData)
	print("has_sdk is " + str(has_sdk))
	print("This is the mod name " + mod_name)
	'''
	print("convert_path.py 2.0")
		
	texconv = os.path.join(script_path, "texconv.exe")
	id_dds_bat = os.path.join(script_path, "ID_DDS.BAT")
	for root, subdirs, files in os.walk(targetData):
		if root != targetData:
			print("Walking folder " + root)
			os.chdir(root)
			for filename in files:
				if filename.lower().endswith(".dds"):
					file_path = os.path.join(root, filename)
					print("ModConverting " + file_path)
					commandLine = [id_dds_bat, filename]
					#subprocess.call(commandLine, shell=True)
					util.RunCommandLine(commandLine)
					ddsinfo = filename + ".ddsinfo.txt "
					texdiag = filename + ".texdiag.txt "
					convert_dds.ConvertDDS(texconv, targetData, filename, ddsinfo, texdiag, has_sdk)
					os.remove(ddsinfo)
					os.remove(texdiag)

	os.chdir(script_path)

if __name__ == '__main__':
	mod_name = sys.argv[1]
	target = sys.argv[2]
	script_path = sys.argv[3]
	has_sdk = sys.argv[4]
	ConvertPath(mod_name, target, script_path, has_sdk)