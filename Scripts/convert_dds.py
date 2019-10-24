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
import math
import sizes
import util
import shutil
import toolkit_config
import xtx_extract

import subprocess


def ConvertDDS(basePath, ddsFileName, opt_InRecursion=1):
    relativeFilename = ddsFileName.replace(basePath, '')
    ddsFilePath = os.path.dirname(ddsFileName)
    hasSDK = util.HasSDK()

    util.LogDebug("This is the base path: " + " " + basePath)
    util.LogDebug("This is dds file: " + " " + ddsFileName)
    util.LogDebug("HAS_SDK: " + str(hasSDK))

    util.LogDebug("convert_dds.py 2.0")

    relativePathList = relativeFilename[1:].split('\\')
    util.LogDebug('PATH')
    for path in relativePathList:
        util.LogDebug(path)
    util.LogDebug('END PATH')

    utilities_path = util.GetUtilitiesPath()
    nvddsinfo = os.path.join(utilities_path, "nvddsinfo.exe")
    util.LogDebug(nvddsinfo + " " + ddsFileName)
    dds_buffer, dds_err = util.RunCommandLine([nvddsinfo, ddsFileName])

    util.LogDebug('DDSINFO START')
    util.LogDebug(dds_buffer)
    util.LogDebug('DDSINFO END')

    def getIntPattern(name):
        namePattern = name + r": ([\d]+)"
        nameReturn = re.search(namePattern, dds_buffer)
        if nameReturn != None:
            nameReturn = nameReturn.group(1)
        else:
            nameReturn = -1
        util.LogDebug(name + " is :" + str(nameReturn))
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

    if fourCC == 'DXT1':
        util.LogDebug("Running nvcompress on DXT1 texture")
        nvcompress = os.path.join(utilities_path, "nvcompress.exe")
        (nvc_buffer, nvc_err) = util.RunCommandLine(
            [nvcompress, "-bc1", ddsFileName, ddsFileName])
		
    if fourCC == 'DXT5':
        util.LogDebug("Running nvcompress on DXT5 texture")
        nvcompress = os.path.join(utilities_path, "nvcompress.exe")
        (nvc_buffer, nvc_err) = util.RunCommandLine(
            [nvcompress, "-bc3", ddsFileName, ddsFileName])
    texdiag = os.path.join(utilities_path, "texdiag.exe")
    util.LogDebug(texdiag + " " + ddsFileName)
    td_buffer, td_err = util.RunCommandLine([texdiag, "info", ddsFileName])
    m = re.search(r"FAILED", td_buffer)
    if m != None:
        util.LogError("texconv FAILED")
        return False

    if fourCC == '----' or fourCC == 'DX10':
        diffPattern = r"format = \b(.*)\b"
        tdFormat = ''
        m = re.search(diffPattern, td_buffer)
        if m != None:
            tdFormat = m.group(1)
            util.LogDebug("Format is <" + tdFormat + ">")
        for formatInfo in sizes.Formats:
            if formatInfo[1] == tdFormat:
                fourCC = formatInfo[0]

    util.LogDebug("FourCC is " + str(fourCC))

    maxSize = toolkit_config.get_int_setting("Textures", "DefaultSizeLimit")
    forceFormat = None
    shouldRun = False
    util.LogDebug('File is ' + relativeFilename)
    size_rules = toolkit_config.get_setting("Textures", "SizeRules")
    ruleSet = None
    if size_rules in sizes.Rules:
        ruleSet = sizes.Rules[size_rules]
    else:
        ruleSet = sizes.Rules['Base']

    for rule in ruleSet:
        rulePath = rule['Path']
        pathStart = rulePath[0]
        match = False
        util.LogDebug('Checking rule: ' + str(rule))
        for iP in range(len(relativePathList)):
            path = relativePathList[iP]
            m = re.search(pathStart, path, re.IGNORECASE)
            if m != None:
                # we have the start of a match.  See if it bears out.
                util.LogDebug('on the trail of ' + pathStart)
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
                        m = re.search(pathOngoing, nextPath, re.IGNORECASE)
                        match = m != None
                        util.LogDebug('ongoing into ' +
                                      nextPath + ' == ' + pathOngoing)
                        if match == True:
                            break
                    if match == False:
                        break
            if match:
                util.LogDebug('APPLYING RULE [' + rule['Name'] + ']')
                if 'Size' in rule:
                    maxSize = rule['Size']
                if 'Format' in rule:
                    formatRule = rule['Format']
                    if formatRule[0] != fourCC:
                        forceFormat = formatRule[1]
                        util.LogDebug('Forcing Format from ' +
                                      fourCC + ' to ' + forceFormat)

                break

    convertTable = None
    if hasSDK:
        convertTable = sizes.ConvertFromToSDK
    else:
        convertTable = sizes.ConvertFromTo

    util.LogDebug("Check force conversion for fourCC " + fourCC)
    for conv in convertTable:
        util.LogDebug('Checking ' + conv[0])
        if fourCC == conv[0]:
            forceFormat = conv[1][1]
            util.LogDebug('Match.  Force convert to ' + forceFormat)
            break

    if forceFormat != None:
        if opt_InRecursion > 5:
            util.LogError("Infinite Recursion???")
            return False
        texconv = os.path.join(utilities_path, "texconv.exe")
        commandLine = [texconv, "-y", "-f", conv[1][1]]
        commandLine += [ddsFileName]
        commandLine += ["-o", ddsFilePath]
        (output, err) = util.RunCommandLine(commandLine)
        util.LogDebug(
            "Done a pre-resize conversion, coming back in here for pass " + str(opt_InRecursion + 1))
        # return True
        return ConvertDDS(basePath, ddsFileName, opt_InRecursion + 1)

    shouldRun = shouldRun or linearSize > maxSize
    if shouldRun:
        resizePercentage = 1
        newLinearSize = linearSize
        newWidth = width
        newHeight = height
        rebuildMipmaps = mipmaps > 1
        while newLinearSize > maxSize:
            resizePercentage *= 0.5
            newWidth = int(width * resizePercentage)
            newHeight = int(height * resizePercentage)
            newLinearSize = newWidth * newHeight
            util.LogDebug('Resizing ' + str(resizePercentage) +
                          ' results in ' + str(newWidth) + 'x' + str(newHeight))
        texconv = os.path.join(utilities_path, "texconv.exe")
        commandLine = [texconv, "-nologo", "-sepalpha", "-pow2"]
        if newWidth < width:
            commandLine += ["-w", str(newWidth)]
        if newHeight < height:
            commandLine += ["-h", str(newHeight)]
        finalCommandLine = commandLine[:]

        commandLine += ["-m", "1", "-y"]
        commandLine += [ddsFileName]
        commandLine += ["-o", ddsFilePath]

        (output, err) = util.RunCommandLine(commandLine)
        if rebuildMipmaps:
            finalCommandLine += ["-m", "0", "-y"]
            finalCommandLine += [ddsFileName]
            finalCommandLine += ["-o", ddsFilePath]
            (output, err) = util.RunCommandLine(finalCommandLine)
    else:
        util.LogDebug("TexConv will not run")

    doNXConversion = True
    if not doNXConversion:
        util.LogDebug("Debug passing on NX texture conversion")
        return True

    util.LogDebug("Now for NX texture conversion")
    if hasSDK:
        nvntexpkg = util.GetNvnTexpkg()
        out_filename = ddsFileName + "out.xtx"
        out_file = os.path.join(ddsFilePath, out_filename)
        commandLine = [nvntexpkg, "-i", ddsFileName,
                       "-v", "--printinfo", "-o", out_file]
        (convOutput, convErrors) = util.RunCommandLine(commandLine)

        # if "Everything went OK" in convOutput:
        if os.path.exists(out_file):
            util.ForceMove(out_file, ddsFileName)
            util.LogDebug("SDK conversion success for {}".format(ddsFileName))
            return True
    else:
        out_filename = ddsFileName + "out.xtx"
        out_file = os.path.join(ddsFilePath, out_filename)
        try:
            xtx_extract.main_external(["-o", out_file, ddsFileName])
            #commandLine = ["py", "-3", xtx_extract, ddsFileName]
            # util.RunCommandLine(commandLine)

            #out_file = os.path.join(ddsFilePath, ddsFileName[:-4] + ".xtx")
            if os.path.exists(out_file):
                util.ForceMove(out_file, ddsFileName)
                util.LogDebug(
                    "XTX conversion success for {}".format(ddsFileName))
                return True
        except:
            pass
    util.LogError("Error During Conversion of {}".format(ddsFileName))
    return False


def ConvertDDSAsync(basePath, ddsFileName, logname, ret):
    util.InitialiseMPLog(logname)
    retVal = ConvertDDS(basePath, ddsFileName)
    util.LogDebug("retVal for {} was <{}>".format(ddsFileName, str(retVal)))
    ret["retVal"] = retVal


if __name__ == '__main__':
    basePath = sys.argv[1]
    ddsFileName = sys.argv[2]
    ConvertDDS(basePath, ddsFileName)
