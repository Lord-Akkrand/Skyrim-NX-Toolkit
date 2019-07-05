#! python3

import sys
import multiprocessing
import gui
import util, download_file, unzip_file
import convert_mod, convert_path, load_order, pack_mod, packed_load_order, repack_mod, unpack_mod
	
if __name__ == '__main__':
	multiprocessing.freeze_support()

	py_script = sys.argv[1]
	print("Skyrim-NX-Toolkit {}, sys.argv <{}>".format(util.GetToolkitVersion(), str(sys.argv)))
	if py_script == 'gui':
		gui.main()
	elif py_script == 'download_file':
		url = sys.argv[2]
		file_path = sys.argv[3]
		download_file.DownloadFile(url, file_path)
	elif py_script == 'unzip_file':
		zip_file = sys.argv[2]
		file_path = sys.argv[3]
		unzip_file.UnzipFile(zip_file, file_path)
	elif py_script == 'convert_mod':
		origin = sys.argv[2]
		target = sys.argv[3]
		oldrim = None
		if len(sys.argv) > 3:
			oldrim = sys.argv[4]
		convert_mod.ConvertMod_External(origin, target, oldrim)
	elif py_script == 'convert_path':
		mod_name = sys.argv[2]
		target = sys.argv[3]
		convert_path.ConvertPath_External(mod_name, target)
	elif py_script == 'load_order':
		origin = sys.argv[2]
		target = sys.argv[3]
		loadOrderName = sys.argv[4]
		load_order.LoadOrder_External(origin, target, loadOrderName)
	elif py_script == 'packed_load_order':
		origin = sys.argv[2]
		target = sys.argv[3]
		loadOrderName = sys.argv[4]
		packed_load_order.PackedLoadOrder_External(origin, target, loadOrderName)
	elif py_script == 'pack_mod':
		mod_name = sys.argv[2]
		target = sys.argv[3]
		pack_mod.PackMod_External(mod_name, target)
	elif py_script == 'repack_mod':
		origin = sys.argv[2]
		target = sys.argv[3]
		repack_mod.RepackMod_External(origin, target)
	elif py_script == 'unpack_mod':
		origin = sys.argv[2]
		target = sys.argv[3]
		unpack_mod.UnpackMod_External(origin, target)
	

		
