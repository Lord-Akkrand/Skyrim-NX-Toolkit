#! python3

import os
import util
import sys
import toolkit_config

def ConvertNIF_Internal(filename):
	utilities_path = util.GetUtilitiesPath()
	nswnifopt = os.path.join(utilities_path, "nswnifopt.exe")

	util.LogDebug("ConvertNIF_Internal: " + " " +  filename)

	conversionMode = toolkit_config.get_setting("Meshes", "ConversionMode")
	commandLine = [nswnifopt, conversionMode, filename]
	util.RunCommandLine(commandLine)
	
	return True

def ConvertNIF(target, filename):
	return ConvertNIF_Internal(filename)

def ConvertNIFAsync(target, filename, logname, ret):
	util.InitialiseMPLog(logname)
	retVal = ConvertNIF(target, filename)
	ret["retVal"] = retVal

if __name__ == '__main__':
	filename = sys.argv[1]
	util.InitialiseLog(filename + ".log")
	util.StartTimer()
	util.LogInfo("Skyrim-NX-Toolkit {} - convert_nif".format(util.GetToolkitVersion()))
	ConvertNIF_Internal(filename)
	util.EndTimer()
	