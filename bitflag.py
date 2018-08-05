#! /usr/bin/env python
# -*- coding: utf-8 -*-

class BitFlag(object):
	def __init__(self, *args):
		if len(args)==0: 
			self.value = 0
		else:
			self.value = 0
			for val in args:
				SetFlag(self, val)
		
	def IsSet(self, flag):
		return (self.value & flag) != 0
	def SetFlag(self, flag):
		self.value = self.value | flag
		return self.value
	def UnsetFlag(self, flag):
		self.value = flags & ~flag
		return self.value
	def GetValue(self):
		return self.value