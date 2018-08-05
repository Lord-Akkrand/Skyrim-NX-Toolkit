[SCRIPTS FOR RESIZED TEXTURE Conversion v3.2.3]
Here is a link to the windows batch scripts I've written to do resized texture conversion of mods for Skyrim NX:
https://drive.google.com/open?id=1EXJEBl6QY057hwHpkYRCyxnwckhZmTtJ

It is also necessary that you have Python 3.x installed.
- Python 3.x https://www.python.org/downloads/
The script will attempt to find the path to your python.exe automatically.  If it fails, you will get an error and may need to modify the DRAG_ONTO_ME.BAT file to compensate.

I've removed the dependency on ImageMagick.  It was causing too many issues for people.
The script will resize any textures above 1024x1024 (in linear size) down to that size.  If you want to change that, open sizes.py and edit it.  Fairly straightforward to change the default.
There is a blanket rule for max size - DefaultLimit to 1024x1024, and a series of rules which override that.
I added an examples of /actors/dragon/dragonskeleton.dds and /actors/character/* being limited to 2048x2048

If you drag a folder onto the file DRAG_ONTO_ME.BAT, it should start the process.
- It will pause at the beginning, displaying "Akkrand's NX Texture Conversion Scripts" and the version of the script.
- It makes  copy of the folder you dragged on, with _Converted added to it.  So, if you were converting "C:\Mods\CBBE", it would create a folder called "C:\Mods\CBBE_Converted"
- It makes a log file named after the folder, so continuing our example of CBBE, it would make a file "C:\Mods\CBBE_Log.TXT"

The converted mod will need to be packed back into a BSA and loaded in your Skyrim.ini(edited)
If you have 2 folders called NvnTools & GraphicsTools in the scripts folder, and the NvnTools folder contains NvnTextPkg.exe (which I will not link to here), then the script will use that to do the texture conversion instead of xtx-xtractor.
The folder structure would look like this:
Scripts/
Scripts/DRAG_ONTO_ME.BAT (and other files)
Scripts/GraphicsTools/... (2 dlls)
Scripts/NvnTools/NvnTextPkg.exe (and other files)
Scripts/test me
Scripts/test me_Converted
Scripts/XTX-Extractor-master


Note that the linked folder contains 3 external tools that I did not develop myself, but I've included them as they're publicly available, so people don't have problems downloading the wrong ones or installing them into different paths than I used.
The external tools are:
- textconv https://github.com/Microsoft/DirectXTex/releases
- Switch 'XTX' Texture Extractor https://github.com/aboood40091/XTX-Extractor
- nVidia Texture Tools https://github.com/castano/nvidia-texture-tools/releases