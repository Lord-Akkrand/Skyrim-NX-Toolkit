#! python3

import sys
import os.path
import shutil

import subprocess
import bitflag

target = sys.argv[1]
bsarch_path = sys.argv[2]
script_path = bsarch_path.replace("bsarch.exe", "")
base_name = os.path.basename(target)
base_name = base_name.replace(" ", "")
print("This is the target: <" + target + ">")
print("This is scripts path: <" + script_path + ">")
print("This is bsarch path: <" + bsarch_path + ">")
print("This is the base name: <" + base_name + ">")

target_data_folder = os.path.join(target, "Data")
target_data = '"' + target + "\\Data" + '"'
target_bsa = '"' + target + "\\" + base_name + ".bsa" + '"'

data_list = os.listdir(target_data_folder)
print(str(data_list))

def GetArchiveFlags():
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
		flags.SetFlag(Flag_Compressed)
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

archive_flags = GetArchiveFlags()
flags_arg = "-sse -af:" + str(archive_flags)
commandLine = '"' + bsarch_path + '" pack ' + target_data + " " + target_bsa + " " + flags_arg
print("Command Line:\n" + str(commandLine))
p = subprocess.Popen(commandLine, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
checkCommandLine = '"' + bsarch_path + '" ' + target_bsa
print("Command Line2:\n" + str(checkCommandLine))
p = subprocess.Popen(checkCommandLine, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
