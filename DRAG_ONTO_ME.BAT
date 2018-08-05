@ECHO OFF
GOTO :END_TUTORIAL
This is my Google Drive link to this suite of scripts, to help convert mods' textures into a format usable by the Nintendo Switch.
https://drive.google.com/open?id=1zIMfoXr82TdDFAWAjDgSBuE8Cg1FS5r5

This is a work in progress.  I'll have a step-by-step when it actually works for most mods.

It attempts to locate the directory for python 3.x
If it can't, or there's some other problem with that, you can replace lines 23-24:
<<<<<
>CON CALL PYTHON_TEST
IF ERRORLEVEL 1 GOTO pythonError
<<<<<
 with 
>>>>>
SET PYTHON3="C:\Python34\python.exe"
>>>>>
(or whatever your path to python 3.x is)


:END_TUTORIAL


SET LOG=%~d1%~p1%~n1_Log.TXT

>CON ECHO Starting up...
SET SCRIPTS_PATH=%~d0%~p0
>CON ECHO Scripts Path is %SCRIPTS_PATH%
SET SDK_PATH=%SCRIPTS_PATH%
>CON ECHO SDK Path is %SDK_PATH%
SET NVN_TEXTPKG="%SDK_PATH%NvnTools\NvnTexpkg.exe"
>CON ECHO NvnTexpkg is at %NVN_TEXTPKG%
SET TEXCONVEXE="%SCRIPTS_PATH%texconv.exe"
>CON ECHO texconv.exe is set at %TEXCONVEXE%
SET TEXTDIAG="%SCRIPTS_PATH%\texdiag.exe"
>CON ECHO textdiag.exe is set at %TEXTDIAG%
SET NVDDSINFOEXE="%SCRIPTS_PATH%nvddsinfo.exe"
>CON ECHO nvddsinfo.exe is set at %NVDDSINFOEXE%
SET XTRACTOR="%SCRIPTS_PATH%XTX-Extractor-master\xtx_extract.py"
>CON ECHO XTX-Extractor-master is set at %XTRACTOR%
SET CONVERT_DDS_PY="%SCRIPTS_PATH%convert_dds.py"
>CON ECHO resize_dds.py is set at %CONVERT_DDS_PY%

IF EXIST %NVN_TEXTPKG% (
	SET HAS_SDK=true
) ELSE (
	SET HAS_SDK=false
)
>CON ECHO HAS_SDK is set as %HAS_SDK%

>CON ECHO Akkrand's NX Texture Conversion Scripts v3.2.3
pause


SET PATH=%PATH%;%SCRIPTS_PATH%

>CON ECHO Finding Python 3.x path
>CON CALL FIND_PYTHON_PATH
IF ERRORLEVEL 1 GOTO pythonError

>CON ECHO Found Python 3.x path

SET ORIGINAL=%~f1
SET DUPLICATE=%~f1_Converted

>CON ECHO Making "%DUPLICATE%"
ROBOCOPY "%ORIGINAL%" "%DUPLICATE%" /MIR

>CON ECHO Converting "%DUPLICATE%"
ECHO | CALL "%SCRIPTS_PATH%\CONVERT_PATH" "%DUPLICATE%" >"%LOG%"
>CON ECHO Done
PAUSE

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path
