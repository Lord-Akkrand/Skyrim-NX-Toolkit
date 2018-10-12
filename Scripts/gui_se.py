import util
import os
import gui_log
import logging
import toolkit_config

from tkinter import filedialog, messagebox, ttk
from tkinter import *

class SolutionExplorer:
	def __init__(self, root, path):
		self.root = root
		self.pane = PanedWindow(root, orient=VERTICAL, relief=RAISED)
		self.treeView = ttk.Treeview(self.pane)
	
		def SUBS(path, parent):    
			for p in os.listdir(path):
				abspath = os.path.join(path, p)
				parent_element = self.treeView.insert(parent, 'end', text=p, open=False)
				if os.path.isdir(abspath):
					SUBS(abspath, parent_element)
	
		self.treeView.heading("#0", text="Solution Explorer")
		
		self.treeView.pack(expand=YES, fill=BOTH)
		root = self.treeView.insert('', 'end', text=path, open=True)
		SUBS(path, root)

		self.treeView.bind("<3>", self.rightClickMenu)
		
		self.pane.pack()
	
	def getPane(self):
		return self.pane
		
	def rightClickMenu(self, event):
		def undo():
			logging.debug("SolutionExplorer:rightClickMenu()->Undo({})".format(rowID))
		def redo():
			logging.debug("SolutionExplorer:rightClickMenu()->Redo({})".format(rowID))
		# create a popup menu
		logging.debug("SolutionExplorer:rightClickMenu({}, {})".format(event.x, event.y))
		rowID = self.treeView.identify('item', event.x, event.y)
		if rowID:
			self.treeView.selection_set(rowID)
			self.treeView.focus_set()
			self.treeView.focus(rowID)
			ir = self.treeView.item(rowID)
			logging.debug("SolutionExplorer:rightClickMenu()->{} ({})".format(rowID, ir))

			menu = Menu(self.root, tearoff=0)
			menu.add_command(label="Undo", command=undo)
			menu.add_command(label="Redo", command=redo)
			menu.post(event.x_root, event.y_root)
		else:
			pass
		