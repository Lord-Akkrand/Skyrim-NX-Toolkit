#! python3

import sys
import re
import os.path
import shutil
import util

def get_mods(load_order_filename):
	mods_list = []
	with open(load_order_filename, 'r') as load_order_file:
		lines = load_order_file.readlines()
	for line in lines:
		if line[0] in ['#', '*', '\n']:
			continue
		mods_list.append(line.strip("\n"))
	return mods_list

def get_mods_master_payload(mods_list):
	mods_master_payload = {}
	master_payload = b''
	for mod in mods_list:
		_len = len(mod) + 1
		master_payload = master_payload + \
			b'MAST' + \
			_len.to_bytes(0x02, byteorder = 'little') + \
			mod.encode('latin-1') + \
			b'\x00' + \
			b'DATA' + \
			b'\x08\x00' + \
		    b'\x00\x00\x00\x00' + \
			b'\x00\x00\x00\x00'
		mods_master_payload[mod] = master_payload
	return mods_master_payload

def ChainMod(data_folder, load_order_filename):
	print(data_folder)
	mods_list = get_mods(load_order_filename)
	print(mods_list)
	mods_master_payload = get_mods_master_payload(mods_list)
	print(mods_master_payload)

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