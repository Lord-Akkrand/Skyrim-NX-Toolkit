#! python3
'''

Example input file (alduin.dds)

Flags: 0x000A1007
	DDSD_CAPS
	DDSD_PIXELFORMAT
	DDSD_WIDTH
	DDSD_HEIGHT
	DDSD_LINEARSIZE
	DDSD_MIPMAPCOUNT
Height: 1024
Width: 1024
Depth: 0
Linear size: 1048576
Mipmap count: 10
Pixel Format:
	Flags: 0x00000004
		DDPF_FOURCC
	FourCC: 'DXT5' (0x35545844)
	Bit count: 0
	Red mask:   0x00000000
	Green mask: 0x00000000
	Blue mask:  0x00000000
	Alpha mask: 0x00000000
Caps:
	Caps 1: 0x00401008
		DDSCAPS_COMPLEX
		DDSCAPS_TEXTURE
		DDSCAPS_MIPMAP
	Caps 2: 0x00000000
	Caps 3: 0x00000000
	Caps 4: 0x00000000

Example RGBA from texdiag:
        width = 1024
       height = 1024
        depth = 1
    mipLevels = 10
    arraySize = 1
       format = R8G8B8A8_UNORM
    dimension = 2D
   alpha mode = Unknown
       images = 10
   pixel size = 5461 (KB)
'''
import sys
import re
import os.path
import sizes
import util
import logging

import subprocess

def ConvertDDS(basePath, ddsFileName):
	relativeFilename = ddsFileName.replace(basePath, '')

	hasSDK = util.HasSDK()
	
	logging.debug("This is the base path: " + " " +  basePath)
	logging.debug("This is dds file: " + " " +  ddsFileName)
	logging.debug("HAS_SDK: " +  str(hasSDK))
		
	logging.debug("convert_dds.py 2.0")

	relativePathList = relativeFilename[1:].split('\\')
	logging.debug('PATH')
	for path in relativePathList:
		logging.debug(path)
	logging.debug('END PATH')
	
	utilities_path = util.GetUtilitiesPath()
	nvddsinfo = os.path.join(utilities_path, "nvddsinfo.exe")
	logging.debug(nvddsinfo + " " +  ddsFileName)
	dds_buffer, dds_err = util.RunCommandLine([nvddsinfo, ddsFileName])
	
	logging.debug('DDSINFO START')
	logging.debug(dds_buffer)
	logging.debug('DDSINFO END')

	texdiag = os.path.join(utilities_path, "texdiag.exe")
	logging.debug(texdiag + " " + ddsFileName)
	td_buffer, td_err = util.RunCommandLine([texdiag, "info", ddsFileName])
	logging.debug('TEXDIAG START')
	logging.debug(td_buffer)
	logging.debug('TEXDIAG END')

	def getIntPattern(name):
		namePattern = name + r": ([\d]+)"
		nameReturn = re.search(namePattern, dds_buffer)
		if nameReturn != None:
			nameReturn = nameReturn.group(1)
		else:
			nameReturn = -1
		logging.debug(name + " is :" + str(nameReturn))
		return int(nameReturn)

	def lerp(x, a, b):
		return ((b - a) * x) + a
		
	height = getIntPattern("Height")
	width = getIntPattern("Width")
	mipmaps = getIntPattern("Mipmap count")
	linearSize = height * width

	fourCCPattern = r"FourCC: '(....)'"
	fourCC = re.search(fourCCPattern, dds_buffer)
	if fourCC != None:
		fourCC = fourCC.group(1)
	else:
		fourCC = '----'
		diffPattern = r"format = \b(.*)\b"
		tdFormat = ''
		m = re.search(diffPattern, td_buffer)
		if m != None:
			tdFormat = m.group(1)
			logging.debug("Format is <" + tdFormat + ">")
		for formatInfo in sizes.Formats:
			if formatInfo[1] == tdFormat:
				fourCC = formatInfo[0]

	logging.debug("FourCC is " + str(fourCC))

	maxSize = sizes.DefaultSizeLimit
	forceFormat = None
	shouldRun = False
	logging.debug('File is ' + relativeFilename)
	for rule in sizes.Rules:
		rulePath = rule['Path']
		pathStart = rulePath[0]
		match = False
		logging.debug('Checking rule: ' + str(rule))
		for iP in range(len(relativePathList)):
			path = relativePathList[iP]
			m = re.search(pathStart, path)
			if m != None:
				# we have the start of a match.  See if it bears out.
				logging.debug('on the trail of ' + pathStart)
				match = True
				for iL in range(1, len(rulePath)):
					pathOngoing = rulePath[iL]
					internalIdx = 0
					while True:
						nextIdx = iP + iL + internalIdx
						if nextIdx < len(relativePathList):
							nextPath = relativePathList[nextIdx]
						else:
							match = False
							break
						internalIdx += 1
						m = re.search(pathOngoing, nextPath)
						match = m != None
						logging.debug('ongoing into ' + nextPath + ' == ' + pathOngoing)
						if match == True:
							break
					if match == False:
						break
			if match:
				logging.debug('APPLYING RULE [' + rule['Name'] + ']')
				if 'Size' in rule:
					maxSize = rule['Size']
				if 'Format' in rule:
					formatRule = rule['Format']
					if formatRule[0] != fourCC:
						forceFormat = formatRule[1]
						logging.debug('Forcing Format from ' + fourCC + ' to ' + forceFormat)
						
				break


	convertTable = None
	if hasSDK:
		convertTable = sizes.ConvertFromToSDK
	else:
		convertTable = sizes.ConvertFromTo

	logging.debug("Check force conversion for fourCC " + fourCC)
	for conv in convertTable:
		logging.debug('Checking ' + conv[0])
		if fourCC == conv[0]:
			forceFormat = conv[1][1]
			logging.debug('Match.  Force convert to ' + forceFormat)
			break

	shouldRun = shouldRun or linearSize > maxSize
	shouldRun = shouldRun or (forceFormat != None)
	if shouldRun:
		resizePercentage = 1
		newLinearSize = linearSize
		newWidth = width
		newHeight = height
		newMipmaps = mipmaps
		while newLinearSize > maxSize:
			resizePercentage *= 0.5
			newWidth = int(width * resizePercentage)
			newHeight = int(height * resizePercentage)
			newLinearSize = newWidth * newHeight
			newMipmaps -= 1
			logging.debug('Resizing ' + str(resizePercentage) + ' results in ' + str(newWidth) + 'x' + str(newHeight))
		texconv = os.path.join(utilities_path, "texconv.exe")
		commandLine = [texconv, "-pow2", "-fl", "9.3", "-y"]
		if newWidth < width:
			commandLine += ["-w", str(newWidth)]
		if newHeight < height:
			commandLine += ["-h", str(newHeight)]
		if newMipmaps < mipmaps:
			commandLine += ["-m", str(newMipmaps)]
		
		if forceFormat != None:
			commandLine += ["-f", forceFormat]
		elif fourCC == "DX10" and not hasSDK:
			commandLine += ["-f", BC3_UNORM]
		
		commandLine += [ddsFileName]
		output, err = util.RunCommandLine(commandLine)
	else:
		logging.debug("TexConv will not run")


if __name__ == '__main__':
	basePath = sys.argv[1]
	ddsFileName = sys.argv[2]
	ConvertDDS(basePath, ddsFileName)