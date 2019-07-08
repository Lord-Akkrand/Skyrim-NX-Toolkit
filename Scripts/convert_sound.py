#! python3

import os
import util
import nx_fuz

def GetTool():
	utilities_path = util.GetUtilitiesPath()
	soundconverter = os.path.join(utilities_path, "Sound", "Skyim NX Audio-Voice Dialog Converter.exe")
	return soundconverter
	
def GetFuzExtractor():
	utilities_path = util.GetUtilitiesPath()
	fuztool = os.path.join(utilities_path, "Sound", "fuz_extractor.exe")
	return fuztool
	
def GetxWMAEncode():
	utilities_path = util.GetUtilitiesPath()
	xWMAEncode = os.path.join(utilities_path, "Sound", "xWMAEncode.exe")
	return xWMAEncode
	
def FUZ2XWMLIP(filepath):
	fuz_extractor = GetFuzExtractor()
	commandLine = [fuz_extractor, "-e", filepath]
	util.RunCommandLine(commandLine)
	util.RemoveFile(filepath)
	
def XWM2WAV(xwmFile, wavFile):
	xWMAEncode = GetxWMAEncode()
	commandLine = [xWMAEncode, xwmFile, wavFile]
	util.RunCommandLine(commandLine)
	util.RemoveFile(xwmFile)
	
def ANY2MCADPCM(wavFile):
	soundconverter = GetTool()
	commandLine = [soundconverter, "-mcadpcm", wavFile]
	(convOutput, convErrors) = util.RunCommandLine(commandLine)
	return (convOutput, convErrors)

def FUZ2MCADPCM(wavFile):
	soundconverter = GetTool()
	commandLine = [soundconverter, "-part1fuz", wavFile]
	(convOutput, convErrors) = util.RunCommandLine(commandLine)
	return (convOutput, convErrors)
	
def LIPMCADPCM2FUZ(baseFile, lipFile, mcadpcmFile):
	nx_fuz.FuzMend(baseFile)
	util.RemoveFile(lipFile)
	util.RemoveFile(mcadpcmFile)

def LP2WAV(wavFile):
	soundconverter = GetTool()
	commandLine = [soundconverter, "-mcwav", wavFile]
	util.RunCommandLine(commandLine)

def ConvertSound_Internal(filepath):
	soundconverter = GetTool()
	# default, if in doubt, use mcadpcm
	argument = "-mcadpcm"
	filename = os.path.basename(filepath)
	
	baseFile = filepath[:-4]
	wavFile = baseFile + ".wav"
	xwmFile = baseFile + ".xwm"
	lipFile = baseFile + ".lip"
	mcadpcmFile = baseFile + ".mcadpcm"
	fuzFile = baseFile + ".fuz"
	
	util.LogDebug("Convert Sound <{}>".format(filename))
	if filename.endswith(".fuz"):
		(convOutput, convErrors) = FUZ2MCADPCM(filepath)
		if "Unknown Error" in convOutput or "Not Implemented" in convOutput:
			return False
		
		if os.path.exists(lipFile) and os.path.exists(mcadpcmFile):
			LIPMCADPCM2FUZ(baseFile, lipFile, mcadpcmFile)
		
			if os.path.exists(filepath):
				return True
		return False
	else:
		if "_lp." in filename or "_lpm." in filename:
			LP2WAV(filepath)
		elif filename.endswith(".xwm") and os.path.exists(lipFile):
			XWM2WAV(xwmFile, wavFile)
		
			(convOutput, convErrors) = ANY2MCADPCM(wavFile)
			if "Unknown Error" in convOutput or "Not Implemented" in convOutput:
				return False
		
			LIPMCADPCM2FUZ(baseFile, lipFile, mcadpcmFile)
			
			if not os.path.exists(fuzFile):
				return False
		else:
			(convOutput, convErrors) = ANY2MCADPCM(filepath)
			
			if "Unknown Error" in convOutput or "Not Implemented" in convOutput:
				return False
	return True
	
def ConvertSound(target, filepath):
	return ConvertSound_Internal(filepath)

def ConvertSoundAsync(target, filename, logname, ret):
	util.InitialiseMPLog(logname)
	retVal = ConvertSound(target, filename)
	ret["retVal"] = retVal

if __name__ == '__main__':
	filepath = sys.argv[1]
	util.InitialiseLog(filepath + ".log")
	util.StartTimer()
	util.LogInfo("Skyrim-NX-Toolkit {} - convert_txt".format(util.GetToolkitVersion()))
	ConvertSound_Internal(filepath)
	util.EndTimer()