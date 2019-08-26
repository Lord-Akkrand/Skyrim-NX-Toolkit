#! python3

import sys
import util
import codecs
import chardet

def ConvertTXT_Internal(filename):
	buffer = None
	with open(filename, "rb") as pcFile:
		buffer = pcFile.read()
		
	encoding = chardet.detect(buffer)["encoding"]
	buffer = buffer.decode(encoding)

	linebreak = checkLineBreak(buffer)
	if linebreak!="\r\n":
		buffer = buffer.replace(linebreak, "\r\n")
		
	with open(filename, "w", encoding="utf32", newline=None) as outFile:
		outFile.write(buffer)
	
	return True

def checkLineBreak(contents):
	for b in ["\r\n","\n","\r"]:
		if b in contents:
			return b
	return "\r\n"

def ConvertTXT(target, filename):
	return ConvertTXT_Internal(filename)

def ConvertTXTAsync(target, filename, logname, ret):
	util.InitialiseMPLog(logname)
	retVal = ConvertTXT(target, filename)
	ret["retVal"] = retVal

if __name__ == '__main__':
	filename = sys.argv[1]
	util.InitialiseLog(filename + ".log")
	util.StartTimer()
	util.LogInfo("Skyrim-NX-Toolkit {} - convert_txt".format(util.GetToolkitVersion()))
	ConvertTXT_Internal(filename)
	util.EndTimer()
	
