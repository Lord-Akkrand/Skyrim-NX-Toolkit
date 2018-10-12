#! python3

# 2GB Limit for BSA Files (I know 2GB is actually 2048 MB, not 2000, but Bethesdas BSAs limit seemed to be 2000MB)
BSASizeLimit = 1024 * 1024 * 2000

BSARules = []

FullRules = False

if FullRules:
	# In order to be placed in a BSA you must meet all the criteria.  First rule evaluated wins.
	BSARules.append({"BSA":"Animations", "Folder":"meshes", "Extension":"hkx"})
	BSARules.append({"BSA":"Animations", "Folder":"meshes", "Extension":"txt"})

	BSARules.append({"BSA":"Meshes", "Folder":"meshes"})
	BSARules.append({"BSA":"Meshes", "Folder":"lodsettings"})

	BSARules.append({"BSA":"Misc", "Folder":"grass"})
	BSARules.append({"BSA":"Misc", "Folder":"scripts"})
	BSARules.append({"BSA":"Misc", "Folder":"seq"})
	BSARules.append({"BSA":"Shaders", "Folder":"shadersfx"})

	BSARules.append({"BSA":"Sounds", "Folder":"music"})
	BSARules.append({"BSA":"Sounds", "Folder":"sound\\fx"})

	BSARules.append({"BSA":"Interface", "Folder":"strings"})
	BSARules.append({"BSA":"Interface", "Folder":"interface"})
	
	BSARules.append({"BSA":"Textures", "Folder":"textures"})

	BSARules.append({"BSA":"Voices", "Folder":"sound\\voice"})
	
else:

	# Basic Rules, only make Textures/Meshes/Animations/''
	# "BSA":"" will just be PluginName.bsa

	BSARules.append({"BSA":"Textures", "Folder":"textures"})
	
	BSARules.append({"BSA":"Animations", "Folder":"meshes", "Extension":"hkx"})
	BSARules.append({"BSA":"Animations", "Folder":"meshes", "Extension":"txt"})

	BSARules.append({"BSA":"Meshes", "Folder":"meshes"})
	BSARules.append({"BSA":"Meshes", "Folder":"lodsettings"})

	BSARules.append({"BSA":"", "Folder":"grass"})
	BSARules.append({"BSA":"", "Folder":"scripts"})
	BSARules.append({"BSA":"", "Folder":"seq"})
	BSARules.append({"BSA":"", "Folder":"shadersfx"})
	BSARules.append({"BSA":"", "Folder":"strings"})
	BSARules.append({"BSA":"", "Folder":"interface"})

	BSARules.append({"BSA":"Voices", "Folder":"sound\\voice"})
	BSARules.append({"BSA":"", "Folder":"music"})
	BSARules.append({"BSA":"", "Folder":"sound\\fx"})
	
# Not implemented yet
#BSARules.append({"NotIncluded":True, "Folder":"source"})

