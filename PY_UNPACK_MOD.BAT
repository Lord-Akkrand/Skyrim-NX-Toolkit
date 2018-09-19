@ECHO OFF
SETLOCAL

SET TOOLKIT_PATH=%~d0%~p0
SET SCRIPTS_PATH=%TOOLKIT_PATH%Scripts\
SET UNPACK_MOD_PY="%SCRIPTS_PATH%unpack_mod.py"

SET ORIGINAL=%~f1
SET TARGET=%~f1_Unpacked
SET EMPTY=%TOOLKIT_PATH%Empty

SET PATH=%PATH%;%SCRIPTS_PATH%
>CON ECHO Starting up...

>CON ECHO unpack_mod.py is set at %UNPACK_MOD_PY%

>CON ECHO Akkrand's Unpack Mod Script v1.0.0
>CON ECHO This script expects to be given a folder containing all the files for a mod:
>CON ECHO ESP Files
>CON ECHO BSA Files
>CON ECHO INI Files
>CON ECHO Skyrim Data Folders (grass/interface/lodsettings/meshes/music/scripts/seq/shadersfx/sound/strings/textures)
PAUSE

>CON ECHO Finding Python 3.x path
>CON CALL "%SCRIPTS_PATH%FIND_PYTHON_PATH"
IF ERRORLEVEL 1 GOTO pythonError

>CON ECHO Found Python 3.x path

>CON CALL "%SCRIPTS_PATH%CHECK_BSARCH"
IF ERRORLEVEL 1 GOTO utilityError


>CON ECHO Making "%TARGET%"
ROBOCOPY "%EMPTY%" "%TARGET%" /MIR /PURGE /XF .gitignore

"%PYTHON3%" %UNPACK_MOD_PY% "%ORIGINAL%" "%TARGET%"
PAUSE

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path
GOTO :EOF

:utilityError
>CON ECHO There was an error finding a 3rd-party tool.  Aborting.
GOTO :EOF