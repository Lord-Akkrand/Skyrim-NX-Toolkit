@ECHO OFF
GOTO :END_TUTORIAL

spits out identifying information about all the textures in a mod

:END_TUTORIAL


SET LOG=%~d1%~p1%~n1_Log.TXT

>CON ECHO Starting up...
SET SCRIPTS_PATH=%~d0%~p0
>CON ECHO Scripts Path is %SCRIPTS_PATH%
SET XTRACTOR="%SCRIPTS_PATH%\XTX-Extractor-master\xtx_extract.py"
>CON ECHO XTX-Extractor-master is set at %XTRACTOR%
SET TEXCONVEXE="%SCRIPTS_PATH%\texconv.exe"
>CON ECHO texconv.exe is set at %TEXCONVEXE%
SET NVDDSINFOEXE="%SCRIPTS_PATH%\nvddsinfo.exe"
>CON ECHO nvddsinfo.exe is set at %NVDDSINFOEXE%
SET TEXTDIAG="%SCRIPTS_PATH%\texdiag.exe"
>CON ECHO textdiag.exe is set at %TEXTDIAG%
SET IDENTIFIER_DDS_PY="%SCRIPTS_PATH%\identify_dds.py"
>CON ECHO identify_dds.py is set at %IDENTIFIER_DDS_PY%
SET OUTPUT_CSV="%~d1%~p1%~n1_Identified.CSV"
>CON ECHO Output CSV is set at %OUTPUT_CSV%

IF EXIST %OUTPUT_CSV% (ERASE %OUTPUT_CSV%)

>CON ECHO Akkrand's NX Texture Identifier 1.0

SET PATH=%PATH%;%SCRIPTS_PATH%
>CON CALL FIND_PYTHON_PATH
IF ERRORLEVEL 1 GOTO pythonError

SET ORIGINAL=%~f1

>CON ECHO Identifying "%ORIGINAL%"
ECHO | CALL "%SCRIPTS_PATH%\IDENTIFY_PATH" "%ORIGINAL%" >"%LOG%"
>CON ECHO Done

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path