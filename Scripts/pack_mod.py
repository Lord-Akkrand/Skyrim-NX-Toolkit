#! python3

import sys
import os, os.path
import shutil
import subprocess
import util
import logging
import archive_bsa

import bitflag

def PackMod(mod_name, target):
	script_path = util.GetScriptPath()
	utilities_path = util.GetUtilitiesPath()
	bsarch = os.path.join(utilities_path, "bsarch.exe")
	logging.debug("This is the target: " + target)
	logging.debug("This is the mod name " + mod_name)
	logging.info("Pack Mod")

	data_list = os.listdir(target)
	logging.debug(str(data_list))

	BSAGroups = {
		"Textures":["textures", "facetint"],
		"Meshes":["meshes"],
		"":["grass", "interface", "lodsettings", "music", "scripts", "seq", "shadersfx", "sound", "strings"]
	}
	ReverseBSAGroups = {}
	for bsaName in BSAGroups:
		for folder in BSAGroups[bsaName]:
			ReverseBSAGroups[folder] = bsaName

	logging.debug(str(ReverseBSAGroups))
	MakeBSAs = {}
	def AddBSA(name, folder, MakeBSAs):
		if name not in MakeBSAs:
			MakeBSAs[name] = []
		MakeBSAs[name].append(folder)
		
	def DetectBSAType(full_path):
		for root, subdirs, files in os.walk(full_path):
			for file in files:
				if file.endswith(".dds") or file.endswith(".DDS"):
					return "Textures"
				if file.endswith(".nif"):
					return "Meshes"
		return ""
		
	for path in data_list:
		logging.debug('Checking path ' + path)
		full_path = os.path.join(target, path)
		if os.path.isdir(full_path):
			if path == "sound":
				util.RemoveTree(full_path)
			else:
				bsa_type = None
				if path not in ReverseBSAGroups:
					bsa_type = DetectBSAType(full_path)
				else:
					bsa_type = ReverseBSAGroups[path]
				AddBSA(bsa_type, path, MakeBSAs)

	def GetArchiveFlags(data_list, target_data_folder):
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
		lower_case_data_list = map(str.lower, data_list)
		
		if "meshes" in lower_case_data_list:
			#flags.SetFlag(Flag_Compressed)
			flags.SetFlag(Flag_StartupStr)
		if "seq" in lower_case_data_list:
			flags.SetFlag(Flag_RetainName)
		if "grass" in lower_case_data_list:
			flags.SetFlag(Flag_RetainName)
		if "scripts" in lower_case_data_list:
			flags.SetFlag(Flag_RetainName)
		if "music" in lower_case_data_list:
			flags.SetFlag(Flag_RetainName)
		if "sound" in lower_case_data_list:
			sound_list = os.listdir(os.path.join(target_data_folder, "sound"))
			if "fx" in lower_case_data_list:
				flags.SetFlag(Flag_RetainName)

		value = flags.GetValue()
		hexvalue = hex(value)
		return hexvalue

	MakeBSAOrder = ["", "Meshes", "Textures"]
	
	bsaList = []
	logging.debug("Make BSAs: \n" + str(MakeBSAs))
	for bsa_subname in MakeBSAOrder:
		logging.debug("Make BSA <" + bsa_subname + ">")
		if bsa_subname in MakeBSAs:
			logging.debug("<" + bsa_subname + "> in MakeBSAs")
			logging.info("Making BSA <" + bsa_subname + ">")
			folder_list = MakeBSAs[bsa_subname]
			bsa_file_suffix = bsa_subname
			if bsa_file_suffix != "":
				bsa_file_suffix = " - " + bsa_file_suffix
			temp = os.path.join(target, "Temp" + bsa_file_suffix)
			temp_data = os.path.join(temp, "Data")
			
			util.RemoveTree(temp)
			
			for folder in folder_list:
				from_folder = os.path.join(target, folder)
				to_folder = os.path.join(temp_data, folder)
				shutil.move(from_folder, to_folder)
			bsa_filename = mod_name + bsa_file_suffix + ".bsa"
			target_bsa = os.path.join(target, bsa_filename)
			useArchive = True
			if useArchive:
				bsa_list = archive_bsa.ArchiveBSA(temp, bsa_filename)
				for bsa_info in bsa_list:
					bsa_filename = bsa_info["FileName"]
					bsa_filepath = bsa_info["Folder"]
					bsa_fullpath = os.path.join(bsa_filepath, bsa_filename)
					newTargetBSA = os.path.join(target, bsa_filename)
					shutil.move(bsa_fullpath, newTargetBSA)
					bsaList.append(newTargetBSA)
			else:
				archive_flags = GetArchiveFlags(folder_list, temp_data)
				
				flags_arg = "-sse -af:" + str(archive_flags)
				commandLine = [bsarch, "pack", temp_data, target_bsa, "-sse", "-af:"+archive_flags]
				#commandLine = '"' + bsarch + '" pack "' + temp_data + '" "' + target_bsa + '" ' + flags_arg
				util.RunCommandLine(commandLine)

				checkCommandLine = [bsarch, target_bsa]
				#checkCommandLine = '"' + bsarch + '" "' + target_bsa + '"'
				util.RunCommandLine(checkCommandLine)
				bsaList.append(target_bsa)
			
			util.RemoveTree(temp)
			
	return bsaList

if __name__ == '__main__':
	mod_name = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(target + ".log")
	PackMod(mod_name, target)