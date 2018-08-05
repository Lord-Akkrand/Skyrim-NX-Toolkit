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

'''
import sys
import re
import os.path
import sizes

import subprocess

basePath = sys.argv[1]
ddsFileName = sys.argv[2]
ddsInfo = sys.argv[3]
relativeFilename = ddsFileName.replace(basePath, '')
print("This is the base path: ", basePath)
print("This is dds file: ", ddsFileName)
print("This is the relative dds file: ", relativeFilename)
print("This is ddsinfo text file: ", ddsInfo)

relativePathList = relativeFilename[1:].split('\\')
print('PATH')
for path in relativePathList:
	print(path)
print('END PATH')
buffer = open(ddsInfo, 'r').read()
print('BUFFER START')
print(buffer)
print('BUFFER END')

def getIntPattern(name):
	namePattern = name + r": ([\d]+)"
	nameReturn = re.search(namePattern, buffer)
	if nameReturn != None:
		nameReturn = nameReturn.group(1)
	else:
		nameReturn = -1
	print(name + " is :" + str(nameReturn))
	return int(nameReturn)

height = getIntPattern("Height")
width = getIntPattern("Width")
linearSize = getIntPattern("Linear size")

fourCCPattern = r"FourCC: '(....)'"
fourCC = re.search(fourCCPattern, buffer)
if fourCC != None:
	fourCC = fourCC.group(1)
else:
	fourCC = "----"

print("FourCC is " + str(fourCC))

maxSize = sizes.DefaultLimit
for sizeLimitPair in sizes.SizeLimits:
	sizeLimitPath = sizeLimitPair[0]
	pathStart = sizeLimitPath[0]
	match = False
	print('Checking SizeLimitPair: ' + str(sizeLimitPair))
	for iP in range(len(relativePathList)):
		path = relativePathList[iP]
		if path == pathStart:
			# we have the start of a match.  See if it bears out.
			print('on the trail of ' + pathStart)
			match = True
			for iL in range(1, len(sizeLimitPath)):
				pathOngoing = sizeLimitPath[iL]
				nextPath = relativePathList[iP + iL]
				match = nextPath == pathOngoing
				print('ongoing into ' + nextPath + ' == ' + pathOngoing)
		if match:
			maxSize = sizeLimitPair[1]
			print('all good, using new size limit: ' + str(maxSize))
			break
		

if linearSize > maxSize:
	resizeValue = maxSize / linearSize
	resizeValue = resizeValue * 100.0
	print('Going to resize this at ' + str(resizeValue) + '%')
	commandLine = 'mogrify "' + ddsFileName + '" -resize ' + str(resizeValue) + '% "' + ddsFileName + '"'
	# commandLine = 'magick convert "' + ddsFileName + '" -resize ' + str(resizeValue) + '% "' + ddsFileName + '"'
	
	print('Command Line <' + commandLine + '>')
	subprocess.call(commandLine, shell=True)
	'''
	commandLine = ['magick', 'convert', '"' + ddsFileName + '"', '-resize', str(resizeValue) + '%', '"' + ddsFileName + '"']
	print('Command Line <' + str(commandLine) + '>')
	subprocess.call(commandLine, shell=True)
	'''
else:
	print("No Resizing necessary")

