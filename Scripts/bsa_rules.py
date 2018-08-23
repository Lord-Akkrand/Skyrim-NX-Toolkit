#! python3

# 2GB Limit for BSA Files (I know 2GB is actually 2048 MB, not 2000, but Bethesdas BSAs limit seemed to be 2000MB)
BSASizeLimit = 1024 * 1024 * 2000

BSARules = []
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

BSARules.append({"BSA":"Textures", "Folder":"textures"})

BSARules.append({"BSA":"Voices", "Folder":"sound\\voice"})