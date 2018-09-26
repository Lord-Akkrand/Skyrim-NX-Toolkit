#! python3

import sys
import re
import os.path
import sizes
import util
import shutil

import subprocess

Unknown = 0
PC = 1
NX = 2
#PNG = 3

Types = []
Magic = {}
ReturnCodes = {}
def AddType(name, magic, code):
	Types.append(name)
	Magic[name] = magic
	ReturnCodes[name] = code

AddType('Magic_DDS', b'\x44\x44\x53', PC)
AddType('Magic_XTX', b'\x44\x46\x76\x4E', NX)
#AddType('Magic_PNG', b'\x89\x50\x4E\x0D', PNG)

def CheckDDS_Internal(filename):
	util.LogDebug("CheckDDS : " + filename)
	
	with open(filename, "rb") as file:
		file.seek(0, 0)
		fourBytes = file.read(4)
		
		for typeName in Types:
			magic = Magic[typeName]
			isType = True
			for i in range(len(magic)):
				if magic[i] != fourBytes[i]:
					#util.LogDebug("<{}> vs <{}> failed at {}".format(str(fourBytes), str(magic), i))
					isType = False
					break
			if isType:
				util.LogDebug("{} match for {} with {}".format(typeName, filename, str(fourBytes)))
				return ReturnCodes[typeName]
		util.LogDebug("No match for {} with {}".format(filename, str(fourBytes)))
	return Unknown

def CheckDDS(target, filename):
	return CheckDDS_Internal(filename)
	
if __name__ == '__main__':
	filename = sys.argv[1]
	CheckDDS_Internal(filename)