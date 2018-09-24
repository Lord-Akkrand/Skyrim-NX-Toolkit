import util
import os
import gui_log
import logging
import toolkit_config

from tkinter import filedialog, messagebox
from tkinter import *

def MainLoop():
	toolkit_path = util.GetToolKitPath()
	logo_filename = os.path.join(toolkit_path, "Skyrim-NX-Toolkit.25.png")
	icon_filename = os.path.join(toolkit_path, "Skyrim-NX-Toolkit.Icon.png")
	
	root = Tk()
	xResolution = 1280
	yResolution = 640
	root.geometry('{}x{}'.format(xResolution, yResolution))
	root.title("Skyrim-NX-Toolkit {}".format(util.GetToolkitVersion()))
	root.tk.call('wm', 'iconphoto', root._w, PhotoImage(file=icon_filename))
	
	def NewFile():
		print("New File!")
	def OpenFile():
		name = filedialog.askopenfilename()
		print(name)
	def About():
		messagebox.showinfo('About', 'Skyrim NX Toolkit {}'.format(util.GetToolkitVersion()))
	def QuitToolkit():
		if messagebox.askyesno('Are You Sure?', 'Really quit?'):
			root.quit()
	
	menu = Menu(root)
	root.config(menu=menu)
	filemenu = Menu(menu, tearoff=0)
	menu.add_cascade(label="File", menu=filemenu)
	filemenu.add_command(label="New", command=NewFile)
	filemenu.add_command(label="Open...", command=OpenFile)
	filemenu.add_separator()
	filemenu.add_command(label="Exit", command=QuitToolkit)

	helpmenu = Menu(menu, tearoff=0)
	menu.add_cascade(label="Help", menu=helpmenu)
	helpmenu.add_command(label="About...", command=About)
	

	main_window = PanedWindow(orient=HORIZONTAL, relief=RAISED)
	

	convert_pane = PanedWindow(main_window, orient=VERTICAL, relief=RAISED)
	convert_pane.add(Label(convert_pane, text="Convert 1"))
	convert_pane.add(Label(convert_pane, text="Convert 2"))
	convert_pane.add(Label(convert_pane, text="Convert 3"))
	convert_pane.pack()
	
	
	main_window.add(convert_pane)

	log_pane = PanedWindow(main_window, orient=VERTICAL, relief=RAISED)
	log_pane.add(Label(log_pane, text="Log Window"))
	
	log_window = gui_log.myGUI(log_pane)
	log_pane.add(log_window)
	log_pane.pack()
	
	main_window.add(log_pane)

	mod_pane = PanedWindow(main_window, orient=VERTICAL, relief=RAISED)
	mod_pane.add(Label(mod_pane, text="Mod 1"))
	mod_pane.add(Label(mod_pane, text="Mod 2"))
	mod_pane.add(Label(mod_pane, text="Mod 3"))
	mod_pane.pack()
	
	main_window.add(mod_pane)
	
	main_window.pack(fill=BOTH, expand=1)
	main_window.update()
	
	weights = [1, 3, 1]
		
	total_weight = sum(weights)
	current_tally = 0
	for i in range(len(weights)-1):
		weight = weights[i]
		current_tally += weight
		main_window.sash_place(i, int((current_tally / total_weight) * xResolution), 0)
	
	root.mainloop()

import time, threading
def testLogDaemonFn():
	# Skeleton worker function, runs in separate thread (see below)   
	while True:
		# Report time / date at 2-second intervals
		time.sleep(2)
		timeStr = time.asctime()
		msg = 'Current time: ' + timeStr
		logging.info(msg) 

def main():
	#test_config = toolkit_config.get_config()
	
	util.InitialiseGUILog()
	
	testLogDaemon = threading.Thread(target=testLogDaemonFn, args=[])
	testLogDaemon.daemon = True
	testLogDaemon.start()
	
	MainLoop()
	
	sys.exit(0)
		
if __name__ == '__main__':
	main()
	
	