#! python3

import sys
import os.path
import shutil
import subprocess
import util

def ReconcileHKX(mod_path, oldrim_path):

	script_path = util.GetScriptPath()
	
	util.LogInfo("Reconcile HKX")
	util.LogDebug("This is the mod_path: " + mod_path)
	util.LogDebug("This is the oldrim_path " + oldrim_path)
	
	CopyHKX = []
	totalCount = 0
	matchedCount = 0
	for root, subdirs, files in os.walk(mod_path):
		util.LogDebug("Walking folder " + root)
		for filename in files:
			if filename.lower().endswith(".hkx"):
				file_path = os.path.join(root, filename)
				relative_path = os.path.relpath(file_path, mod_path)
				
				util.LogDebug("Relative path {} OR Path {}".format(relative_path, oldrim_path))
				oldrim_file_path = os.path.join(oldrim_path, relative_path)
				totalCount += 1
				util.LogDebug("Found {}, checking {}".format(file_path, oldrim_file_path))
				if os.path.exists(oldrim_file_path):
					util.LogDebug("Found {} match in oldrim".format(oldrim_file_path))
					matchedCount += 1
					CopyHKX.append( (file_path, oldrim_file_path) )
	util.LogInfo("Matched {}/{} hkx files in the mod".format(matchedCount, totalCount))
	
	for i in range(len(CopyHKX)):
		(copy_to, copy_from) = CopyHKX[i]
		util.LogDebug("Copying {}->{}".format(copy_from, copy_to))
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