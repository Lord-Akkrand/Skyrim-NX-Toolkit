![Skyrim NX Toolkit](Skyrim-NX-Toolkit.png)

#### External Tools and Credits
There are several external tools that are used by my scripts to get things done.  
- `bsarch.exe` is included in the repository directly, as it was developed under MPL.  
  It is available on Nexus here  
  <https://www.nexusmods.com/newvegas/mods/64745> and the source code is available here  
  <https://github.com/TES5Edit/TES5Edit/tree/dev/Tools/BSArchive>
- `Skyim NX Audio-Voice Dialog Converter.exe` was created by Clayson  
  <https://github.com/clayclayson>  It is included with permission.  
  `VGAudioCli.exe` is used during processing of Clayson's audio conversion tool.  
  <https://github.com/Thealexbarney/VGAudio>
- `XTX-Extractor` was created by AboodXD  
  <https://github.com/aboood40091> and is available here  
  <https://github.com/aboood40091/XTX-Extractor>

There are further external tools that the toolkit will attempt to download if you don't have them in the 'Utilities' directory, or that you must source yourself.
These tools are:
- `nvddsinfo.exe` <https://github.com/castano/nvidia-texture-tools/releases>
- `textconv.exe` <https://github.com/Microsoft/DirectXTex/releases>
- `texdiag.exe` <https://github.com/Microsoft/DirectXTex/releases>
  
  
- `HavocBehaviourPostProcess.exe` is available from the Bethesda Creation Kit.  
  It is necessary to convert any mod that has animations in it, and you are also required to have a 32-bit version of those animation files in order to perform that conversion.  

There are 2 folders in the toolkit folder, GraphicsTools & NvnTools, which require files that are not publicly available in order to work.  The Readme files in those folder list the files required for the SDK conversion to work.  I will not link to those files publicly.  
They cover slightly more texture formats than `XTX-Extractor`, and do so a lot faster.

#### Running in Python
All my scripts were written in Python 3.x, then packaged into an exe using PyInstaller.
If you have Python 3.x (and Python Launcher, or 'py') accessible from your command line, you may run the scripts directly if you like.
You can get Python here:
- Python 3.x https://www.python.org/downloads/

#### Examples
There are Examples listed in the "Examples" folder.  They are filled with dummy mod files, but you should be able to run them and they should produce the appropriate output.  
Most of the scripts can be used by dragging a folder onto them, but I prefer to run them from the command line in case there's an error whilst in the batch file, so you can see it before the window disappears.  
The examples all show proper command line usage.

