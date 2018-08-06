#! python3

import sys
import re
import os.path
import shutil

import subprocess

def LoadOrder(origin, target, loadOrderName):
	targetData = target + r"\Data"
	print("This is the origin: ", origin)
	print("This is the target: ", target)
	print("This is the target Data: ", targetData)
	print("This is the load order name: ", loadOrderName)

	print("Create empty target Data")
	os.mkdir(targetData)
	if not os.access(targetData, os.F_OK):
		print("Error creating targetData")
		sys.exit(1)

	loadOrderTxt = os.path.join(origin, loadOrderName + ".txt")
	loadOrder = open(loadOrderTxt, 'r').read()
	#print("LOAD ORDER <" + loadOrder + ">")
	loadOrderList = loadOrder.splitlines()
	loadOrderStart = int(loadOrderList[0])
	loadOrderList = loadOrderList[1:]
	print("ESP Start at " + str(loadOrderStart))
	print("LOAD ORDER LIST <" + str(loadOrderList) + ">")

	pristineFolder = target
	pristineSkyrimIni = pristineFolder + r"\Skyrim.ini"
	print("Attempt to open " + pristineSkyrimIni)
	pristineSkyrim = open(pristineSkyrimIni, 'r').read()
	#print("PRISTINE:\n" + pristineSkyrim + "END PRISTINE")
	newSkyrimIni = pristineSkyrim

	languageInis = {}
	for file in os.listdir(pristineFolder):
		if file.endswith(".ini") and file != "Skyrim.ini" and file != "desktop.ini":
			print("Language ini <" + file + ">")
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

	if loadOrderStart <= 4:
		print("Hyrule.esp will not be loaded, so removing Skyrim - Hyrule.bsa from sResourceArchiveList")
		sResourceArchiveList.replace(", Skyrim - Hyrule.bsa", "")
		print ("sResourceArchiveList is now:\n" + sResourceArchiveList)

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
		nonlocal CurrentTestFileIDX, newSkyrimIni
		currentTestFile = "sTestFile" + str(CurrentTestFileIDX)
		CurrentTestFileIDX = CurrentTestFileIDX + 1
		newTestFile = currentTestFile + "=" + name
		newSkyrimIni = newSkyrimIni.replace(sTestFiles[currentTestFile], newTestFile)
		print(newTestFile)
		CopyFile(file, filename)
	#print("TESTFILES<" + str(sTestFiles) + ">")

	newResourceArchiveList2 = sResourceArchiveList2
	def InsertTextureBSA(name, filename):
		nonlocal newResourceArchiveList2
		newResourceArchiveList2 += ", " + name
		print(newResourceArchiveList2)
		CopyFile(file, filename)

	newResourceArchiveList = sResourceArchiveList
	def InsertMainBSA(name, filename):
		nonlocal newResourceArchiveList
		newResourceArchiveList += ", " + name
		print(newResourceArchiveList)
		CopyFile(file, filename)

	iniPattern = r"^[; ]*([^=]*)=([^$]*)$"
	def InsertIni(filename):
		nonlocal newSkyrimIni
		buffer = open(filename, 'r').read()
		lines = buffer.splitlines()
		pendingAdditions = []
		currentHeader = ''
		def EndHeader():
			nonlocal newSkyrimIni
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
		print("Found " + plugin)
		pluginFolder = origin + "\\" + plugin
		if plugin.startswith("#"):
			print("Passing on " + plugin)
		else:
			print("Adding " + plugin)
			for file in os.listdir(pluginFolder):
				print("   Found " + file)
				filename = pluginFolder + "\\" + file
				if file.endswith(".esm") or file.endswith(".esp"):
					InsertTestFile(file, filename)
				elif file.endswith("Textures.bsa"):
					InsertTextureBSA(file, filename)
				elif file.endswith(".bsa"):
					InsertMainBSA(file, filename)
				elif file.endswith(".ini"):
					InsertIni(filename)

	def WriteIniFile(file, buffer):
		newSkyrimIniFile = target + "\\" + file
		print("Write out new " + newSkyrimIniFile)
		with open(newSkyrimIniFile, "w+") as f:
			f.write(buffer)

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


if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	loadOrderName = sys.argv[3]
	LoadOrder(origin, target, loadOrderName)