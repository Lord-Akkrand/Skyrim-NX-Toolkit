#! python3

import sys
import re
import os.path
import shutil
import logging
import util

import subprocess

def ArchiveBSA(target_folder, bsa_filename):
	script_path = util.GetScriptPath()
	archive_original = os.path.join(script_path, "Archive.exe") 
	
	logging.info("Copy Archive.exe to target folder")
	archive = os.path.join(target_folder, "Archive.exe")
	shutil.copy2(archive_original, archive)

	log_basename = "log.txt"
	log_filename = os.path.join(target_folder, log_basename)
	config_basename = "bsa_config.txt"
	config_filename = os.path.join(target_folder, config_basename)
	filelist_basename = "bsa_filelist.txt"
	filelist_filename = os.path.join(target_folder, filelist_basename)
	
	with open(config_filename, 'w') as config_file:
		config_file.write("Log: " + log_basename + "\n")
		config_file.write("New Archive\n")
		config_file.write("Check: Misc\n")
		config_file.write("Check: Compress Archive\n")
		config_file.write("Set File Group Root: Data\\\n")
		config_file.write("Add File Group: " + filelist_basename + "\n")
		config_file.write("Save Archive: Data\\" + bsa_filename + "\n")
		with open(filelist_filename, 'w') as filelist_file:
			
			logging.debug("Walking the target directory " + target_folder)
			for root, subdirs, files in os.walk(target_folder):
				logging.debug('--\nroot = ' + root)
				if root != target_folder:
					for filename in files:
						if filename != "desktop.ini":
							file_path = os.path.join(root, filename)
							relative_path = file_path.replace(target_folder, '')

							logging.debug('\t- file %s (relative path: %s)' % (filename, relative_path))
							path_no_data = relative_path[6:]
							filelist_file.write(path_no_data + "\n")
	commandLine = ["Archive.exe", config_basename]
	os.chdir(target_folder)
	util.RunCommandLine(commandLine)
	with open(log_filename, "r") as log_file:
		for line in log_file:
			logging.debug(line)
	os.remove(log_filename)
	os.remove(config_filename)
	os.remove(filelist_filename)
	os.remove(archive)

if __name__ == '__main__':
	target_folder = sys.argv[1]
	origin_folder = sys.argv[2]
	bsa_basename = os.path.basename(origin_folder) + ".bsa"
	bsa_basename = bsa_basename.replace(" ", "")
	bsa_filename = os.path.join(target_folder, bsa_basename)
	util.InitialiseLog(bsa_filename + ".log")
	ArchiveBSA(target_folder, bsa_basename)