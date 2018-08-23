#! python3

import sys
import re
import os.path
import shutil
import logging
import util
import bsa_rules

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
	allFilesList = []
	
	checks = {}
	logging.info("Build File List")
	totalFileSizeTally = 0
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
					file_size = os.path.getsize(file_path)
					totalFileSizeTally += file_size
					logging.debug("totalFileSizeTally is now: " + str(totalFileSizeTally))
					allFilesList.append( {'FileName': filename, 'FilePath': file_path, 'RelativePath': relative_path, 'PathNoData': path_no_data, 'FileSize':file_size} )
	
	
	SizeLimitBSA = bsa_rules.BSASizeLimit
	
	currentFileIndex = None
	currentFileSizeTally = 0
	buffer = ''
	bsaFileWritten = []
	bsa_original_filename = bsa_filename
	def WrtiteBSA():
		nonlocal currentFileIndex, buffer, bsa_filename
		logging.debug("Writing BSA with filelist:<" + buffer + ">")
		filelist_basename = "bsa_filelist.txt"
		if currentFileIndex != None:
			filelist_basename = "bsa_filelist" + str(currentFileIndex) + ".txt"
			bsa_filename = bsa_original_filename[:-4] + str(currentFileIndex) + ".bsa"
			currentFileIndex += 1
			
		filelist_filename = os.path.join(target_folder, filelist_basename)
		with open(filelist_filename, 'w') as filelist_file:
			filelist_file.write(buffer)
		buffer = ''
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
		os.remove(log_filename)
		os.remove(filelist_filename)
		os.remove(config_filename)
		bsaFileWritten.append({"Folder":target_folder, "FileName":bsa_filename})
		
		
	if totalFileSizeTally > SizeLimitBSA:
		currentFileIndex = 0
	
	totalWrittenTally = 0
	for fileInfo in allFilesList:
		file_size = fileInfo['FileSize']
		newTally = currentFileSizeTally + file_size
		totalWrittenTally = totalWrittenTally + file_size
		logging.debug("Adding " + fileInfo['FileName'] + " currentFileSizeTally is " + str(currentFileSizeTally) + " file_size is " + str(file_size) + " totalWrittenTally is " + str(totalWrittenTally))
		buffer += fileInfo['PathNoData'] + "\n"
		currentFileSizeTally += file_size
		if (newTally >= SizeLimitBSA) or (totalWrittenTally >= totalFileSizeTally):
			WrtiteBSA()
			currentFileSizeTally = 0
		
	if buffer != '':
		logging.warning("BUFFER NOT EMPTY!")
		
	
	
	logging.info("Clean Up")

	util.RemoveFile(archive)

	os.chdir(script_path)
	return bsaFileWritten

if __name__ == '__main__':
	target_folder = sys.argv[1]
	origin_folder = sys.argv[2]
	bsa_basename = os.path.basename(origin_folder) + ".bsa"
	bsa_basename = bsa_basename.replace(" ", "")
	bsa_filename = os.path.join(target_folder, bsa_basename)
	util.InitialiseLog(bsa_filename + ".log")
	util.StartTimer()
	ArchiveBSA(target_folder, bsa_basename)
	util.EndTimer()