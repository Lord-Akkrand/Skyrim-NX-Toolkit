#! python3

import os
import sys
import zipfile

def UnzipFile(origin, target):

	print("Zip file: " + origin)
	print("Target File: " + target)
	target_filename = os.path.basename(target)
	target_path = os.path.dirname(target)
	cwd = os.getcwd()
	os.chdir(target_path)
	print("Target Folder: " + target_path)
	print("Target Filename: " + target_filename)
	
	with zipfile.ZipFile(origin) as myzip:
		for filename in myzip.namelist():
			if filename.endswith(target_filename):
				final_path = myzip.extract(filename, target_path)
				if final_path != target:
					endPath = os.path.dirname(final_path)
					os.rename(final_path, target)
					os.rmdir(endPath)
	
	print("Unzip Complete")
	os.chdir(cwd)
	
if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	UnzipFile(origin, target)