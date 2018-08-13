# Pack Mod

Pack mod packages a mod using Archive.exe, making separate bsas for textures, meshes, and everything else.
It will automatically break up bsas that would be larger than 2gb into several bsas.

## Usage

`PACK_MOD.BAT "C:\path\to\mod"`

It expects the folder passed to it contains the "Data" for the mod.  That is, an ESP, INI, and the folders (grass/interface/lodsettings/meshes/music/scripts/seq/shadersfx/sound/strings/textures)

