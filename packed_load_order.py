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
script_path = bsarch.replace("bsarch.exe", "")
targetData = target + r"\Data"
print("This is the origin: ", origin)
print("This is the target: ", target)
print("This is the target Data: ", targetData)

print("Make sure the target is empty")
if os.access(target, os.F_OK):
	print("Target exists, removing")
	#shutil.rmtree(target)
	os.system('rmdir /S /Q "{}"'.format(target))
print("Create empty target")
os.mkdir(target)
os.mkdir(targetData)
if not os.access(targetData, os.F_OK):
	print("Error creating targetData")
	sys.exit(1)

loadOrderTxt = origin + r"\LoadOrder.txt"
loadOrder = open(loadOrderTxt, 'r').read()
#print("LOAD ORDER <" + loadOrder + ">")
loadOrderList = loadOrder.splitlines()
loadOrderStart = int(loadOrderList[0])
loadOrderList = loadOrderList[1:]
print("ESP Start at " + str(loadOrderStart))
print("LOAD ORDER LIST <" + str(loadOrderList) + ">")


pristineFolder = origin + r"\Pristine"
pristineSkyrimIni = pristineFolder + r"\Skyrim.ini"
print("Attempt to open " + pristineSkyrimIni)
pristineSkyrim = open(pristineSkyrimIni, 'r').read()
#print("PRISTINE:\n" + pristineSkyrim + "END PRISTINE")
newSkyrimIni = pristineSkyrim

languageInis = {}
for file in os.listdir(pristineFolder):
	if file != "Skyrim.ini":
		#print("Language ini <" + file + ">")
		languageInis[file] = pristineFolder + "\\" + file

print("Language Inis:")
for languageIni in languageInis:
	liFilename = languageInis[languageIni]
	print(languageIni, liFilename)

def GetArchiveList(aln, buffer, flags=None):
	print("Find existing " + aln)
	alPattern = "(" + aln + r"=[^\n$]*)[\n$]*"
	if flags != None:
		alPattern = re.compile(alPattern, flags)
	al = re.search(alPattern, buffer)
	if al == None:
		print("Cannot find " + aln + ", bailing")
		print("BUFFER" + buffer + "ENDBUFFER")
		sys.exit(1)
	retVal = al.group(1)
	print("<" + retVal + ">")
	return retVal
sResourceArchiveList = GetArchiveList("sResourceArchiveList", newSkyrimIni)
sResourceArchiveList2 = GetArchiveList("sResourceArchiveList2", newSkyrimIni)

def GetTestFile(tfn):
	tfn = str(tfn)
	print("Find test file " + tfn)
	tfPattern = "([;]*sTestFile" + tfn + r"=[^\n]*)\n"
	tf = re.search(tfPattern, newSkyrimIni)
	if tf == None:
		print("Cannot find " + tfn + ", bailing")
		sys.exit(1)
	retVal = tf.group(1)
	print("<" + retVal + ">")
	return retVal

CurrentTestFileIDX = loadOrderStart
sTestFiles = {}
for i in range(CurrentTestFileIDX, 11):
	sTestFiles["sTestFile" + str(i)] = GetTestFile(i)

def CopyFile(file, filename):
	newFileName = targetData + "\\" + file
	print(filename + "->" + newFileName)
	shutil.copy2(filename, newFileName)
	
def InsertTestFile(name, filename):
	global CurrentTestFileIDX, newSkyrimIni
	currentTestFile = "sTestFile" + str(CurrentTestFileIDX)
	CurrentTestFileIDX = CurrentTestFileIDX + 1
	newTestFile = currentTestFile + "=" + name
	newSkyrimIni = newSkyrimIni.replace(sTestFiles[currentTestFile], newTestFile)
	print(newTestFile)
	CopyFile(file, filename)
#print("TESTFILES<" + str(sTestFiles) + ">")

def UnpackBSA(file, filename):
	commandLine = '"' + bsarch + '" unpack "' + filename + '" "' + targetData + '"'
	print("Command Line:\n" + str(commandLine))
	p = subprocess.Popen(commandLine, shell=True)
	(output, err) = p.communicate()
	p_status = p.wait()
	
newResourceArchiveList2 = sResourceArchiveList2

def InsertTextureBSA(name):
	global newResourceArchiveList2
	newResourceArchiveList2 += ", " + name
	print(newResourceArchiveList2)

newResourceArchiveList = sResourceArchiveList
def InsertMainBSA(name):
	global newResourceArchiveList
	newResourceArchiveList += ", " + name
	print(newResourceArchiveList)

iniPattern = r"^[; ]*([^=]*)=([^$]*)$"
def InsertIni(filename):
	global newSkyrimIni
	buffer = open(filename, 'r').read()
	lines = buffer.splitlines()
	pendingAdditions = []
	currentHeader = ''
	def EndHeader():
		global newSkyrimIni
		if len(pendingAdditions) > 0 and currentHeader != '':
			currentHeaderSearch = currentHeader + "\n"
			print("Search for <" + currentHeaderSearch + ">")
			newHeader = currentHeaderSearch
			for newKeyValue in pendingAdditions:
				newHeader += newKeyValue
			newSkyrimIni = newSkyrimIni.replace(currentHeaderSearch, newHeader)
	
	for line in lines:
		print("INI <" + line + ">")
		if line.startswith("["):
			EndHeader()
			currentHeader = line
			pendingAdditions = []
		else:
			newLine = line + "\n"
			myKeySearch = re.search(iniPattern, line)
			if myKeySearch == None:
				print("INI line no key/pair found")
			else:
				myKey = myKeySearch.group(1)
				myValue = myKeySearch.group(2)
				print("MyKey <" + myKey + ">")
				print("MyValue <" + myValue + ">")
				localIniPattern = re.compile(r"^[; ]*" + myKey + r"=([^\n\r ]*)[ \n\r]", re.MULTILINE)
				existingKeyValue = re.search(localIniPattern, newSkyrimIni)
				if existingKeyValue != None:
					wholePattern = existingKeyValue.group(0)
					value = existingKeyValue.group(1)
					print("***" + wholePattern + "->" + newLine + "***")
					newSkyrimIni = newSkyrimIni.replace(wholePattern, newLine)
				else:
					pendingAdditions.append(newLine)
	EndHeader()
	
for plugin in loadOrderList:
	print("Adding " + plugin)
	pluginFolder = origin + "\\" + plugin
	for file in os.listdir(pluginFolder):
		print("   Found " + file)
		filename = pluginFolder + "\\" + file
		if file.endswith(".esm") or file.endswith(".esp"):
			InsertTestFile(file, filename)
		elif file.endswith(".bsa"):
			UnpackBSA(file, filename)
		elif file.endswith(".ini"):
			InsertIni(filename)

def WriteIniFile(file, buffer):
	newSkyrimIniFile = target + "\\" + file
	print("Write out new " + newSkyrimIniFile)
	with open(newSkyrimIniFile, "w+") as f:
		f.write(buffer)

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

def RemoveTree(tree):
	try:
		shutil.rmtree(temp_data)
	except FileNotFoundError:
		pass

MakeBSAOrder = ["", "Meshes", "Textures"]

print("Make BSAs: \n" + str(MakeBSAs))
for bsa_subname in MakeBSAOrder:
	if bsa_subname in MakeBSAs:
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
		bsa_filename = "Packed" + bsa_file_suffix + ".bsa"
		target_bsa = os.path.join(targetData, bsa_filename)
		
		archive_flags = GetArchiveFlags(folder_list, temp_data)
		
		flags_arg = "-sse -af:" + str(archive_flags)
		commandLine = '"' + bsarch + '" pack "' + temp_data + '" "' + target_bsa + '" ' + flags_arg
		print("Command Line:\n" + str(commandLine))
		p = subprocess.Popen(commandLine, shell=True)
		(output, err) = p.communicate()
		p_status = p.wait()
		checkCommandLine = '"' + bsarch + '" "' + target_bsa + '"'
		print("Command Line2:\n" + str(checkCommandLine))
		p = subprocess.Popen(checkCommandLine, shell=True)
		(output, err) = p.communicate()
		p_status = p.wait()
		
		#RemoveTree(temp_data)
		
		if bsa_subname == "Textures":
			InsertTextureBSA(bsa_filename)
		else:
			InsertMainBSA(bsa_filename)

newSkyrimIni = newSkyrimIni.replace(sResourceArchiveList, newResourceArchiveList)
newSkyrimIni = newSkyrimIni.replace(sResourceArchiveList2, newResourceArchiveList2)
WriteIniFile("Skyrim.ini", newSkyrimIni)

for languageIni in languageInis:
	liFilename = languageInis[languageIni]
	languageBuffer = open(liFilename, 'r').read()
	print("opening " + liFilename)
	
	liResourceArchiveList2 = GetArchiveList("sResourceArchiveList2", languageBuffer, re.MULTILINE)
	languageBuffer = languageBuffer.replace(liResourceArchiveList2, newResourceArchiveList2)
	WriteIniFile(languageIni, languageBuffer)
	
