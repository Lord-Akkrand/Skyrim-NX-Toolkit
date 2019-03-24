#! python3

import sys
import os.path
import shutil
import subprocess
import util
import job_manager
import toolkit_config
import check_dds, convert_dds
import check_hkx, convert_hkx, convert_hkx64
import convert_txt
import convert_sound_zappa as convert_sound


import bitflag

def ConvertPath(mod_name, target):

	script_path = util.GetScriptPath()
	
	util.LogInfo("Convert Path")
	util.LogDebug("This is the target: " + target)
	util.LogDebug("This is the mod name " + mod_name)
	
	has_havoc = util.HasHavokBPP()
	
	NoConversion = {}
	WarnConversion = {}
	ConvertListDDS = []
	ConvertListHKX = []
	ConvertListHKX64 = []
	ConvertListTXT = []
	ConvertListSound = []
	for root, subdirs, files in os.walk(target):
		if root != target:
			util.LogDebug("Walking folder " + root)
			for filename in files:
				#util.LogDebug("filename: {}".format(filename))
				if filename.lower().endswith(".dds"):
					file_path = os.path.join(root, filename)
					ddsChecked = check_dds.CheckDDS(file_path, file_path)
					if ddsChecked == check_dds.PC:
						ConvertListDDS.append(file_path)
					elif ddsChecked == check_dds.NX:
						if 'DDS' not in NoConversion:
							NoConversion['DDS'] = 0
						NoConversion['DDS'] += 1
					else:
						if 'DDS' not in WarnConversion:
							WarnConversion['DDS'] = []
						WarnConversion['DDS'].append( (filename, "Unknown DDS format") )
				elif filename.lower().endswith(".hkx"):
					file_path = os.path.join(root, filename)
					hkxChecked = check_hkx.CheckHKX(file_path, file_path)
					if hkxChecked == check_hkx.PC_32:
						ConvertListHKX.append(file_path)
					elif hkxChecked == check_hkx.PC_XML:
						ConvertListHKX.append(file_path)
					elif hkxChecked == check_hkx.PC_64:
						if root.lower().find("behaviors") > 0 or filename.lower().find("skeleton") > 0:
							if 'HKX' not in WarnConversion:
								WarnConversion['HKX'] = []
							WarnConversion['HKX'].append( (filename, "SSE hkx animation") )
						else:
							ConvertListHKX64.append(file_path)
					elif hkxChecked == check_hkx.NX_64:
						if 'HKX' not in NoConversion:
							NoConversion['HKX'] = 0
						NoConversion['HKX'] += 1
					else:
						if 'HKX' not in WarnConversion:
							WarnConversion['HKX'] = []
						WarnConversion['HKX'].append( (filename, "Unknown hkx animation format") )
						
				elif filename.lower().startswith("translate_") and filename.lower().endswith(".txt"):
					file_path = os.path.join(root, filename)
					ConvertListTXT.append(file_path)
				elif filename.lower().endswith(".xwm") or filename.lower().endswith(".fuz") or filename.lower().endswith(".wav"):
					file_path = os.path.join(root, filename[:-4])
					if not file_path in ConvertListSound:
						ConvertListSound.append(file_path)

	for fileType in NoConversion:
		util.LogInfo("Found {} {} files that are already in NX format".format(NoConversion[fileType], fileType))
	for fileType in WarnConversion:
		fileTypeWarnings = WarnConversion[fileType]
		for i in range(len(fileTypeWarnings)):
			util.LogInfo("Warning, cannot convert {} because <{}>".format(fileTypeWarnings[i][0], fileTypeWarnings[i][1]))
			
	util.LogInfo("Found {} dds files to convert".format(len(ConvertListDDS)))
	if has_havoc: 
		util.LogInfo("Found {} 32-bit hkx files to convert".format(len(ConvertListHKX)))
	else:
		util.LogInfo("Found {} 32-bit hkx files that won't convert as Havoc utility wasn't found.".format(len(ConvertListHKX)))
	util.LogInfo("Found {} 64-bit hkx files to convert".format(len(ConvertListHKX64)))	
	util.LogInfo("Found {} txt files to convert".format(len(ConvertListTXT)))
	util.LogInfo("Found {} sound files to convert".format(len(ConvertListSound)))
	
	
	
	'''
	def LogProgress(convertList, convertFn, name):
		if len(convertList) > 0:
			failedCount = 0
			for i in range(len(convertList)):
				file_path = convertList[i]
				success = convertFn(target, file_path)
				if not success:
					failedCount += 1
				sys.stdout.write("Converted {}/{} {} ({}) failed. \r".format(i+1, len(convertList), name, failedCount))
				sys.stdout.flush()
			sys.stdout.write("\n")
	'''
	
	def LogProgress(convertList, convertFn, name, threadSetting):
		if len(convertList) > 0:
			failedCount = 0
			maxThreads = toolkit_config.get_int_setting("Performance", threadSetting)
			
			jm = job_manager.JobManager(maxThreads)
			convertedCount = 0
			processedCount = 0
			totalCount = len(convertList)
			def cb(success):
				nonlocal processedCount, convertedCount, failedCount
				processedCount += 1
				if success:
					convertedCount += 1
				else:
					failedCount += 1
				sys.stdout.write("{} Processed {}/{} ({}/{}) success/failure. \r".format(name, processedCount, totalCount, convertedCount, failedCount))
				sys.stdout.flush()
				
			for i in range(len(convertList)):
				file_path = convertList[i]
				job = job_manager.Job(cb, convertFn, target.lower(), file_path.lower())
				jm.AddJob(job)
			jm.ProcessBatch()
			
			sys.stdout.write("\n")
			
	LogProgress(ConvertListDDS, convert_dds.ConvertDDS, "DDS", "MaxTextureThreads")
	if has_havoc:
		LogProgress(ConvertListHKX, convert_hkx.ConvertHKX, "HKX 32-bit", "MaxAnimationThreads")
	LogProgress(ConvertListHKX64, convert_hkx64.ConvertHKX64, "HKX 64-bit", "MaxAnimationThreads")
	LogProgress(ConvertListTXT, convert_txt.ConvertTXT, "TXT", "MaxOtherThreads")
	LogProgress(ConvertListSound, convert_sound.ConvertSound, "Sounds", "MaxSoundThreads")

def ConvertPath_External(mod_name, target):
	util.InitialiseLog(target + ".log")
	util.StartTimer()
	util.LogInfo("Skyrim-NX-Toolkit {} - convert_path".format(util.GetToolkitVersion()))
	ConvertPath(mod_name, target)
	util.EndTimer()
	
if __name__ == '__main__':
	mod_name = sys.argv[1]
	target = sys.argv[2]
	util.InitialiseLog(target + ".log")
	util.StartTimer()
	ConvertPath(mod_name, target)
	util.EndTimer()
