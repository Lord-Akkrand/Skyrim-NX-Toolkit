#! python3

import sys
import re
import os.path
import sizes
import util
import logging
import shutil

import subprocess

	
def ConvertHKX_Internal(filename):
	util.LogDebug("ConvertHKX : " + filename)
		
	havocBPP = util.GetHavokBPP()
	
	commandLine = [havocBPP, "--stripMeta", "--platformPS4", filename, filename]
	util.RunCommandLine(commandLine)
	
	return True

def ConvertHKX(target, filename):
	return ConvertHKX_Internal(filename)
	
if __name__ == '__main__':
	filename = sys.argv[1]
	ConvertHKX_Internal(filename)