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
	SSE_MODS = ['Skyrim.esm', 'Update.esm', 'Dawnguard.esm', 'HearthFires.esm', 'Dragonborn.esm', 'Unofficial Skyrim Special Edition Patch.esp']
	mods_master_payload = {}
	master_payload = b''
	for mod in mods_list:
		payload = master_payload + \
			b'MAST' + (len(mod) + 1).to_bytes(0x02, byteorder = 'little') + mod.encode('latin-1') + b'\x00' + \
			b'DATA' + b'\x08\x00' + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00'
		if not mod in SSE_MODS:
			mods_master_payload[mod] = master_payload
		master_payload = payload
	return mods_master_payload

def chain_mods(data_folder, mods_master_payload):
	util.LogInfo("found {} mods to chain".format(len(mods_master_payload)))
	for mod in mods_master_payload:
		mod_filename = os.path.join(data_folder, mod)
		if not os.path.exists(mod_filename):
			util.LogInfo("skipping '{}' as file not found".format(mod_filename))
		else:
			chain_single_mod(mod_filename, mods_master_payload[mod])

def chain_single_mod(mod_filename_input, master_payload):

	SIGNATURE_SIZE = 0x04
	LENGTH_SIZE = 0x02
	HEADER_SIZE = 0x18
	mod_filename_output = mod_filename_input + '.new'
	shutil.copy(mod_filename_input, mod_filename_output)
	with open(mod_filename_input, 'rb') as mod_file_input, open(mod_filename_output, 'wb') as mod_file_output:
		mod_data = bytearray(mod_file_input.read())
		if mod_data[0:4] != b'TES4':
			util.LogInfo("skipping '{}' as invalid header signature".format(mod_filename_input))
		else:
			util.LogInfo("chaining '{}'".format(mod_filename_input))
			index = HEADER_SIZE
			injected = False
			payload = b''
			sub_header_size = int.from_bytes(mod_data[SIGNATURE_SIZE:SIGNATURE_SIZE + LENGTH_SIZE], byteorder = 'little', signed = False)
			total_header_size = HEADER_SIZE + sub_header_size
			block_type = mod_data[index:index+4]
			block_size = int.from_bytes(mod_data[index + SIGNATURE_SIZE:index + SIGNATURE_SIZE + LENGTH_SIZE], byteorder = 'little', signed = False)
			while index < total_header_size:
				if block_type not in [b'MAST', b'DATA']:
					payload = payload + mod_data[index:index + SIGNATURE_SIZE + block_size]
				elif not injected:
					injected = True
					payload = payload + master_payload
				index = index + block_size + SIGNATURE_SIZE + LENGTH_SIZE
				block_type = mod_data[index:index+4]
				block_size = int.from_bytes(mod_data[index+4:index+6], byteorder = 'little', signed = False)
			payload_len = len(payload)
			header = mod_data[0:HEADER_SIZE]
			header[SIGNATURE_SIZE:SIGNATURE_SIZE + LENGTH_SIZE] = int.to_bytes(payload_len, LENGTH_SIZE, byteorder = 'little', signed = False)
			mod_file_output.write(header)
			mod_file_output.write(payload)
			mod_file_output.write(mod_data[total_header_size:])

def ChainMod(data_folder, load_order_filename):
	mods_list = get_mods(load_order_filename)
	mods_master_payload = get_mods_master_payload(mods_list)
	chain_mods(data_folder, mods_master_payload)

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