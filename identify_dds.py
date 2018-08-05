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

basePath = sys.argv[1]
ddsFileName = sys.argv[2]
ddsInfo = sys.argv[3]
outputFilename = sys.argv[4]
relativeFilename = ddsFileName.replace(basePath, '')
print("This is the base path: ", basePath)
print("This is dds file: ", ddsFileName)
print("This is the relative dds file: ", relativeFilename)
print("This is ddsinfo text file: ", ddsInfo)
print("This is the output file: ", outputFilename)

buffer = open(ddsInfo, 'r').read()
print('BUFFER START')
print(buffer)
print('BUFFER END')

def getIntPattern(name):
	header.append(name)
	namePattern = name + r": ([\d]+)"
	nameReturn = re.search(namePattern, buffer)
	if nameReturn != None:
		nameReturn = nameReturn.group(1)
	else:
		nameReturn = -1
	print(name + " is :" + str(nameReturn))
	return nameReturn

def getHexPattern(name, patternName):
	# Flags: 0x00000004
	header.append(name)
	namePattern = patternName + r":[ ]+(0[xX][0-9a-fA-F]+)"
	nameReturn = re.search(namePattern, buffer)
	if nameReturn != None:
		nameReturn = nameReturn.group(1)
	else:
		nameReturn = -1
	print(name + " is :" + str(nameReturn))
	return nameReturn
	
header = []
header.append("filename")

outputs = []
outputs.append(relativeFilename)
outputs.append(getIntPattern("Height"))
outputs.append(getIntPattern("Width"))
outputs.append(getIntPattern("Depth"))
outputs.append(getIntPattern("Mipmap count"))
outputs.append(getIntPattern("Linear size"))
outputs.append(getIntPattern("Bit count"))

# FourCC: 'DXT5'
header.append("FourCC")
fourCCPattern = r"FourCC: '(....)'"
fourCC = re.search(fourCCPattern, buffer)
if fourCC != None:
	fourCC = fourCC.group(1)
else:
	fourCC = "----"
print("FourCC is :" + str(fourCC))
outputs.append(fourCC)

outputs.append(getHexPattern("Flags", r"^Flags"))
outputs.append(getHexPattern("PF Flags", r"[ \t]+Flags"))

outputs.append(getHexPattern("Caps 1", r"[ \t]+Caps 1"))
outputs.append(getHexPattern("Caps 2", r"[ \t]+Caps 2"))
outputs.append(getHexPattern("Caps 3", r"[ \t]+Caps 3"))
outputs.append(getHexPattern("Caps 4", r"[ \t]+Caps 4"))

outputs.append(getHexPattern("Red mask", r"[ \t]+Red mask"))
outputs.append(getHexPattern("Green mask", r"[ \t]+Green mask"))
outputs.append(getHexPattern("Blue mask", r"[ \t]+Blue mask"))
outputs.append(getHexPattern("Alpha mask", r"[ \t]+Alpha mask"))

def hasFlag(flag):
	header.append(flag)
	flagReturn = re.search(flag, buffer)
	if flagReturn != None:
		#print(flag + " is set!")
		return True
	#print(flag + " is NOT set!")
	return False
	
outputs.append(hasFlag("DDSD_ALL"))
outputs.append(hasFlag("DDSD_ALPHABITDEPTH"))
outputs.append(hasFlag("DDSD_BACKBUFFERCOUNT"))
outputs.append(hasFlag("DDSD_CAPS"))
outputs.append(hasFlag("DDSD_CKDESTBLT"))
outputs.append(hasFlag("DDSD_CKDESTOVERLAY"))
outputs.append(hasFlag("DDSD_CKSRCBLT"))
outputs.append(hasFlag("DDSD_CKSRCOVERLAY"))
outputs.append(hasFlag("DDSD_HEIGHT"))
outputs.append(hasFlag("DDSD_LINEARSIZE"))
outputs.append(hasFlag("DDSD_MIPMAPCOUNT"))
outputs.append(hasFlag("DDSD_PITCH"))
outputs.append(hasFlag("DDSD_PIXELFORMAT"))
outputs.append(hasFlag("DDSD_REFRESHRATE"))
outputs.append(hasFlag("DDSD_WIDTH"))
outputs.append(hasFlag("DDSD_ZBUFFERBITDEPTH"))

outputs.append(hasFlag("DDPF_ALPHA"))
outputs.append(hasFlag("DDPF_ALPHAPIXELS"))
outputs.append(hasFlag("DDPF_ALPHAPREMULT"))
outputs.append(hasFlag("DDPF_BUMPLUMINANCE"))
outputs.append(hasFlag("DDPF_BUMPDUDV"))
outputs.append(hasFlag("DDPF_COMPRESSED"))
outputs.append(hasFlag("DDPF_D3DFORMAT"))
outputs.append(hasFlag("DDPF_FOURCC"))
outputs.append(hasFlag("DDPF_LUMINANCE"))
outputs.append(hasFlag("DDPF_PALETTEINDEXED1"))
outputs.append(hasFlag("DDPF_PALETTEINDEXED2"))
outputs.append(hasFlag("DDPF_PALETTEINDEXED4"))
outputs.append(hasFlag("DDPF_PALETTEINDEXED8"))
outputs.append(hasFlag("DDPF_PALETTEINDEXEDTO8"))
outputs.append(hasFlag("DDPF_RGB"))
outputs.append(hasFlag("DDPF_RGBTOYUV"))
outputs.append(hasFlag("DDPF_STENCILBUFFER"))
outputs.append(hasFlag("DDPF_YUV"))
outputs.append(hasFlag("DDPF_ZBUFFER"))
outputs.append(hasFlag("DDPF_ZPIXELS"))

outputs.append(hasFlag("DDSCAPS_3D"))
outputs.append(hasFlag("DDSCAPS_3DDEVICE"))
outputs.append(hasFlag("DDSCAPS_ALLOCONLOAD"))
outputs.append(hasFlag("DDSCAPS_ALPHA"))
outputs.append(hasFlag("DDSCAPS_BACKBUFFER"))
outputs.append(hasFlag("DDSCAPS_COMPLEX"))
outputs.append(hasFlag("DDSCAPS_FLIP"))
outputs.append(hasFlag("DDSCAPS_FRONTBUFFER"))
outputs.append(hasFlag("DDSCAPS_HWCODEC"))
outputs.append(hasFlag("DDSCAPS_LIVEVIDEO"))
outputs.append(hasFlag("DDSCAPS_LOCALVIDMEM"))
outputs.append(hasFlag("DDSCAPS_MIPMAP"))
outputs.append(hasFlag("DDSCAPS_MODEX"))
outputs.append(hasFlag("DDSCAPS_NONLOCALVIDMEM"))
outputs.append(hasFlag("DDSCAPS_OFFSCREENPLAIN"))
outputs.append(hasFlag("DDSCAPS_OPTIMIZED"))
outputs.append(hasFlag("DDSCAPS_OVERLAY"))
outputs.append(hasFlag("DDSCAPS_OWNDC"))
outputs.append(hasFlag("DDSCAPS_PALETTE"))
outputs.append(hasFlag("DDSCAPS_PRIMARYSURFACE"))
outputs.append(hasFlag("DDSCAPS_STANDARDVGAMODE"))
outputs.append(hasFlag("DDSCAPS_SYSTEMMEMORY"))
outputs.append(hasFlag("DDSCAPS_TEXTURE"))
outputs.append(hasFlag("DDSCAPS_VIDEOMEMORY"))
outputs.append(hasFlag("DDSCAPS_VIDEOPORT"))
outputs.append(hasFlag("DDSCAPS_VISIBLE"))
outputs.append(hasFlag("DDSCAPS_WRITEONLY"))
outputs.append(hasFlag("DDSCAPS_ZBUFFER"))

doHeader = True
if os.path.isfile(outputFilename):
	doHeader = False
	
with open(outputFilename, "a") as outputFile:
	outputLine = ""
	if doHeader:
		headerLine = ""
		for column in header:
			headerLine += str(column) + ", "
		headerLine += "\n"
		outputFile.write(headerLine)
	for output in outputs:
		outputLine += str(output) + ", "
	
	outputLine += "\n"
	print("Output line is START LINE <\n" + outputLine + "> END LINE")
	outputFile.write(outputLine)
