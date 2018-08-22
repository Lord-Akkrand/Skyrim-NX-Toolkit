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
	
	BSARules = []
	# In order to be placed in a BSA you must meet all the criteria.  First rule evaluated wins.
	BSARules.append({"BSA":"Animations", "Folder":"meshes", "Extension":"hkx"})
	BSARules.append({"BSA":"Animations", "Folder":"meshes", "Extension":"txt"})
	
	BSARules.append({"BSA":"Meshes", "Folder":"meshes"})
	BSARules.append({"BSA":"Meshes", "Folder":"lodsettings"})
	
	BSARules.append({"BSA":"Misc", "Folder":"grass"})
	BSARules.append({"BSA":"Misc", "Folder":"scripts"})
	BSARules.append({"BSA":"Misc", "Folder":"seq"})
	BSARules.append({"BSA":"Shaders", "Folder":"shadersfx"})
	
	BSARules.append({"BSA":"Sounds", "Folder":"music"})
	BSARules.append({"BSA":"Sounds", "Folder":"sound\\fx"})
	
	BSARules.append({"BSA":"Textures", "Folder":"textures"})
	
	BSARules.append({"BSA":"Voices", "Folder":"sound\\voice"})
	
	BSAs = {}
	
	def DefineBSA(bsa_name):
		nonlocal BSAs
		temp = os.path.join(target, "Temp - " + bsa_name)
		temp_data = os.path.join(temp, "Data")
		util.RemoveTree(temp)
		os.makedirs(temp_data, exist_ok=True)
		BSAs[bsa_name] = temp_data
	
	def ApplyRuleToFolder(rule, folder):
		bsa_name = rule["BSA"]
		if bsa_name not in BSAs:
			DefineBSA(bsa_name)
			
		shutil.move(folder, BSAs[bsa_name])
		
	def ApplyRuleToFile(rule, file_path):
		bsa_name = rule["BSA"]
		if bsa_name not in BSAs:
			DefineBSA(bsa_name)
		relative_path = os.path.relpath(file_path, target)
		target_folder = os.path.join(BSAs[bsa_name], relative_path)
		os.makedirs(target_folder, exist_ok=True)
		filename = os.path.basename(file_path)
		target_path = os.path.join(target_folder, filename)
		shutil.move(file_path, target_path)
	
	RemoveFolders = []
	for root, subdirs, files in os.walk(target):
		relative_folder = os.path.relpath(root, target)
		#logging.debug("Walking relative folder " + relative_folder)
		if root == target:
			for child in subdirs:
				logging.info("Children {}".format(child))
				RemoveFolders.append(os.path.join(target, root))
		else:
			# First check if there is an unqualified path rule for this folder (like "scripts" are only placed in Misc)
			folderCount = 0
			lastRuleMatch = None
			for rule in BSARules:
				if "Folder" in rule and rule["Folder"].startswith(relative_folder):
					folderCount += 1
					lastRuleMatch = rule
			if folderCount == 1:
				logging.debug("ApplyRuleToFolder({}) -> {}".format(lastRuleMatch["BSA"], relative_folder))
				ApplyRuleToFolder(lastRuleMatch, root)
			else:
				#logging.debug("No folder match, check files")
				for filename in files:
					file_path = os.path.join(root, filename)
					relative_path = os.path.relpath(file_path, target)
					should_apply = False
					for rule in BSARules:
						should_apply = True
						if should_apply and "Folder" in rule:
							#logging.debug("checking folder rule {} vs relative_folder {}".format(rule["Folder"], relative_folder))
							should_apply = should_apply and relative_folder.startswith(rule["Folder"])
						if should_apply and "Extension" in rule:
							#logging.debug("checking extension rule {} vs filename {}".format(rule["Extension"], filename))
							should_apply = should_apply and filename.endswith(rule["Extension"])
						if should_apply:
							logging.debug("Applying BSA {} for {}".format(rule["BSA"], file_path))
							ApplyRuleToFile(rule, file_path)
							break
					if not should_apply:
						logging.debug("Could not apply rule for <{}>".format(relative_path))
						for rule in BSARules:
							should_apply = True
							if should_apply and "Folder" in rule:
								logging.debug("checking folder rule {} vs relative_folder {}".format(rule["Folder"], relative_folder))
								should_apply = should_apply and relative_folder.startswith(rule["Folder"])
							if should_apply and "Extension" in rule:
								logging.debug("checking extension rule {} vs filename {}".format(rule["Extension"], filename))
								should_apply = should_apply and filename.endswith(rule["Extension"])
	logging.info("Cleanup")
	for folder in RemoveFolders:
		logging.info("Cleanup {}".format(folder))
		util.RemoveTree(folder)
		
	print("Done")
	'''
	BSAGroups = {
		"Textures":["textures", "facetint"],
		"Meshes":["meshes"],
		"":["grass", "interface", "lodsettings", "music", "scripts", "seq", "shadersfx", "sound", "strings"]
	}
	
	ReverseBSAGroups = {}
	for bsaName in BSAGroups:
		for folder in BSAGroups[bsaName]:
			ReverseBSAGroups[folder] = bsaName
			
	FileTypeToBSA = {
		"hkx":"Animations",
		"dds":"Textures",
		"nif":"Meshes",
	}
	logging.debug(str(ReverseBSAGroups))
	MakeBSAs = {}
	def AddBSA(name, folder, MakeBSAs):
		if name not in MakeBSAs:
			MakeBSAs[name] = []
		MakeBSAs[name].append(folder)
	
	def DetectBSAType(full_path):
		for root, subdirs, files in os.walk(full_path):
			for file in files:
				file_ext = file.lower()[:-3]
				if file_ext in FileTypeToBSA:
					return FileTypeToBSA[file_ext]
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

	MakeBSAOrder = ["", "Meshes", "Textures", "Animations"]
	
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
	'''

if __name__ == '__main__':
	mod_name = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(target + ".log")
	util.StartTimer()
	PackMod(mod_name, target)
	logging.shutdown()
	util.EndTimer()