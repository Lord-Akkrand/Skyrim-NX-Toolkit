#! python3

import sys
import re
import os.path
import shutil
import logging
import util
import unpack_mod
import pack_mod
import subprocess
import distutils.dir_util 

def LoadOrder(origin, target, loadOrderName):
	targetData = target + r"\Data"
	logging.debug("This is the origin: " + origin)
	logging.debug("This is the target: " + target)
	logging.debug("This is the target Data: " + targetData)
	logging.debug("This is the load order name: " + loadOrderName)

	logging.info("Packed Load Order " + loadOrderName)
	
	loadOrderTxt = os.path.join(origin, loadOrderName + ".txt")
	loadOrder = open(loadOrderTxt, 'r').read()
	#logging.debug("LOAD ORDER <" + loadOrder + ">")
	loadOrderList = loadOrder.splitlines()
	loadOrderStart = int(loadOrderList[0])
	loadOrderList = loadOrderList[1:]
	logging.debug("ESP Start at " + str(loadOrderStart))
	logging.debug("LOAD ORDER LIST <" + str(loadOrderList) + ">")

	pristineFolder = target
	pristineSkyrimIni = pristineFolder + r"\Skyrim.ini"
	logging.debug("Attempt to open " + pristineSkyrimIni)
	pristineSkyrim = open(pristineSkyrimIni, 'r').read()
	#logging.debug("PRISTINE:\n" + pristineSkyrim + "END PRISTINE")
	newSkyrimIni = pristineSkyrim

	languageInis = {}
	for file in os.listdir(pristineFolder):
		if file.endswith(".ini") and file != "Skyrim.ini" and file != "desktop.ini":
			logging.debug("Language ini <" + file + ">")
			languageInis[file] = pristineFolder + "\\" + file

	logging.debug("Language Inis:")
	for languageIni in languageInis:
		liFilename = languageInis[languageIni]
		logging.debug(languageIni+ " " +  liFilename)

	def GetArchiveList(aln, buffer, flags=None):
		logging.debug("Find existing " + aln)
		alPattern = "(" + aln + r"=[^\n$]*)[\n$]*"
		if flags != None:
			alPattern = re.compile(alPattern, flags)
		al = re.search(alPattern, buffer)
		if al == None:
			logging.error("Cannot find " + aln + ", bailing")
			logging.error("BUFFER" + buffer + "ENDBUFFER")
			sys.exit(1)
		retVal = al.group(1)
		logging.debug("<" + retVal + ">")
		return retVal
	sResourceArchiveList = GetArchiveList("sResourceArchiveList", newSkyrimIni)
	sResourceArchiveList2 = GetArchiveList("sResourceArchiveList2", newSkyrimIni)

	def GetTestFile(tfn):
		tfn = str(tfn)
		logging.debug("Find test file " + tfn)
		tfPattern = "([;]*sTestFile" + tfn + r"=[^\n]*)\n"
		tf = re.search(tfPattern, newSkyrimIni)
		if tf == None:
			logging.error("Cannot find " + tfn + ", bailing")
			sys.exit(1)
		retVal = tf.group(1)
		logging.debug("<" + retVal + ">")
		return retVal

	CurrentTestFileIDX = loadOrderStart
	sTestFiles = {}
	for i in range(CurrentTestFileIDX, 11):
		sTestFiles["sTestFile" + str(i)] = GetTestFile(i)

	def CopyFile(file, filename):
		newFileName = targetData + "\\" + file
		logging.debug(filename + "->" + newFileName)
		shutil.copy2(filename, newFileName)
		
	def InsertTestFile(name, filename):
		nonlocal CurrentTestFileIDX, newSkyrimIni
		currentTestFile = "sTestFile" + str(CurrentTestFileIDX)
		CurrentTestFileIDX = CurrentTestFileIDX + 1
		newTestFile = currentTestFile + "=" + name
		newSkyrimIni = newSkyrimIni.replace(sTestFiles[currentTestFile], newTestFile)
		logging.debug(newTestFile)
		CopyFile(file, filename)
	#logging.debug("TESTFILES<" + str(sTestFiles) + ">")

	newResourceArchiveList2 = sResourceArchiveList2
	def InsertTextureBSA(name, filename):
		nonlocal newResourceArchiveList2
		newResourceArchiveList2 += ", " + name
		logging.debug(newResourceArchiveList2)

	newResourceArchiveList = sResourceArchiveList
	def InsertMainBSA(name, filename):
		nonlocal newResourceArchiveList
		newResourceArchiveList += ", " + name
		logging.debug(newResourceArchiveList)
		
	if loadOrderStart <= 4:
		logging.debug("Hyrule.esp will not be loaded, so removing Skyrim - Hyrule.bsa from newResourceArchiveList")
		newResourceArchiveList = newResourceArchiveList.replace(", Skyrim - Hyrule.bsa", "")
		logging.debug("newResourceArchiveList is now:\n" + newResourceArchiveList)

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
				logging.debug("Search for <" + currentHeaderSearch + ">")
				newHeader = currentHeaderSearch
				for newKeyValue in pendingAdditions:
					newHeader += newKeyValue
				newSkyrimIni = newSkyrimIni.replace(currentHeaderSearch, newHeader)
		
		for line in lines:
			logging.debug("INI <" + line + ">")
			if line.startswith("["):
				EndHeader()
				currentHeader = line
				pendingAdditions = []
			else:
				newLine = line + "\n"
				myKeySearch = re.search(iniPattern, line)
				if myKeySearch == None:
					logging.debug("INI line no key/pair found")
				else:
					myKey = myKeySearch.group(1)
					myValue = myKeySearch.group(2)
					logging.debug("MyKey <" + myKey + ">")
					logging.debug("MyValue <" + myValue + ">")
					localIniPattern = re.compile(r"^[; ]*" + myKey + r"=([^\n\r ]*)[ \n\r]", re.MULTILINE)
					existingKeyValue = re.search(localIniPattern, newSkyrimIni)
					if existingKeyValue != None:
						wholePattern = existingKeyValue.group(0)
						value = existingKeyValue.group(1)
						logging.debug("***" + wholePattern + "->" + newLine + "***")
						newSkyrimIni = newSkyrimIni.replace(wholePattern, newLine)
					else:
						pendingAdditions.append(newLine)
		EndHeader()
		
	for plugin in loadOrderList:
		logging.debug("Found " + plugin)
		pluginFolder = os.path.join(origin, plugin)
		if plugin.startswith("#"):
			logging.debug("Passing on " + plugin)
		else:
			unpack_mod.UnpackMod(pluginFolder, target)
			for file in os.listdir(targetData):
				if file.endswith(".ini"):
					filename = os.path.join(targetData, file)
					os.remove(filename)
			for file in os.listdir(pluginFolder):
				logging.debug("   Found " + file)
				filename = os.path.join(pluginFolder, file)
				if file.endswith(".esm") or file.endswith(".esp"):
					InsertTestFile(file, filename)
				elif file.endswith(".ini"):
					InsertIni(filename)
				elif file.endswith(".bsa"):
					pass # we unpacked already
				else:
					if os.path.isdir(filename):
						shutil.copytree(filename, os.path.join(targetData, file))
					else:
						shutil.copy2(filename, os.path.join(targetData, file))
					
	bsaList = pack_mod.PackMod(loadOrderName, target)
	for filename in bsaList:
		file = os.path.basename(filename)
		if file.endswith("Textures.bsa"):
			InsertTextureBSA(file, filename)
		elif file.endswith(".bsa"):
			InsertMainBSA(file, filename)
	
	def WriteIniFile(file, buffer):
		newSkyrimIniFile = target + "\\" + file
		logging.info("Writing " + file)
		with open(newSkyrimIniFile, "w+") as f:
			f.write(buffer)

	newSkyrimIni = newSkyrimIni.replace(sResourceArchiveList, newResourceArchiveList)
	newSkyrimIni = newSkyrimIni.replace(sResourceArchiveList2, newResourceArchiveList2)
	WriteIniFile("Skyrim.ini", newSkyrimIni)

	for languageIni in languageInis:
		liFilename = languageInis[languageIni]
		languageBuffer = open(liFilename, 'r').read()
		logging.debug("opening " + liFilename)
		
		liResourceArchiveList2 = GetArchiveList("sResourceArchiveList2", languageBuffer, re.MULTILINE)
		languageBuffer = languageBuffer.replace(liResourceArchiveList2, newResourceArchiveList2)
		WriteIniFile(languageIni, languageBuffer)
	

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	loadOrderName = sys.argv[3]
	util.InitialiseLog(os.path.join(origin, loadOrderName) + ".log")
	LoadOrder(origin, target, loadOrderName)