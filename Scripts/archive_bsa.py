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
	utilities_path = util.GetUtilitiesPath()
	archive_original = os.path.join(utilities_path, "Archive.exe") 
	
	logging.debug("Copy Archive.exe to target folder")
	archive = os.path.join(target_folder, "Archive.exe")
	shutil.copy2(archive_original, archive)

	log_basename = "log.txt"
	log_filename = os.path.join(target_folder, log_basename)
	config_basename = "bsa_config.txt"
	config_filename = os.path.join(target_folder, config_basename)
	filelist_basename = "bsa_filelist.txt"
	filelist_filename = os.path.join(target_folder, filelist_basename)
	
	checks = {}
	logging.info("Build File List")
	with open(filelist_filename, 'w') as filelist_file:
		target_data = os.path.join(target_folder, "Data")
		logging.debug("Walking the target directory " + target_data)
		for root, subdirs, files in os.walk(target_data):
			logging.debug('--\nroot = ' + root)
			if root == target_data:
				logging.debug("subdirs: " + str(subdirs))
				lower_case_data_list = [x.lower() for x in subdirs]
				logging.debug("lcds: " + str(lower_case_data_list))
				if "meshes" in lower_case_data_list:
					logging.debug("found meshes")
					checks["Retain Strings During Startup"] = True
					checks["Meshes"] = True
				if "textures" in lower_case_data_list:
					logging.debug("found texttures")
					checks["Textures"] = True
				if "interface" in lower_case_data_list:
					logging.debug("found interface")
					checks["Menus"] = True
				if "music" in lower_case_data_list:
					logging.debug("found music")
					checks["Retain File Names"] = True
					checks["Sounds"] = True
				if "sound" in lower_case_data_list:
					logging.debug("found sound")
					sound_list = os.listdir(os.path.join(target_data, "sound"))
					sound_list_lower = [x.lower() for x in sound_list]
					
					if "fx" in sound_list_lower:
						logging.debug("found sound//fx")
						checks["Retain File Names"] = True
						checks["Sounds"] = True
					if "voice" in sound_list_lower:
						logging.debug("found sound//voice")
						checks["Voices"] = True
				if "shadersfx" in lower_case_data_list:
					logging.debug("found shaders")
					checks["Shaders"] = True
				if "seq" in lower_case_data_list:
					logging.debug("found seq")
					checks["Retain File Names"] = True
					checks["Misc"] = True
				if "grass" in lower_case_data_list:
					logging.debug("found grass")
					checks["Retain File Names"] = True
					checks["Misc"] = True
				if "scripts" in lower_case_data_list:
					logging.debug("found scripts")
					checks["Retain File Names"] = True
					checks["Misc"] = True
				
			else:
				for filename in files:
					if filename != "desktop.ini":
						file_path = os.path.join(root, filename)
						relative_path = file_path.replace(target_folder, '')

						logging.debug('\t- file %s (relative path: %s)' % (filename, relative_path))
						path_no_data = relative_path[6:]
						filelist_file.write(path_no_data + "\n")
	logging.info("Build Config")
	checksOrder = ["Meshes", "Textures", "Menus", "Sounds", "Voices", "Shaders", "Trees", "Fonts", "Misc", "Compress Archive", "Retain Directory Names", "Retain File Names", "Retain File Name Offsets", "Retain Strings During Startup", "XBox 360 Archive", "Embed File Names"]
	with open(config_filename, 'w') as config_file:
		config_file.write("Log: " + log_basename + "\n")
		config_file.write("New Archive\n")
		for check in checksOrder:
			if check in checks:
				config_file.write("Check: " + check + "\n")

		config_file.write("Set File Group Root: Data\\\n")
		config_file.write("Add File Group: " + filelist_basename + "\n")
		config_file.write("Save Archive: " + bsa_filename + "\n")
	logging.info("Run Archive.exe")
	
	commandLine = ["Archive.exe", config_basename]
	os.chdir(target_folder)
	util.RunCommandLine(commandLine)
	with open(log_filename, "r") as log_file:
		for line in log_file:
			logging.debug(line)
	logging.info("Clean Up")
	os.remove(log_filename)
	os.remove(config_filename)
	os.remove(filelist_filename)
	os.remove(archive)
	os.chdir(script_path)
	return os.path.join(target_folder, bsa_filename)

if __name__ == '__main__':
	target_folder = sys.argv[1]
	origin_folder = sys.argv[2]
	bsa_basename = os.path.basename(origin_folder) + ".bsa"
	bsa_basename = bsa_basename.replace(" ", "")
	bsa_filename = os.path.join(target_folder, bsa_basename)
	util.InitialiseLog(bsa_filename + ".log")
	ArchiveBSA(target_folder, bsa_basename)