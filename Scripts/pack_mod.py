#! python3

import sys
import os, os.path
import shutil
import subprocess
import util
import logging
import archive_bsa
import bsarch_bsa
import bsa_rules

import bitflag

def PackMod(mod_name, target):
	script_path = util.GetScriptPath()
	utilities_path = util.GetUtilitiesPath()
	bsarch = os.path.join(utilities_path, "bsarch.exe")
	util.LogDebug("This is the target: " + target)
	util.LogDebug("This is the mod name " + mod_name)
	util.LogInfo("Pack Mod")
	
	has_archive = util.HasArchive()
	util.LogDebug("HasArchive is {}".format(has_archive))
	
	data_list = os.listdir(target)
	util.LogDebug(str(data_list))
	
	BSARules = bsa_rules.BSARules
	
	BSAs = {}
	
	def DefineBSA(bsa_name):
		nonlocal BSAs
		temp = os.path.join(target, "Temp - " + bsa_name)
		temp_data = os.path.join(temp, "Data")
		util.RemoveTree(temp)
		os.makedirs(temp_data, exist_ok=True)
		BSAs[bsa_name] = temp_data
	
	numFoldersToMove = 0
	numFilesToMove = 0
	numFoldersMoved = 0
	numFilesMoved = 0
	def ApplyRuleToFolder(rule, folder):
		nonlocal numFoldersMoved
		bsa_name = rule["BSA"]
		if bsa_name not in BSAs:
			DefineBSA(bsa_name)
		
		move_to_folder = BSAs[bsa_name]
		child = os.path.basename(folder)
		parent = os.path.dirname(folder)
		if parent != target:
			util.LogDebug("parent is not target")
			rel_parent = os.path.relpath(parent, target)
			util.LogDebug("rel_parent is {}".format(rel_parent))
			move_to_folder = os.path.join(move_to_folder, rel_parent, child)
			util.LogDebug("move_to_folder is {}".format(move_to_folder))
		shutil.move(folder, move_to_folder)
		util.LogDebug("moving {} to {}".format(folder, move_to_folder))
		numFoldersMoved += 1
		sys.stdout.write("Moved Files {}/{} Folders {}/{} \r".format(numFilesMoved, numFilesToMove, numFoldersMoved, numFoldersToMove))
		sys.stdout.flush()
		
	def ApplyRuleToFile(rule, file_path):
		nonlocal numFilesMoved
		bsa_name = rule["BSA"]
		if bsa_name not in BSAs:
			DefineBSA(bsa_name)
		relative_path = os.path.relpath(file_path, target)
		target_path = os.path.join(BSAs[bsa_name], relative_path)
		target_folder = os.path.dirname(target_path)
		
		os.makedirs(target_folder, exist_ok=True)
		util.LogDebug("moving {} to {}".format(file_path, target_path))
		shutil.move(file_path, target_path)
		numFilesMoved += 1
		sys.stdout.write("Moved Files {}/{} Folders {}/{} \r".format(numFilesMoved, numFilesToMove, numFoldersMoved, numFoldersToMove))
		sys.stdout.flush()
	
	ignoreMovedFolders = []
	for root, subdirs, files in os.walk(target):
		relative_folder = os.path.relpath(root, target)
		if root != target:
			# Check if this folder is ignored already
			ignoreThisFolder = False
			for ignored in ignoreMovedFolders:
				if relative_folder.startswith(ignored):
					ignoreThisFolder = True
			if not ignoreThisFolder:
				# Now check if there is an unqualified path rule for this folder (like "scripts" are only placed in Misc)
				folderCount = 0
				lastRuleMatch = None
				for rule in BSARules:
					if "Folder" in rule and relative_folder.startswith(rule["Folder"]):
						folderCount += 1
						lastRuleMatch = rule
				if folderCount == 1:
					numFoldersToMove += 1
					ignoreMovedFolders.append(relative_folder)
				else:
					for filename in files:
						util.LogDebug(os.path.join(relative_folder, filename))
						numFilesToMove += 1
	util.LogInfo("Files ({}) / Folders ({}) to move".format(numFilesToMove, numFoldersToMove))
	
	RemoveFolders = []
	for root, subdirs, files in os.walk(target):
		relative_folder = os.path.relpath(root, target)
		#util.LogDebug("Walking relative folder " + relative_folder)
		if root == target:
			for child in subdirs:
				util.LogDebug("Children {}".format(child))
				RemoveFolders.append(os.path.join(target, child))
		else:
			# First check if there is an unqualified path rule for this folder (like "scripts" are only placed in Misc)
			folderCount = 0
			lastRuleMatch = None
			for rule in BSARules:
				if "Folder" in rule and relative_folder.startswith(rule["Folder"]):
					folderCount += 1
					lastRuleMatch = rule
			if folderCount == 1:
				util.LogDebug("ApplyRuleToFolder({}) -> {}".format(lastRuleMatch["BSA"], relative_folder))
				ApplyRuleToFolder(lastRuleMatch, root)
			else:
				#util.LogDebug("No folder match, check files")
				for filename in files:
					file_path = os.path.join(root, filename)
					relative_path = os.path.relpath(file_path, target)
					should_apply = False
					for rule in BSARules:
						should_apply = True
						if should_apply and "Folder" in rule:
							#util.LogDebug("checking folder rule {} vs relative_folder {}".format(rule["Folder"], relative_folder))
							should_apply = should_apply and relative_folder.startswith(rule["Folder"])
						if should_apply and "Extension" in rule:
							#util.LogDebug("checking extension rule {} vs filename {}".format(rule["Extension"], filename))
							should_apply = should_apply and filename.endswith(rule["Extension"])
						if should_apply:
							util.LogDebug("Applying BSA {} for {}".format(rule["BSA"], file_path))
							ApplyRuleToFile(rule, file_path)
							break
					if not should_apply:
						util.LogWarn("Could not apply rule for <{}>".format(relative_path))
						for rule in BSARules:
							should_apply = True
							if should_apply and "Folder" in rule:
								util.LogDebug("checking folder rule {} vs relative_folder {}".format(rule["Folder"], relative_folder))
								should_apply = should_apply and relative_folder.startswith(rule["Folder"])
							if should_apply and "Extension" in rule:
								util.LogDebug("checking extension rule {} vs filename {}".format(rule["Extension"], filename))
								should_apply = should_apply and filename.endswith(rule["Extension"])
	sys.stdout.write("\n")
	util.LogInfo("Cleanup old folders")
	for folder in RemoveFolders:
		util.LogDebug("Cleanup {}".format(folder))
		util.RemoveTree(folder)
	
	SafePlugins = ["skyrim.esm", "dawnguard.esm", "hearthfires.esm", "dragonborn.esm"]
	MoveFromTo = []
	def CleanPluginSpecificPaths(cleanup_directory):
		for root, subdirs, files in os.walk(cleanup_directory):
			directory = root.lower()
			dir_name = os.path.basename(directory)
			if (dir_name.endswith("esm") or dir_name.endswith("esp")) and dir_name not in SafePlugins:
				new_path = os.path.join(os.path.dirname(directory), "skyrim.esm")
				
				if not os.path.isdir(new_path):
					logging.debug("Rename plugin directory {} to {}".format(directory, new_path))
					os.rename(directory, new_path)
				else:
					logging.debug("Move plugin files from directory {} to {}".format(directory, new_path))
					MoveFromTo.append( (directory, new_path) )
					'''
					for file in files:
						file_path = os.path.join(directory, file)
						new_file_path = os.path.join(new_path, file)
						logging.debug("Move {} to {}".format(file_path, new_file_path))
						shutil.move(file_path, new_file_path)
					for subdir in subdirs:
						sub_path = os.path.join(directory, subdir)
						#new_sub_path = os.path.join(new_path, subdir)
						logging.debug("Move {} to {}".format(sub_path, new_path))
						shutil.move(sub_path, new_path)
					'''
		for moveFromTo in MoveFromTo:
			(move_from, move_to) = moveFromTo
			logging.debug("Need to move from {} to {}".format(move_from, move_to))
			for root, subdirs, files in os.walk(move_from):
				for file in files:
					file_path = os.path.join(root, file)
					relative_path = os.path.relpath(root, move_from)
					new_path = os.path.join(move_to, relative_path)
					
					logging.debug("Moving file from {} to {}".format(file_path, new_path))
					new_directory = os.path.dirname(new_path)
					os.makedirs(new_directory, exist_ok=True)
					shutil.move(file_path, new_path)
					
	util.LogDebug("Build BSAs")
	bsaList = []
	for bsa_name in BSAs:
		temp_data = BSAs[bsa_name]
		temp = os.path.dirname(temp_data)
		bsa_file_suffix = ""
		if bsa_name != "":
			bsa_file_suffix = " - " + bsa_name
		
		CleanPluginSpecificPaths(temp_data)
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
	
	util.LogDebug("PackMod Done")
	return bsaList

if __name__ == '__main__':
	mod_name = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(target + ".log")
	util.StartTimer()
	PackMod(mod_name, target)
	logging.shutdown()
	util.EndTimer()