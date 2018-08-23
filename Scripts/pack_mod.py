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
	logging.debug("This is the target: " + target)
	logging.debug("This is the mod name " + mod_name)
	logging.info("Pack Mod")
	
	has_archive = util.HasArchive()
	logging.debug("HasArchive is {}".format(has_archive))
	
	data_list = os.listdir(target)
	logging.debug(str(data_list))
	
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
			logging.debug("parent is not target")
			rel_parent = os.path.relpath(parent, target)
			logging.debug("rel_parent is {}".format(rel_parent))
			move_to_folder = os.path.join(move_to_folder, rel_parent, child)
			logging.debug("move_to_folder is {}".format(move_to_folder))
		shutil.move(folder, move_to_folder)
		logging.debug("moving {} to {}".format(folder, move_to_folder))
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
		logging.debug("moving {} to {}".format(file_path, target_path))
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
						logging.debug(os.path.join(relative_folder, filename))
						numFilesToMove += 1
	logging.info("Files ({}) / Folders ({}) to move".format(numFilesToMove, numFoldersToMove))
	
	RemoveFolders = []
	for root, subdirs, files in os.walk(target):
		relative_folder = os.path.relpath(root, target)
		#logging.debug("Walking relative folder " + relative_folder)
		if root == target:
			for child in subdirs:
				logging.debug("Children {}".format(child))
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
						logging.warning("Could not apply rule for <{}>".format(relative_path))
						for rule in BSARules:
							should_apply = True
							if should_apply and "Folder" in rule:
								logging.debug("checking folder rule {} vs relative_folder {}".format(rule["Folder"], relative_folder))
								should_apply = should_apply and relative_folder.startswith(rule["Folder"])
							if should_apply and "Extension" in rule:
								logging.debug("checking extension rule {} vs filename {}".format(rule["Extension"], filename))
								should_apply = should_apply and filename.endswith(rule["Extension"])
	sys.stdout.write("\n")
	logging.info("Cleanup old folders")
	for folder in RemoveFolders:
		logging.debug("Cleanup {}".format(folder))
		util.RemoveTree(folder)
	
	logging.debug("Build BSAs")
	bsaList = []
	for bsa_name in BSAs:
		temp_data = BSAs[bsa_name]
		temp = os.path.dirname(temp_data)
		bsa_file_suffix = ""
		if bsa_name != "":
			bsa_file_suffix = " - " + bsa_name
			
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
	
	logging.debug("PackMod Done")
	return bsaList

if __name__ == '__main__':
	mod_name = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(target + ".log")
	util.StartTimer()
	PackMod(mod_name, target)
	logging.shutdown()
	util.EndTimer()