#! python3

import sys
import re
import os.path
import sizes
import util
import logging
import shutil

import subprocess

def ConvertHKX(filename):
	util.LogDebug("ConvertHKX : " + filename)
		
	havocBPP = util.GetHavokBPP()
	
	commandLine = [havocBPP, "--stripMeta", "--platformPS4", filename, filename]
	util.RunCommandLine(commandLine)

if __name__ == '__main__':
	filename = sys.argv[1]
	ConvertHKX(filename)