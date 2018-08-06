#! python3

import subprocess

def RunCommandLine(commandLine):
	print("Running commandLine " + str(commandLine))
	p = subprocess.Popen(commandLine, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
	output, err = p.communicate()
	p_status = p.wait()
	if output != None:
		#output = output.decode('ascii')
		print("Output:" + output)#str(output.splitlines()))
	if err != None:
		#err = err.decode('ascii')
		print("Errors:" + err)#str(err.splitlines()))
