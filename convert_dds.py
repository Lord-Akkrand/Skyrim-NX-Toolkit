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

import subprocess

texconv = sys.argv[1]
basePath = sys.argv[2]
ddsFileName = sys.argv[3]
ddsInfo = sys.argv[4]
texdiag = sys.argv[5]
has_sdk = sys.argv[6]
relativeFilename = ddsFileName.replace(basePath, '')

print("This is texconv: ", texconv)
print("This is the base path: ", basePath)
print("This is dds file: ", ddsFileName)
print("This is the relative dds file: ", relativeFilename)
print("This is ddsinfo text file: ", ddsInfo)
print("This is texdiag text file: ", texdiag)
print("HAS_SDK: ", has_sdk)
hasSDK = has_sdk == 'true'

relativePathList = relativeFilename[1:].split('\\')
print('PATH')
for path in relativePathList:
	print(path)
print('END PATH')
buffer = open(ddsInfo, 'r').read()
print('DDSINFO START')
print(buffer)
print('DDSINFO END')

tdBuffer = open(texdiag, 'r').read()
print('TEXDIAG START')
print(tdBuffer)
print('TEXDIAG END')

def getIntPattern(name):
	namePattern = name + r": ([\d]+)"
	nameReturn = re.search(namePattern, buffer)
	if nameReturn != None:
		nameReturn = nameReturn.group(1)
	else:
		nameReturn = -1
	print(name + " is :" + str(nameReturn))
	return int(nameReturn)

def lerp(x, a, b):
	return ((b - a) * x) + a
	
height = getIntPattern("Height")
width = getIntPattern("Width")
mipmaps = getIntPattern("Mipmap count")
linearSize = height * width

fourCCPattern = r"FourCC: '(....)'"
fourCC = re.search(fourCCPattern, buffer)
if fourCC != None:
	fourCC = fourCC.group(1)
else:
	fourCC = '----'
	diffPattern = r"format = \b(.*)\b"
	tdFormat = ''
	m = re.search(diffPattern, tdBuffer)
	if m != None:
		tdFormat = m.group(1)
		print("Format is <" + tdFormat + ">")
	for formatInfo in sizes.Formats:
		if formatInfo[1] == tdFormat:
			fourCC = formatInfo[0]

print("FourCC is " + str(fourCC))

maxSize = sizes.DefaultSizeLimit
forceFormat = None
shouldRun = False
print('File is ' + relativeFilename)
for rule in sizes.Rules:
	rulePath = rule['Path']
	pathStart = rulePath[0]
	match = False
	print('Checking rule: ' + str(rule))
	for iP in range(len(relativePathList)):
		path = relativePathList[iP]
		m = re.search(pathStart, path)
		if m != None:
			# we have the start of a match.  See if it bears out.
			print('on the trail of ' + pathStart)
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
					print('ongoing into ' + nextPath + ' == ' + pathOngoing)
					if match == True:
						break
				if match == False:
					break
		if match:
			print('APPLYING RULE [' + rule['Name'] + ']')
			if 'Size' in rule:
				maxSize = rule['Size']
			if 'Format' in rule:
				formatRule = rule['Format']
				if formatRule[0] != fourCC:
					forceFormat = formatRule[1]
					print('Forcing Format from ' + fourCC + ' to ' + forceFormat)
					
			break


convertTable = None
if hasSDK:
	convertTable = sizes.ConvertFromToSDK
else:
	convertTable = sizes.ConvertFromTo

print("Check force conversion for fourCC " + fourCC)
for conv in convertTable:
	print('Checking ' + conv[0])
	if fourCC == conv[0]:
		forceFormat = conv[1][1]
		print('Match.  Force convert to ' + forceFormat)
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
		print('Resizing ' + str(resizePercentage) + ' results in ' + str(newWidth) + 'x' + str(newHeight))
		
	commandLine = '"' + texconv + '"  -pow2 -fl 9.3 -y'
	
	if newWidth < width:
		commandLine += " -w " + str(newWidth)
	if newHeight < height:
		commandLine += " -h " + str(newHeight)
	if newMipmaps < mipmaps:
		commandLine += " -m " + str(newMipmaps)
	
	if forceFormat != None:
		commandLine += " -f " + forceFormat
	elif fourCC == "DX10" and not hasSDK:
		commandLine += " -f BC3_UNORM"
	commandLine += ' "' + ddsFileName + '"'
	print('Command Line <' + commandLine + '>')
	subprocess.call(commandLine, shell=True)
else:
	print("TexConv will not run")

