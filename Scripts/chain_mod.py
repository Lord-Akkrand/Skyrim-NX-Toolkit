#! python3

import sys
import re
import os.path
import shutil
import util

def ChainMod(data_folder, load_order_filename):
    print(data_folder)
    print(load_order_filename)

def ChainMod_External(data_folder, load_order_filename):
	util.InitialiseLog(os.path.join(data_folder, "chain_mod.log"))
	util.StartTimer()
	util.LogInfo("Skyrim-NX-Toolkit {} - chain_mod".format(util.GetToolkitVersion()))
	ChainMod(data_folder, load_order_filename)
	util.EndTimer()

if __name__ == '__main__':
	data_folder = sys.argv[1]
	load_order_filename = sys.argv[2]
	ChainMod(data_folder, load_order_filename)