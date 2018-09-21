import util
import os
import configparser

def create_config(path):
	"""
	Create a config file
	"""
	config = configparser.ConfigParser()
	toolkit_path = util.GetToolKitPath()
	original_mods_path = os.path.join(toolkit_path, "OriginalMods")
	converted_mods_path = os.path.join(toolkit_path, "ConvertedMods")
	config['Paths'] = { 
		"OriginalModsDirectory": original_mods_path,
		"ConvertedModsDirectory": converted_mods_path
	}
	
	config['Performance'] = {
		"MaxTextureThreads" : 5,
		"MaxAnimationThreads" : 5,
		"MaxSoundThreads" : 5,
		"MaxOtherThreads" : 5
	}
 
	write_config(config)

def get_config():
	"""
	Create, read, update, delete config
	"""
	toolkit_path = util.GetToolKitPath()
	path = os.path.join(toolkit_path, "settings.ini")
	if not os.path.exists(path):
		create_config(path)
 
	config = configparser.ConfigParser()
	config.read(path)
 
	return config
	
def get_setting(section, setting):
	"""
	Print out a setting
	"""
	config = get_config()
	value = config.get(section, setting)
	util.LogDebug("{section} {setting} is {value}".format(
		section=section, setting=setting, value=value))
	return value

def get_int_setting(section, setting):
	value = get_setting(section, setting)
	return int(value)
 
def update_setting(section, setting, value):
	"""
	Update a setting
	"""
	config = get_config()
	config.set(section, setting, value)
	write_config(config)
 
def delete_setting(section, setting):
	"""
	Delete a setting
	"""
	config = get_config()
	config.remove_option(section, setting)
	write_config(config)
	
def write_config(config):
	toolkit_path = util.GetToolKitPath()
	path = os.path.join(toolkit_path, "settings.ini")
	with open(path, "w") as config_file:
		config.write(config_file)