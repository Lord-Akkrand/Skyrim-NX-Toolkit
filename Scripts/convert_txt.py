#! python3

import util
import codecs

def ConvertTXT_Internal(filename):
	buffer = None
	with open(filename, "rb") as pcFile:
		buffer = pcFile.read()
	
	
	buffer = bytearray(buffer)
	util.LogInfo("Buffer0<{}>".format(buffer[0]))
	util.LogInfo("Buffer0<{}>".format(buffer[1]))
	i = 1
	while i < len(buffer):
		buffer[i:i] = b'\x00\x00\x00'
		i += 4
		
	util.LogDebug("BUFFER<{}>".format(buffer))
	with open(filename, "wb") as outFile:
		
		outFile.write(b'\xff\xfe\x00\x00')
		outFile.write(buffer)
	return True

def ConvertTXT(target, filename):
	return ConvertTXT_Internal(filename)
	
if __name__ == '__main__':
	filename = sys.argv[1]
	util.InitialiseLog(filename + ".log")
	util.StartTimer()
	ConvertTXT_Internal(filename)
	util.EndTimer()
	