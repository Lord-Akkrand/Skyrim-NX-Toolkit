#! python3

import sys
import os, os.path
import shutil
import subprocess
import util
import logging
import archive_bsa
import bsarch_bsa

import bitflag

def PackMod(mod_name, target):
	script_path = util.GetScriptPath()
	utilities_path = util.GetUtilitiesPath()
	bsarch = os.path.join(utilities_path, "bsarch.exe")
	logging.debug("This is the target: " + target)
	logging.debug("This is the mod name " + mod_name)
	logging.info("Pack Mod")
	
	has_archive = util.HasArchive()
	logging.debug("HasArchive is {}".format(has_archive))
	
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
			useArchive = has_archive
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
				bsa_list = bsarch_bsa.BsarchBSA(temp, target_bsa)
				for bsa_info in bsa_list:
					bsa_filename = bsa_info["FileName"]
					bsa_filepath = bsa_info["Folder"]
					bsa_fullpath = os.path.join(bsa_filepath, bsa_filename)
					newTargetBSA = os.path.join(target, bsa_filename)
					shutil.move(bsa_fullpath, newTargetBSA)
					bsaList.append(newTargetBSA)
			
			util.RemoveTree(temp)
			
	return bsaList

if __name__ == '__main__':
	mod_name = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(target + ".log")
	PackMod(mod_name, target)