#! python3

import sys
import re
import os.path
import shutil

import subprocess

target = sys.argv[1]
archive_path = sys.argv[2]
script_path = archive_path.replace("Archive.exe", "")
base_name = os.path.basename(target)
base_name = base_name.replace(" ", "")
print("This is the target: <" + target + ">")
print("This is scripts path: <" + script_path + ">")
print("This is archive path: <" + archive_path + ">")
print("This is the base name: <" + base_name + ">")

log_basename = base_name + "_log.txt"
log_filename = os.path.join(script_path, log_basename)
mod_config_basename = base_name + "_mod.txt"
mod_config_filename = os.path.join(script_path, mod_config_basename)
mod_filelist_basename = base_name + "_filelist.txt"
mod_filelist_filename = os.path.join(script_path, mod_filelist_basename)
mod_bsa_basename = base_name + ".bsa"
mod_bsa_filename = os.path.join(script_path, mod_bsa_basename)

with open(mod_config_filename, 'w') as mod_file:
	mod_file.write("Log: " + log_basename + "\n")
	mod_file.write("New Archive\n")
	mod_file.write("Set File Group Root: " + target + "\\Data\\\n")
	mod_file.write("Add File Group: " + mod_filelist_basename + "\n")
	mod_file.write("Save Archive: " + mod_bsa_basename + "\n")
	with open(mod_filelist_filename, 'w') as mod_file_list:
		
		print("Walking the target directory " + target)
		for root, subdirs, files in os.walk(target):
			#print('--\nroot = ' + root)
			if root != target:
				
				'''
				for subdir in subdirs:
					print('\t- subdirectory ' + subdir)
				'''

				for filename in files:
					if filename != "desktop.ini":
						file_path = os.path.join(root, filename)
						relative_path = file_path.replace(target, '')

						#print('\t- file %s (full path: %s)' % (filename, file_path))
						print('\t- file %s (relative path: %s)' % (filename, relative_path))
						path_no_data = relative_path[6:]
						mod_file_list.write(path_no_data + "\n")
		
		print("Command Line:\n" + archive_path + " " + mod_config_basename)
		p = subprocess.Popen([archive_path, mod_config_basename], shell=True)
		(output, err) = p.communicate()
		p_status = p.wait()
		print(p_status)
		archive_log = open(log_filename, 'r').read()
		print("ARCHIVE LOG:")
		print(archive_log)
		