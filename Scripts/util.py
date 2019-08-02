#! python3

import datetime, inspect, logging, os, subprocess, shutil

g_ToolkitVersion = 'v2.6.2'

def GetToolkitVersion():
	return g_ToolkitVersion

gStartTime = 0
def StartTimer():
	global gStartTime
	gStartTime = datetime.datetime.now()
	LogInfo("Timer Started {}".format(gStartTime.strftime('%Y-%m-%d %H:%M:%S')))

def EndTimer():
	ts = datetime.datetime.now()
	delta = ts - gStartTime

	LogInfo("Total Time Taken {}".format(str(delta)))

def RunCommandLine(commandLine, useShell=False):
	LogDebug("RunCommandLine({}, shell={})".format(str(commandLine), str(useShell)))

	p = subprocess.Popen(commandLine, shell=useShell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	output, err = p.communicate()
	p_status = p.wait()
	if output != None:
		output = output.decode('utf-8', errors='ignore')
		#output = output.decode('ascii')
		LogDebug("Output:" + output)#str(output.splitlines()))
	if err != None:
		err = err.decode('utf-8', errors='ignore')
		#err = err.decode('ascii')
		LogDebug("Errors:" + err)#str(err.splitlines()))
	return (output, err)

g_loggingInitialised = False
g_logname = ''
g_tempLog = []
def InitialiseLog(newFileName):
	global g_loggingInitialised, g_logname, g_tempLog
	if not g_loggingInitialised:
		g_loggingInitialised = True
		g_logname = newFileName
		with open(newFileName, "w") as myfile:
			myfile.write("")

		logging.basicConfig(format='%(message)s', filename=newFileName, level=logging.DEBUG)
		logger = logging.getLogger(__name__)

		# define a Handler which writes INFO messages or higher to the sys.stderr
		console = logging.StreamHandler()
		console.setLevel(logging.INFO)
		# set a format which is simpler for console use
		formatter = logging.Formatter('%(message)s')
		# tell the handler to use this format
		console.setFormatter(formatter)
		# add the handler to the root logger
		logging.getLogger('').addHandler(console)

		LogInfo("Logger Initialised {}".format(newFileName))
		for msg in g_tempLog:
			LogInfo(msg)

def GetLogName():
	global g_logname
	return g_logname

def InitialiseMPLog(newFileName):
	global g_loggingInitialised
	if not g_loggingInitialised:
		g_loggingInitialised = True
		logging.basicConfig(format='%(message)s', filename=newFileName, level=logging.DEBUG)
		logger = logging.getLogger(__name__)
		# define a Handler which writes INFO messages or higher to the sys.stderr
		console = logging.StreamHandler()
		console.setLevel(logging.INFO)
		# set a format which is simpler for console use
		formatter = logging.Formatter('%(message)s')
		# tell the handler to use this format
		console.setFormatter(formatter)
		# add the handler to the root logger
		logging.getLogger('').addHandler(console)

g_LogGUI_Initialised = False
g_LogGUI = ''
def InitialiseGUILog():
	global g_LogGUI, g_LogGUI_Initialised
	if not g_LogGUI_Initialised:
		g_LogGUI_Initialised = True
	g_LogGUI = ''

def LogDebug(msg):
	global g_loggingInitialised, g_tempLog
	if g_LogGUI_Initialised:
		g_LogGUI
	else:
		if g_loggingInitialised:
			logging.debug(msg)
		else:
			g_tempLog.append("[Debug]" + msg)

def LogInfo(msg):
	global g_loggingInitialised, g_tempLog
	if g_loggingInitialised:
		logging.info(msg)
	else:
		g_tempLog.append('Info' + msg)

def LogWarn(msg):
	global g_loggingInitialised, g_tempLog
	if g_loggingInitialised:
		logging.warning(msg)
	else:
		g_tempLog.append('Warn' + msg)


def LogError(msg):
	global g_loggingInitialised, g_tempLog
	if g_loggingInitialised:
		logging.error(msg)
	else:
		g_tempLog.append('Error' + msg)

def OldRemoveTree(tree):
	success = False
	for i in range(0,3):
		LogDebug("Remove Tree <" + tree + ">")
		try:
			shutil.rmtree(tree, ignore_errors=True)
			os.rmdir(tree)
			success = True
			break
		except Exception:
			pass
	if not success:
		RemoveTree(tree)
	return success

def RemoveTree(tree):
	success = False
	empty_path = GetEmptyPath()
	commandLine = ["ROBOCOPY", empty_path, tree, "/PURGE", "/XF", ".gitignore"]
	commandLine2 = ["RD", "/s", "/q", tree]
	for i in range(0,3):
		try:
			if os.path.isdir(tree):
				LogDebug("RemoveTree({})".format(tree))
				RunCommandLine(commandLine, True)
				LogDebug("RD")
				RunCommandLine(commandLine2, True)
				LogDebug("rmdir")
				os.rmdir(tree)
			success = True
			break
		except Exception:
			pass
	if not success:
		LogWarn("RemoveTree({}) not successful".format(tree))
	return success

def RenameFile(source_filename, destination_filename):
	success = False
	for i in range(0,3):
		LogDebug("Rename File <" + source_filename + "> to <" + destination_filename + ">")
		try:
			os.rename(source_filename, destination_filename)
			success = True
			break
		except Exception:
			pass
	return success

def RemoveFile(filename):
	success = False
	for i in range(0,3):
		LogDebug("Remove File <" + filename + ">")
		try:
			os.remove(filename)
			success = True
			break
		except Exception:
			pass
	return success

def CreateTarget(target):
	LogInfo("CreateTarget({})".format(target))
	empty_path = GetEmptyPath()

	commandLine = ["ROBOCOPY", empty_path, target, "/MIR", "/XF", ".gitignore"]
	RunCommandLine(commandLine, True)


def CopyOriginToTarget(origin, target):
	LogInfo("CopyOriginToTarget({}, {})".format(origin, target))

	commandLine = ["ROBOCOPY", origin, target, "/MIR"]
	RunCommandLine(commandLine, True)


def GetScriptPath():
	script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	return script_path

def GetEmptyPath():
	toolkit_path = GetToolKitPath()
	empty_path = os.path.join(toolkit_path, "Empty")
	return empty_path

def GetToolKitPath():
	script_path = GetScriptPath()
	toolkit_path = os.path.dirname(script_path)
	return toolkit_path

def GetUtilitiesPath():
	toolkit_path = GetToolKitPath()
	utilities_path = os.path.join(toolkit_path, "Utilities")
	return utilities_path

def HasSDK():
	# NvnTools\NvnTexpkg.exe
	toolkit_path = GetToolKitPath()
	sdk_path = os.path.join(toolkit_path, "NvnTools", "NvnTexpkg.exe")
	return os.path.exists(sdk_path)

def HasArchive():
	# Utilities\Archive.exe
	utilities_path = GetUtilitiesPath()
	archive_path = os.path.join(utilities_path, "Archive.exe")
	return os.path.exists(archive_path)

def GetNvnTexpkg():
	toolkit_path = GetToolKitPath()
	sdk_path = os.path.join(toolkit_path, "NvnTools", "NvnTexpkg.exe")
	return sdk_path

def HasHavokBPP():
	# Utilities\HavokBehaviorPostProcess.exe
	utilities_path = GetUtilitiesPath()
	havok_path = os.path.join(utilities_path, "HavokBehaviorPostProcess.exe")
	return os.path.exists(havok_path)

def GetHavokBPP():
	utilities_path = GetUtilitiesPath()
	havok_path = os.path.join(utilities_path, "HavokBehaviorPostProcess.exe")
	return havok_path

def GetXTXExtract():
	toolkit_path = GetToolKitPath()
	xtx_extract_path = os.path.join(toolkit_path, "XTX-Extractor-master", "xtx_extract.py")
	return xtx_extract_path

def ForceMove(fromFile, toFile):
	shutil.move(fromFile, toFile)
