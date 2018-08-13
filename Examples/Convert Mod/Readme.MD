# Convert Mod

Convert Mod will make a copy of a mod folder and unpack all the bsas from the mod into that folder, and copy across everything else.  
It will then convert all the textures in the newly unpacked mod folder.  
It will finally pack all the loose files back up into bsas.  
The output is functionally identical to calling Unpack Mod, Convert Textures, Pack Mod on each of the successives outputs from those scripts.

## Usage

`CONVERT_MOD.BAT "C:\path\to\mod"`

It expects the folder passed to it contains the "Data" for the mod.  That is, an ESP, INI, BSA files and (optionally) the loose folders (grass/interface/lodsettings/meshes/music/scripts/seq/shadersfx/sound/strings/textures)

