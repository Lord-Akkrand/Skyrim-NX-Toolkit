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
		
def GetScriptPath():
	script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	return script_path
	
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