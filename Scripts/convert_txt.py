#! python3

import util
import codecs

def ConvertTXT_Internal(filename):
	buffer = None
	with open(filename, "r", newline="\r") as pcFile:
		buffer = pcFile.read()
	
	buffer = buffer[2:]
	util.LogDebug("BUFFER<{}>".format(buffer))
	with open(filename, "wb") as outFile:
		outFile.write(b'\xff\xfe\x00\x00')
		outFile.write(buffer.encode('utf-16-le'))
	return True

def ConvertTXT(target, filename):
	return ConvertTXT_Internal(filename)
	
if __name__ == '__main__':
	filename = sys.argv[1]
	util.InitialiseLog(filename + ".log")
	util.StartTimer()
	ConvertTXT_Internal(filename)
	util.EndTimer()
	