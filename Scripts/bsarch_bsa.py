#! python3

import sys
import re
import os.path
import shutil
import logging
import util
import bitflag
import bsa_rules

import subprocess

def BsarchBSA(target_folder, bsa_filename):
	script_path = util.GetScriptPath()
	utilities_path = util.GetUtilitiesPath()
	bsarch = os.path.join(utilities_path, "bsarch.exe")

	log_basename = "log.txt"
	log_filename = os.path.join(target_folder, log_basename)
	config_basename = "bsa_config.txt"
	config_filename = os.path.join(target_folder, config_basename)
	allFilesList = []
	
	Flag_NamedDir = 1
	Flag_NamedFiles = 2
	Flag_Compressed = 4
	Flag_RetainDir = 8
	Flag_RetainName = 16
	Flag_RetainFOff = 32
	Flag_XBox360 = 64
	Flag_StartupStr = 128
	Flag_EmbedName = 256
	Flag_XMem = 512
	Flag_Bit = 1024

	flags = bitflag.BitFlag()

	flags.SetFlag(Flag_NamedDir)
	flags.SetFlag(Flag_NamedFiles)
	
	logging.info("Build File List")
	totalFileSizeTally = 0
	target_data = os.path.join(target_folder, "Data")
	logging.debug("Walking the target directory " + target_data)
	bsaFolders = []
	
	SizeLimitBSA = bsa_rules.BSASizeLimit
	
	for root, subdirs, files in os.walk(target_data):
		logging.debug('--\nroot = ' + root)
		if root != target_data:
			for filename in files:
				if filename != "desktop.ini" and filename != 'thumbs.db':
					file_path = os.path.join(root, filename)
					
					file_size = os.path.getsize(file_path)
					totalFileSizeTally += file_size
	currentFileIndex = None
	if totalFileSizeTally > SizeLimitBSA:
		currentFileIndex = 0
	
	totalWrittenTally = 0
	
	
	currentFileSizeTally = 0
	buffer = ''
	bsaFileWritten = []
	bsa_original_filename = bsa_filename
	temp_data = os.path.join(os.path.dirname(target_data), "Ready")
	def WriteBSA():
		nonlocal currentFileIndex, bsa_filename
		logging.debug("Writing BSA")
		
		if currentFileIndex != None:
			bsa_filename = bsa_original_filename[:-4] + str(currentFileIndex) + ".bsa"
			currentFileIndex += 1
			
		logging.info("Run bsarch.exe")
		
		flags_value = flags.GetValue()
		flags_hexvalue = hex(flags_value)
		
		commandLine = [bsarch, "pack", temp_data, bsa_filename, "-sse", "-af:"+flags_hexvalue]
		util.RunCommandLine(commandLine)
		
		bsaFileWritten.append({"Folder":target_folder, "FileName":bsa_filename})
		util.RemoveTree(temp_data)
	
	for root, subdirs, files in os.walk(target_data):
		logging.debug('--\nroot = ' + root)
		if root == target_data:
			logging.debug("subdirs: " + str(subdirs))
			lower_case_data_list = [x.lower() for x in subdirs]
			logging.debug("lcds: " + str(lower_case_data_list))
			if "meshes" in lower_case_data_list:
				logging.debug("found meshes")
				flags.SetFlag(Flag_StartupStr)
			if "textures" in lower_case_data_list:
				logging.debug("found texttures")
			if "interface" in lower_case_data_list:
				logging.debug("found interface")
			if "music" in lower_case_data_list:
				logging.debug("found music")
				flags.SetFlag(Flag_RetainName)
			if "sound" in lower_case_data_list:
				logging.debug("found sound")
				sound_list = os.listdir(os.path.join(target_data, "sound"))
				sound_list_lower = [x.lower() for x in sound_list]
				
				if "fx" in sound_list_lower:
					logging.debug("found sound//fx")
					flags.SetFlag(Flag_RetainName)
				if "voice" in sound_list_lower:
					logging.debug("found sound//voice")
			if "shadersfx" in lower_case_data_list:
				logging.debug("found shaders")
			if "seq" in lower_case_data_list:
				logging.debug("found seq")
				flags.SetFlag(Flag_RetainName)
			if "grass" in lower_case_data_list:
				logging.debug("found grass")
				flags.SetFlag(Flag_RetainName)
			if "scripts" in lower_case_data_list:
				logging.debug("found scripts")
				flags.SetFlag(Flag_RetainName)
		else:
			for filename in files:
				if filename != "desktop.ini" and filename != 'thumbs.db':
					file_path = os.path.join(root, filename)
					
					file_size = os.path.getsize(file_path)
					newTally = currentFileSizeTally + file_size
					logging.debug("Attempting to add " + file_path + " currentFileSizeTally is " + str(currentFileSizeTally) + " file_size is " + str(file_size))
					if (newTally >= SizeLimitBSA):
						logging.debug("New BSA would be too big, writing current BSA")
						WriteBSA()
						currentFileSizeTally = 0
						
					relative_path = file_path.replace(target_folder, '')
					
					path_no_data = relative_path[6:]
					temp_path = os.path.join(temp_data, path_no_data)
					logging.debug("Moving <{}> to <{}>".format(file_path, temp_path))
					paths_to_create = []
					check_path = os.path.dirname(temp_path)
					
					logging.debug("Checking path {}".format(check_path))
					while not os.path.isdir(check_path):
						logging.debug("{} does not exist.".format(check_path))
						paths_to_create.insert(0, check_path)
						check_path = os.path.dirname(check_path)
						logging.debug("Checking path {}".format(check_path))
					for path_to_create in paths_to_create:
						logging.debug("{} does not exist.".format(check_path))
						os.mkdir(path_to_create)
					shutil.move(file_path, temp_path)
					currentFileSizeTally += file_size
	if currentFileSizeTally > 0:
		WriteBSA()
	
	logging.info("Clean Up")

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
	BsarchBSA(target_folder, bsa_basename)
	util.EndTimer()