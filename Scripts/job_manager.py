#! python3

import threading
import util

MaxThreads = 5


class Job():
	def __init__(self, cb, func, *args):
		self.m_Callback = cb
		self.m_Func = func
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
		retVal = self.m_Func(*self.m_Args)
		self.m_Callback and self.m_Callback(retVal)

class JobManager:
	def __init__(self, maxThreads=None):
		self.m_RunningJobs = []
		self.m_JobsBacklog = []
		if maxThreads != None:
			self.m_MaxThreads = maxThreads
		else:
			self.m_MaxThreads = MaxThreads
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
			