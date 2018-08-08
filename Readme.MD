![Skyrim NX Toolkit](Skyrim-NX-Toolkit.png)

It is necessary that you have Python 3.x installed.
- Python 3.x https://www.python.org/downloads/
The batch scripts will attempt to find the path to your python.exe automatically.  If it fails, you will get an error and may need to modify the FIND_PYTHON.BAT file to compensate.

The script will resize any textures above 1024x1024 (in linear size) down to that size.  If you want to change that, open sizes.py and edit it.  Fairly straightforward to change the default.
There is a blanket rule for max size - DefaultLimit to 1024x1024, and a series of rules which override that.

If you drag a folder onto the file DRAG_ONTO_ME.BAT, it should start the process.
- It will pause at the beginning, displaying "Akkrand's NX Texture Conversion Scripts" and the version of the script.
- It makes  copy of the folder you dragged on, with _Converted added to it.  So, if you were converting "C:\Mods\CBBE", it would create a folder called "C:\Mods\CBBE_Converted"
- It makes a log file named after the folder, so continuing our example of CBBE, it would make a file "C:\Mods\CBBE_Log.TXT"

The converted mod will need to be packed back into a BSA and loaded in your Skyrim.ini(edited)

Alternatively, if you have all the files for a given mod in a folder (esp + bsas or loose files), you can convert the mod using CONVERT_MOD.BAT
- It will unpack any bsas it finds, and copy across any other loose files it finds
- it will then convert any textures it finds
- It will then pack all the folders (textures/meshes/scripts/etc) into bsas, one for misc, one for meshes, and one for textures


There are 2 folders in the toolkit folder, GraphicsTools & NvnTools, which require files that are not publicly available in order to work.  The Readme files in those folder list the files required for the SDK conversion to work.  I will not link to those files publicly.

Note that you require some external tools to run my scripts, they should be placed in the 'Utilities' directory.
The external tools are:
- Archive.exe (from the Bethesda CK for SSE)
- bsarch.exe <https://www.nexusmods.com/newvegas/mods/64745>
- nvddsinfo.exe <https://github.com/castano/nvidia-texture-tools/releases>
- textconv.exe <https://github.com/Microsoft/DirectXTex/releases>
- texdiag.exe <https://github.com/Microsoft/DirectXTex/releases>


