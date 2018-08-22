#! python3

import sys
import os.path
import shutil
import subprocess
import util
import logging

def ReconcileHKX(mod_path, oldrim_path):

	script_path = util.GetScriptPath()
	
	logging.info("Reconcile HKX")
	logging.debug("This is the mod_path: " + mod_path)
	logging.debug("This is the oldrim_path " + oldrim_path)
	
	CopyHKX = []
	totalCount = 0
	matchedCount = 0
	for root, subdirs, files in os.walk(mod_path):
		logging.debug("Walking folder " + root)
		for filename in files:
			if filename.lower().endswith(".hkx"):
				file_path = os.path.join(root, filename)
				relative_path = os.path.relpath(file_path, mod_path)
				
				logging.debug("Relative path {} OR Path {}".format(relative_path, oldrim_path))
				oldrim_file_path = os.path.join(oldrim_path, relative_path)
				totalCount += 1
				logging.debug("Found {}, checking {}".format(file_path, oldrim_file_path))
				if os.path.exists(oldrim_file_path):
					logging.debug("Found {} match in oldrim".format(oldrim_file_path))
					matchedCount += 1
					CopyHKX.append( (file_path, oldrim_file_path) )
	logging.info("Matched {}/{} hkx files in the mod".format(matchedCount, totalCount))
	
	for i in range(len(CopyHKX)):
		(copy_to, copy_from) = CopyHKX[i]
		logging.debug("Copying {}->{}".format(copy_from, copy_to))
		shutil.copy2(copy_from, copy_to)
		sys.stdout.write("Reconciled {}/{} \r".format(i+1, len(CopyHKX)))
		sys.stdout.flush()
	sys.stdout.write("\n")
	
if __name__ == '__main__':
	mod_path = sys.argv[1]
	oldrim_path = sys.argv[2]
	util.InitialiseLog(mod_path + ".log")
	util.StartTimer()
	ReconcileHKX(mod_path, oldrim_path)
	util.EndTimer()