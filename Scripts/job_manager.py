#! python3

import threading
import util
import toolkit_config
import multiprocessing

import convert_dds, convert_hkx, convert_hkx64, convert_txt
import convert_sound_zappa as convert_sound

class Job():
	def __init__(self, cb, funcName, func, *args):
		self.m_Callback = cb
		self.m_Func = func
		self.m_FuncName = funcName
		self.m_Args = args
		
	def SetFunc(self, func, *args):
		self.m_Func = func
		self.m_Args = args
	
	def SetCallback(self, cb):
		self.m_Callback = cb
		
	def SetThread(self, t):
		self.m_Thread = t
		
	def IsFinished(self):
		isAlive = self.m_Thread and self.m_Thread.is_alive()
		return not isAlive
	
	def Run(self):
		retVal = True
		
		manager = multiprocessing.Manager()
		return_dict = manager.dict()

		validMultiprocessor = True
		
		useMultiprocessor = toolkit_config.get_bool_setting("Performance", "Multiprocessing")
		if useMultiprocessor:
			if self.m_FuncName == "ConvertDDS":
				basePath, fileName = (self.m_Args)
				newProcess = multiprocessing.Process(target=convert_dds.ConvertDDSAsync, args=(basePath, fileName, return_dict))
			elif self.m_FuncName == "ConvertHKX":
				basePath, fileName = (self.m_Args)
				newProcess = multiprocessing.Process(target=convert_hkx.ConvertHKXAsync, args=(basePath, fileName, return_dict))
			elif self.m_FuncName == "ConvertHKX64":
				basePath, fileName = (self.m_Args)
				newProcess = multiprocessing.Process(target=convert_hkx64.ConvertHKX64Async, args=(basePath, fileName, return_dict))
			elif self.m_FuncName == "ConvertTXT":
				basePath, fileName = (self.m_Args)
				newProcess = multiprocessing.Process(target=convert_txt.ConvertTXTAsync, args=(basePath, fileName, return_dict))
			elif self.m_FuncName == "ConvertSound":
				basePath, fileName = (self.m_Args)
				newProcess = multiprocessing.Process(target=convert_sound.ConvertSoundAsync, args=(basePath, fileName, return_dict))
			else:
				validMultiprocessor = False

			if validMultiprocessor:
				newProcess.start()
				newProcess.join()
				retVal = return_dict["retVal"]
		else:
			validMultiprocessor = False

		if not validMultiprocessor:
			retVal = self.m_Func(*self.m_Args)
		
		self.m_Callback and self.m_Callback(retVal)

class JobManager:
	def __init__(self, maxThreads=None):
		self.m_RunningJobs = []
		self.m_JobsBacklog = []
		if maxThreads != None:
			self.m_MaxThreads = maxThreads
		else:
			maxThreads = toolkit_config.get_int_setting("Performance", "MaxOtherThreads")
			if maxThreads == None:
				util.LogWarn("No default max threads parameter!")
				maxThreads = 1
			self.m_MaxThreads = maxThreads
		self.m_UpdateCount = 0
	def AddJob(self, newJob):
		self.m_JobsBacklog.append(newJob)
		
	def ProcessBatch(self):
		util.LogDebug("JM Process Batch {}".format(len(self.m_JobsBacklog)))
		while len(self.m_RunningJobs) > 0 or len(self.m_JobsBacklog) > 0:
			self.Update()
		util.LogDebug("JM Batch Processed")
			
	def Update(self):
		self.m_UpdateCount += 1
		#util.LogDebug("{} JM Update {}/{}".format(self.m_UpdateCount, len(self.m_RunningJobs), len(self.m_JobsBacklog)))
		for job in list(self.m_RunningJobs):
			if job.IsFinished():
				self.m_RunningJobs.remove(job)
				util.LogDebug("{} JM Removing Finished Job {}/{}".format(self.m_UpdateCount, len(self.m_RunningJobs), len(self.m_JobsBacklog)))
				
		while len(self.m_RunningJobs) < self.m_MaxThreads and len(self.m_JobsBacklog) > 0:
			job = self.m_JobsBacklog.pop(0)
			def JobWorker():
				job.Run()
			newThread = threading.Thread(target=JobWorker)
			job.SetThread(newThread)
			newThread.start()
			self.m_RunningJobs.append(job)
			util.LogDebug("{} JM Started Job From Backlog {}/{}".format(self.m_UpdateCount, len(self.m_RunningJobs), len(self.m_JobsBacklog)))
			