#! python3

import sys
import urllib.request
import shutil
import zipfile

def DownloadFile(origin, target):

	print("Downloading from : " + origin)
	print("Downloading to: " + target)
	
	# Download the file from `url` and save it locally under `file_name`:
	with urllib.request.urlopen(origin) as response, open(target, 'wb') as out_file:
		shutil.copyfileobj(response, out_file)
		
	print("Download Complete")
	
if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	DownloadFile(origin, target)