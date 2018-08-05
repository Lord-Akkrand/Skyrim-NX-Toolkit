#! python3

import sys
import re
import os.path
import shutil
import subprocess

import bitflag

origin = sys.argv[1]
target = sys.argv[2]
bsarch = sys.argv[3]
has_sdk = sys.argv[4]
script_path = bsarch.replace("bsarch.exe", "")
targetData = target + r"\Data"
mod_name = os.path.basename(origin)
print("This is the origin: ", origin)
print("This is the target: ", target)
print("This is the target Data: ", targetData)
print("has_sdk is " + str(has_sdk))
print("This is the mod name " + mod_name)


def CopyFile(file, filename):
	newFileName = targetData + "\\" + file
	print(filename + "->" + newFileName)
	shutil.copy2(filename, newFileName)

def UnpackBSA(file, filename):
	commandLine = '"' + bsarch + '" unpack "' + filename + '" "' + targetData + '"'
	print("Command Line:\n" + str(commandLine))
	p = subprocess.Popen(commandLine, shell=True)
	(output, err) = p.communicate()
	p_status = p.wait()

BSAsToUnpack = []
FilesToRename = []
	
for file in os.listdir(targetData):
	print("   Found " + file)
	filename = os.path.join(targetData, file)
	if file.endswith(".bsa"):
		BSAsToUnpack.append( (file, filename) )
	elif file.endswith(".esp") or file.endswith(".ini"):
		newFileName = os.path.join(targetData, mod_name + file[-4:])
		FilesToRename.append( (filename, newFileName) )
		
for bsaToUnpack in BSAsToUnpack:
	(file, filename) = bsaToUnpack
	UnpackBSA(file, filename)
	os.remove(filename)
	
for fileToRename in FilesToRename:
	(filename, newFileName) = fileToRename
	os.rename(filename, newFileName)
	


def RunCommandLine(commandLine):
	print("Running commandLine " + str(commandLine))
	p = subprocess.Popen(commandLine, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
	output, err = p.communicate()
	p_status = p.wait()
	if output != None:
		#output = output.decode('ascii')
		print("Output:" + output)#str(output.splitlines()))
	if err != None:
		#err = err.decode('ascii')
		print("Errors:" + err)#str(err.splitlines()))

texconv = os.path.join(script_path, "texconv.exe")
convert_dds = os.path.join(script_path, "convert_dds.py")
id_dds_bat = os.path.join(script_path, "ID_DDS.BAT")
for root, subdirs, files in os.walk(targetData):
	if root != targetData:
		print("Walking folder " + root)
		os.chdir(root)
		for filename in files:
			if filename.lower().endswith(".dds"):
				file_path = os.path.join(root, filename)
				print("ModConverting " + file_path)
				commandLine = [id_dds_bat, filename]
				#subprocess.call(commandLine, shell=True)
				RunCommandLine(commandLine)
				ddsinfo = filename + ".ddsinfo.txt "
				texdiag = filename + ".texdiag.txt "
				RunCommandLine(["py", "-3", convert_dds, texconv, targetData, filename, ddsinfo, texdiag, has_sdk])
				os.remove(ddsinfo)
				os.remove(texdiag)

os.chdir(script_path)

data_list = os.listdir(targetData)
print(str(data_list))

BSAGroups = {
	"Textures":["textures", "facetint"],
	"Meshes":["meshes"],
	"":["grass", "interface", "lodsettings", "music", "scripts", "seq", "shadersfx", "sound", "strings"]
}
ReverseBSAGroups = {}
for bsaName in BSAGroups:
	for folder in BSAGroups[bsaName]:
		ReverseBSAGroups[folder] = bsaName

print(str(ReverseBSAGroups))
MakeBSAs = {}
def AddBSA(name, folder):
	global MakeBSAs
	if name not in MakeBSAs:
		MakeBSAs[name] = []
	MakeBSAs[name].append(folder)
	
def RemoveTree(tree):
	try:
		shutil.rmtree(tree)
	except FileNotFoundError:
		pass

def DetectBSAType(full_path):
	for root, subdirs, files in os.walk(full_path):
		for file in files:
			if file.endswith(".dds") or file.endswith(".DDS"):
				return "Textures"
			if file.endswith(".nif"):
				return "Meshes"
	return ""
	
for path in data_list:
	print('Checking path ' + path)
	full_path = os.path.join(targetData, path)
	if os.path.isdir(full_path):
		if path == "sound":
			RemoveTree(full_path)
		else:
			bsa_type = None
			if path not in ReverseBSAGroups:
				bsa_type = DetectBSAType(full_path)
			else:
				bsa_type = ReverseBSAGroups[path]
			AddBSA(bsa_type, path)

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
	
	if "meshes" in data_list:
		#flags.SetFlag(Flag_Compressed)
		flags.SetFlag(Flag_StartupStr)
	if "seq" in data_list:
		flags.SetFlag(Flag_RetainName)
	if "grass" in data_list:
		flags.SetFlag(Flag_RetainName)
	if "script" in data_list:
		flags.SetFlag(Flag_RetainName)
	if "music" in data_list:
		flags.SetFlag(Flag_RetainName)
	if "sound" in data_list:
		sound_list = os.listdir(os.path.join(target_data_folder, "sound"))
		if "fx" in sound_list:
			flags.SetFlag(Flag_RetainName)

	value = flags.GetValue()
	hexvalue = hex(value)
	return hexvalue

MakeBSAOrder = ["", "Meshes", "Textures"]

print("Make BSAs: \n" + str(MakeBSAs))
for bsa_subname in MakeBSAOrder:
	print("Make BSA <" + bsa_subname + ">")
	if bsa_subname in MakeBSAs:
		print("<" + bsa_subname + "> in MakeBSAs")
		folder_list = MakeBSAs[bsa_subname]
		bsa_file_suffix = bsa_subname
		if bsa_file_suffix != "":
			bsa_file_suffix = " - " + bsa_file_suffix
		temp_data = os.path.join(targetData, "Data" + bsa_file_suffix)
		
		RemoveTree(temp_data)
		
		for folder in folder_list:
			from_folder = os.path.join(targetData, folder)
			to_folder = os.path.join(temp_data, folder)
			shutil.move(from_folder, to_folder)
		bsa_filename = mod_name + bsa_file_suffix + ".bsa"
		target_bsa = os.path.join(targetData, bsa_filename)
		
		archive_flags = GetArchiveFlags(folder_list, temp_data)
		
		flags_arg = "-sse -af:" + str(archive_flags)
		commandLine = '"' + bsarch + '" pack "' + temp_data + '" "' + target_bsa + '" ' + flags_arg
		RunCommandLine(commandLine)
		'''
		print("Command Line:\n" + str(commandLine))
		p = subprocess.Popen(commandLine, shell=True)
		(output, err) = p.communicate()
		p_status = p.wait()
		'''
		checkCommandLine = '"' + bsarch + '" "' + target_bsa + '"'
		RunCommandLine(checkCommandLine)
		'''
		print("Command Line2:\n" + str(checkCommandLine))
		p = subprocess.Popen(checkCommandLine, shell=True)
		(output, err) = p.communicate()
		p_status = p.wait()
		'''
		
		RemoveTree(temp_data)
