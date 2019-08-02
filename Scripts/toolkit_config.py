import util
import os
import configparser

toolkit_path = util.GetToolKitPath()
original_mods_path = os.path.join(toolkit_path, "OriginalMods")
converted_mods_path = os.path.join(toolkit_path, "ConvertedMods")

DefaultValues = {
	"Paths":{
		"OriginalModsDirectory": original_mods_path,
		"ConvertedModsDirectory": converted_mods_path
	},
	"Performance":{
		"MaxTextureThreads" : 5,
		"MaxAnimationThreads" : 5,
		"MaxSoundThreads" : 5,
		"MaxOtherThreads" : 5,
		"MaxMeshThreads" : 5,
		"Multiprocessing" : False
	},
	"BSA":{
		"FullRules" : False
	},
	"Textures":{
		"DefaultSizeLimit" : 1024*1024,
	"SizeRules" : "Base"
	},
	"Meshes":{
		"RemoveEditorMarker" : True,
		"PrettySortBlocks": False,
		"TrimTexturesPath": False,
		"OptimizeForSSE": False
	},
	"Sounds":{
		"fx": "MCADPCM",
		"music": "MCADPCM",
		"voice": "NXOPUS"
	},
	"Version":{
		"ToolkitVersion" : util.GetToolkitVersion(),
	}
}

def create_config(path):
	"""
	Create a config file
	"""
	config = configparser.ConfigParser()

	for name, section in DefaultValues.items():
		config[name] = section

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

def check_clear():
	config = get_config()
	util.LogInfo("Checking if settings.ini should be updated.")
	clearOldConfig = False
	currentVersion = util.GetToolkitVersion()
	try:
		settingsVersion = config.get("Version", "ToolkitVersion")
		util.LogInfo("Version:ToolkitVersion is {}.  Currrent Version is {}".format(settingsVersion, currentVersion))
		if settingsVersion != currentVersion:
			util.LogInfo("Not a match.  Clearing settings.ini")
			clearOldConfig = True
	except:
		util.LogInfo("Version:ToolkitVersion was not found.  Clearing settings.ini")
		clearOldConfig = True
	if clearOldConfig:
		util.LogInfo("Clearing settings.ini")

		toolkit_path = util.GetToolKitPath()
		path = os.path.join(toolkit_path, "settings.ini")
		create_config(path)
		config.read(path)

def get_setting(section, setting):
	"""
	Print out a setting
	"""
	config = get_config()
	try:
		value = config.get(section, setting)
	except:
		value = DefaultValues[section][setting]
		util.LogInfo("Added default setting {}/{} as {}".format(section, setting, value))
		update_setting(section, setting, str(value))

	return value

def get_int_setting(section, setting):
	value = get_setting(section, setting)
	return int(value)

def get_bool_setting(section, setting):
	value = get_setting(section, setting)
	return (value == "True")

def update_setting(section, setting, value):
	"""
	Update a setting
	"""
	config = get_config()
	if not config.has_section(section):
		config.add_section(section)

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