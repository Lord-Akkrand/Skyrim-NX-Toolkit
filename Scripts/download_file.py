#! python3
'''
import sys
import requests
import shutil
import zipfile
'''

def DownloadFile(origin, target):
	'''
	print("Downloading from : " + origin)
	print("Downloading to: " + target)

	# Download the file from `url` and save it locally under `file_name`:
	with open(target, 'wb') as out_file:
		response = requests.get(origin)
		out_file.write(response.content)

	print("Download Complete")
	'''
	print("Deprecated.  Use the powershell downloader.")

if __name__ == '__main__':
	origin = sys.argv[1]
	target = sys.argv[2]
	DownloadFile(origin, target)