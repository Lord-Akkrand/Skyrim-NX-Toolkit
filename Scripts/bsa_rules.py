#! python3

# 2GB Limit for BSA Files (I know 2GB is actually 2048 MB, not 2000, but Bethesdas BSAs limit seemed to be 2000MB)
BSASizeLimit = 1024 * 1024 * 2000

import toolkit_config

FullRules = []

# In order to be placed in a BSA you must meet all the criteria.  First rule evaluated wins.
FullRules.append({"BSA":"Animations", "Folder":"meshes", "Extension":"hkx"})
FullRules.append({"BSA":"Animations", "Folder":"meshes", "Extension":"txt"})

FullRules.append({"BSA":"Meshes", "Folder":"meshes"})
FullRules.append({"BSA":"Meshes", "Folder":"lodsettings"})

FullRules.append({"BSA":"Misc", "Folder":"grass"})
FullRules.append({"BSA":"Misc", "Folder":"scripts"})
FullRules.append({"BSA":"Misc", "Folder":"seq"})
FullRules.append({"BSA":"Shaders", "Folder":"shadersfx"})

FullRules.append({"BSA":"Voices", "Folder":"sound\\voice"})

FullRules.append({"BSA":"Sounds", "Folder":"music"})
FullRules.append({"BSA":"Sounds", "Folder":"sound\\fx"})
FullRules.append({"BSA":"Sounds", "Folder":"sound\\ebt"})

FullRules.append({"BSA":"Interface", "Folder":"strings"})
FullRules.append({"BSA":"Interface", "Folder":"interface"})

FullRules.append({"BSA":"Textures", "Folder":"textures"})

BasicRules = []
# Basic Rules, only make Textures/Meshes/Animations/''
# "BSA":"" will just be PluginName.bsa

BasicRules.append({"BSA":"Textures", "Folder":"textures"})

BasicRules.append({"BSA":"Animations", "Folder":"meshes", "Extension":"hkx"})
BasicRules.append({"BSA":"Animations", "Folder":"meshes", "Extension":"txt"})

BasicRules.append({"BSA":"Meshes", "Folder":"meshes"})
BasicRules.append({"BSA":"Meshes", "Folder":"lodsettings"})

BasicRules.append({"BSA":"", "Folder":"grass"})
BasicRules.append({"BSA":"", "Folder":"scripts"})
BasicRules.append({"BSA":"", "Folder":"seq"})
BasicRules.append({"BSA":"", "Folder":"shadersfx"})
BasicRules.append({"BSA":"", "Folder":"strings"})
BasicRules.append({"BSA":"", "Folder":"interface"})
BasicRules.append({"BSA":"", "Folder":"video"})

BasicRules.append({"BSA":"Voices", "Folder":"sound\\voice"})
BasicRules.append({"BSA":"", "Folder":"music"})
BasicRules.append({"BSA":"", "Folder":"sound\\fx"})
BasicRules.append({"BSA":"", "Folder":"sound\\ebt"})

CompactRules = []
# Compact Rules, only make Textures/Meshes/MasterBSA
# "BSA":"" will just be PluginName.bsa

CompactRules.append({"BSA":"Textures", "Folder":"textures"})

CompactRules.append({"BSA":"", "Folder":"meshes"})
CompactRules.append({"BSA":"", "Folder":"lodsettings"})
CompactRules.append({"BSA":"", "Folder":"grass"})
CompactRules.append({"BSA":"", "Folder":"scripts"})
CompactRules.append({"BSA":"", "Folder":"seq"})
CompactRules.append({"BSA":"", "Folder":"shadersfx"})
CompactRules.append({"BSA":"", "Folder":"strings"})
CompactRules.append({"BSA":"", "Folder":"interface"})
CompactRules.append({"BSA":"", "Folder":"video"})
CompactRules.append({"BSA":"", "Folder":"sound"})
CompactRules.append({"BSA":"", "Folder":"music"})

def GetBSARules():
	rules = toolkit_config.get_setting("BSA", "Rules").lower()
	if rules == 'full':
		return FullRules
	elif rules == 'basic':
		return BasicRules
	else:
		return CompactRules