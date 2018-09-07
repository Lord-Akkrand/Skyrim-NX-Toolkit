#! python3

import sys
import re
import os.path
import shutil
import util

import subprocess

def LoadOrder(origin, target, loadOrderName):
	targetData = target + r"\Data"
	util.LogDebug("This is the origin: " + origin)
	util.LogDebug("This is the target: " + target)
	util.LogDebug("This is the target Data: " + targetData)
	util.LogDebug("This is the load order name: " + loadOrderName)

	util.LogInfo("Load Order " + loadOrderName)
	
	loadOrderTxt = os.path.join(origin, loadOrderName + ".txt")
	loadOrder = open(loadOrderTxt, 'r').read()
	#util.LogDebug("LOAD ORDER <" + loadOrder + ">")
	loadOrderList = loadOrder.splitlines()
	loadOrderStart = int(loadOrderList[0])
	loadOrderList = loadOrderList[1:]
	util.LogDebug("ESP Start at " + str(loadOrderStart))
	util.LogDebug("LOAD ORDER LIST <" + str(loadOrderList) + ">")

	pristineFolder = target
	pristineSkyrimIni = pristineFolder + r"\Skyrim.ini"
	util.LogDebug("Attempt to open " + pristineSkyrimIni)
	pristineSkyrim = open(pristineSkyrimIni, 'r').read()
	#util.LogDebug("PRISTINE:\n" + pristineSkyrim + "END PRISTINE")
	newSkyrimIni = pristineSkyrim

	languageInis = {}
	for file in os.listdir(pristineFolder):
		if file.endswith(".ini") and file != "Skyrim.ini" and file != "desktop.ini":
			util.LogDebug("Language ini <" + file + ">")
			languageInis[file] = pristineFolder + "\\" + file

	util.LogDebug("Language Inis:")
	for languageIni in languageInis:
		liFilename = languageInis[languageIni]
		util.LogDebug(languageIni+ " " +  liFilename)

	def GetArchiveList(aln, buffer, flags=None):
		util.LogDebug("Find existing " + aln)
		alPattern = "(" + aln + r"=[^\n$]*)[\n$]*"
		if flags != None:
			alPattern = re.compile(alPattern, flags)
		al = re.search(alPattern, buffer)
		if al == None:
			util.LogError("Cannot find " + aln + ", bailing")
			util.LogError("BUFFER" + buffer + "ENDBUFFER")
			sys.exit(1)
		retVal = al.group(1)
		util.LogDebug("<" + retVal + ">")
		return retVal
	sResourceArchiveList = GetArchiveList("sResourceArchiveList", newSkyrimIni)
	sResourceArchiveList2 = GetArchiveList("sResourceArchiveList2", newSkyrimIni)

	def GetTestFile(tfn):
		tfn = str(tfn)
		util.LogDebug("Find test file " + tfn)
		tfPattern = "([;]*sTestFile" + tfn + r"=[^\n]*)\n"
		tf = re.search(tfPattern, newSkyrimIni)
		if tf == None:
			util.LogError("Cannot find " + tfn + ", bailing")
			sys.exit(1)
		retVal = tf.group(1)
		util.LogDebug("<" + retVal + ">")
		return retVal

	CurrentTestFileIDX = loadOrderStart
	sTestFiles = {}
	for i in range(CurrentTestFileIDX, 11):
		sTestFiles["sTestFile" + str(i)] = GetTestFile(i)

	def CopyFile(file, filename):
		newFileName = targetData + "\\" + file
		util.LogDebug(filename + "->" + newFileName)
		shutil.copy2(filename, newFileName)
		
	def InsertTestFile(name, filename):
		nonlocal CurrentTestFileIDX, newSkyrimIni
		currentTestFile = "sTestFile" + str(CurrentTestFileIDX)
		CurrentTestFileIDX = CurrentTestFileIDX + 1
		newTestFile = currentTestFile + "=" + name
		newSkyrimIni = newSkyrimIni.replace(sTestFiles[currentTestFile], newTestFile)
		util.LogDebug(newTestFile)
		CopyFile(file, filename)
	#util.LogDebug("TESTFILES<" + str(sTestFiles) + ">")

	newResourceArchiveList2 = sResourceArchiveList2
	def InsertTextureBSA(name, filename):
		nonlocal newResourceArchiveList2
		newResourceArchiveList2 += ", " + name
		util.LogDebug(newResourceArchiveList2)
		CopyFile(file, filename)

	newResourceArchiveList = sResourceArchiveList
	def InsertMainBSA(name, filename):
		nonlocal newResourceArchiveList
		newResourceArchiveList += ", " + name
		util.LogDebug(newResourceArchiveList)
		CopyFile(file, filename)
		
	if loadOrderStart <= 4:
		util.LogDebug("Hyrule.esp will not be loaded, so removing Skyrim - Hyrule.bsa from newResourceArchiveList")
		newResourceArchiveList = newResourceArchiveList.replace(", Skyrim - Hyrule.bsa", "")
		util.LogDebug("newResourceArchiveList is now:\n" + newResourceArchiveList)

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
				util.LogDebug("Search for <" + currentHeaderSearch + ">")
				newHeader = currentHeaderSearch
				for newKeyValue in pendingAdditions:
					newHeader += newKeyValue
				newSkyrimIni = newSkyrimIni.replace(currentHeaderSearch, newHeader)
		
		for line in lines:
			util.LogDebug("INI <" + line + ">")
			if line.startswith("["):
				EndHeader()
				currentHeader = line
				pendingAdditions = []
			else:
				newLine = line + "\n"
				myKeySearch = re.search(iniPattern, line)
				if myKeySearch == None:
					util.LogDebug("INI line no key/pair found")
				else:
					myKey = myKeySearch.group(1)
					myValue = myKeySearch.group(2)
					util.LogDebug("MyKey <" + myKey + ">")
					util.LogDebug("MyValue <" + myValue + ">")
					localIniPattern = re.compile(r"^[; ]*" + myKey + r"=([^\n\r ]*)[ \n\r]", re.MULTILINE)
					existingKeyValue = re.search(localIniPattern, newSkyrimIni)
					if existingKeyValue != None:
						wholePattern = existingKeyValue.group(0)
						value = existingKeyValue.group(1)
						util.LogDebug("***" + wholePattern + "->" + newLine + "***")
						newSkyrimIni = newSkyrimIni.replace(wholePattern, newLine)
					else:
						pendingAdditions.append(newLine)
		EndHeader()
		
	for plugin in loadOrderList:
		util.LogDebug("Found " + plugin)
		pluginFolder = origin + "\\" + plugin
		if plugin.startswith("#"):
			util.LogDebug("Passing on " + plugin)
		else:
			util.LogInfo("Adding " + plugin)
			for file in os.listdir(pluginFolder):
				util.LogDebug("   Found " + file)
				filename = pluginFolder + "\\" + file
				if file.endswith(".esm") or file.endswith(".esp"):
					InsertTestFile(file, filename)
				elif file.endswith("Textures.bsa"):
					InsertTextureBSA(file, filename)
				elif file.endswith(".bsa"):
					InsertMainBSA(file, filename)
				elif file.endswith(".ini"):
					InsertIni(filename)
				else:
					if os.path.isdir(filename):
						shutil.copytree(filename, os.path.join(targetData, file))
					else:
						shutil.copy2(filename, os.path.join(targetData, file))

	def WriteIniFile(file, buffer):
		newSkyrimIniFile = target + "\\" + file
		util.LogInfo("Writing " + file)
		with open(newSkyrimIniFile, "w+") as f:
			f.write(buffer)

	newSkyrimIni = newSkyrimIni.replace(sResourceArchiveList, newResourceArchiveList)
	newSkyrimIni = newSkyrimIni.replace(sResourceArchiveList2, newResourceArchiveList2)
	WriteIniFile("Skyrim.ini", newSkyrimIni)

	for languageIni in languageInis:
		liFilename = languageInis[languageIni]
		languageBuffer = open(liFilename, 'r').read()
		util.LogDebug("opening " + liFilename)
		
		liResourceArchiveList2 = GetArchiveList("sResourceArchiveList2", languageBuffer, re.MULTILINE)
		languageBuffer = languageBuffer.replace(liResourceArchiveList2, newResourceArchiveList2)
		WriteIniFile(languageIni, languageBuffer)


if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	loadOrderName = sys.argv[3]
	util.InitialiseLog(os.path.join(origin, loadOrderName) + ".log")
	util.StartTimer()
	LoadOrder(origin, target, loadOrderName)
	util.EndTimer()