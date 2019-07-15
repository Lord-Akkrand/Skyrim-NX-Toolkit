![Skyrim NX Toolkit](https://media.discordapp.net/attachments/490595683418636304/497188424273494047/ACH003_big.png)

#### External Tools and Credits
There are several external tools that are used by my scripts to get things done.  
- `bsarch.exe` is included in the repository directly, as it was developed under MPL.  
  It is available on Nexus here  
  <https://www.nexusmods.com/newvegas/mods/64745> and the source code is available here  
  <https://github.com/TES5Edit/TES5Edit/tree/dev/Tools/BSArchive>
- `Skyim NX Audio-Voice Dialog Converter.exe` was created by SockNastre  
  <https://github.com/SockNastre>  It is included with permission.  
  `VGAudioCli.exe` is used during processing of SockNastre's audio conversion tool.  
  <https://github.com/Thealexbarney/VGAudio>
- `XTX-Extractor` was created by AboodXD  
  <https://github.com/aboood40091> and is available here  
  <https://github.com/aboood40091/XTX-Extractor>
- `nx_fuz.py` was written by Zappastuff <https://github.com/thywoof>
- `convert_hkx64.py` was written by Zappastuff <https://github.com/thywoof>
- `AdPDDS.exe` was created by apipino on Nexus <https://www.nexusmods.com/skyrim/users/1522687> and is distributed as a part of his texture opimizer `Ordenador` <https://www.nexusmods.com/skyrim/mods/12801/>
- `nswnifopt.exe` was written by Zappastuff <https://github.com/thywoof>, it was based on the work of <https://github.com/opparco/nifopt>


There are further external tools that the toolkit will attempt to download if you don't have them in the `Utilities` directory, or that you must source yourself.
These tools are:
- `nvddsinfo.exe` <https://github.com/castano/nvidia-texture-tools/releases>
- `textconv.exe` <https://github.com/Microsoft/DirectXTex/releases>
- `texdiag.exe` <https://github.com/Microsoft/DirectXTex/releases>
  
  
- `HavocBehaviourPostProcess.exe` is available from the Bethesda Creation Kit.  
  It is necessary to convert any mod that has animations in it, and you are also required to have a 32-bit version of those animation files in order to perform that conversion.  
  If you have the CK, you need to copy `Tools\HavokBehaviorPostProcessHavocBehaviourPostProcess.exe` to the `Utilities` directory in the Skyrim-NX-Toolkit.

- It won’t convert skeleton and skeleton_female files. Get them from XPMS Switch version on Nexus
- It won’t convert files in behaviors folders. Only occurrence I found in all SSE mods so far were in USSEP and FNIS. You can fish 32 bit equivalent
- FNIS based mods can regenerate their behavior files in 32 bit by using the “Generate Behavior for Modders” tool included in FNIS oldrim
  
#### Running in Python
All my scripts were written in Python 3.x, then packaged into an exe using PyInstaller.
If you have Python 3.x (and Python Launcher, or 'py') accessible from your command line, you may run the scripts directly if you like.
You can get Python here:
- Python 3.x https://www.python.org/downloads/

#### Examples
There are Examples listed in the "Examples" directory.  They are filled with dummy mod files, but you should be able to run them and they should produce the appropriate output.  
Most of the scripts can be used by dragging a directory onto them, but I prefer to run them from the command line in case there's an error whilst in the batch file, so you can see it before the window disappears.  
The examples all show proper command line usage.

