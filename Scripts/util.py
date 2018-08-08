#! python3

import inspect, logging, os, pathlib, subprocess

def RunCommandLine(commandLine):
	logging.debug("Running commandLine " + str(commandLine))
	p = subprocess.Popen(commandLine, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
	output, err = p.communicate()
	p_status = p.wait()
	if output != None:
		#output = output.decode('ascii')
		logging.debug("Output:" + output)#str(output.splitlines()))
	if err != None:
		#err = err.decode('ascii')
		logging.debug("Errors:" + err)#str(err.splitlines()))
	return (output, err)

g_loggingInitialised = False
def InitialiseLog(newFileName):
	global g_loggingInitialised
	if not g_loggingInitialised:
		g_loggingInitialised = True
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
		
		logging.info("Logger Initialised")
		
def OldRemoveTree(tree):
	success = False
	for i in range(0,3):
		logging.debug("Remove Tree <" + tree + ">")
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
	for i in range(0,3):
		try:
			logging.debug("RemoveTree({})".format(tree))
			RunCommandLine(commandLine)
			os.rmdir(tree)
			success = True
			break
		except Exception:
			pass
	if not success:
		logging.warning("RemoveTree({}) not successful".format(tree))
	return success
		
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
	try:
		# NvnTools\NvnTexpkg.exe
		script_path = GetScriptPath()
		sdk_path = os.path.join(script_path, "NvnTools", "NvnTexpkg.exe")
		my_file = pathlib.Path(sdk_path)
		my_abs_path = my_file.resolve()
	except FileNotFoundError:
		# doesn't exist
		return False
	else:
		# exists
		return True