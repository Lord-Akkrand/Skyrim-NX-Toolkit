#! python3

import os
import util

def GetTool():
	utilities_path = util.GetUtilitiesPath()
	soundconverter = os.path.join(utilities_path, "Sound", "Skyim NX Audio-Voice Dialog Converter.exe")
	return soundconverter

	
def ConvertSound_Internal(filepath):
	
	# default, if in doubt, use mcadpcm
	argument = "-mcadpcm"
	filename = os.path.basename(filepath)
	util.LogDebug("Convert Sound <{}>".format(filename))
	if filename.endswith(".fuz"):
		argument = "-fuz"
	elif "_lp." in filename or "_lpm." in filename:
		argument = "-mcwav"
		
	soundconverter = GetTool()
	commandLine = [soundconverter, argument, filepath]
	(convOutput, convErrors) = util.RunCommandLine(commandLine)
	
	if "Unknown Error" in convOutput or "Not Implemented" in convOutput:
		return False
	return True
	
def ConvertSound(target, filepath):
	return ConvertSound_Internal(filepath)
	
if __name__ == '__main__':
	filepath = sys.argv[1]
	util.InitialiseLog(filepath + ".log")
	util.StartTimer()
	util.LogInfo("Skyrim-NX-Toolkit {} - convert_txt".format(util.GetToolkitVersion()))
	ConvertSound_Internal(filepath)
	util.EndTimer()