@ECHO OFF

SET LOG=%~d1%~p1%~n1_ConvertLog.TXT
SET SCRIPTS_PATH=%~d0%~p0
SET CONVERT_MOD_PY="%SCRIPTS_PATH%convert_mod.py"
SET BSARCH="%SCRIPTS_PATH%bsarch.exe"
SET EMPTY=%SCRIPTS_PATH%Empty

SET ORIGINAL=%~f1
SET DUPLICATE=%~f1_Unpacked
SET DUPLICATE_DATA=%DUPLICATE%\Data

SET PATH=%PATH%;%SCRIPTS_PATH%
SET SDK_PATH=%SCRIPTS_PATH%

SET NVN_TEXTPKG="%SDK_PATH%NvnTools\NvnTexpkg.exe"
SET TEXCONVEXE="%SCRIPTS_PATH%texconv.exe"
SET TEXTDIAG="%SCRIPTS_PATH%\texdiag.exe"
SET NVDDSINFOEXE="%SCRIPTS_PATH%nvddsinfo.exe"
SET XTRACTOR="%SCRIPTS_PATH%XTX-Extractor-master\xtx_extract.py"

>CON ECHO Starting up...
>CON ECHO SCRIPTS_PATH is %SCRIPTS_PATH%
>CON ECHO bsarch.exe is set at %BSARCH%
IF EXIST %NVN_TEXTPKG% (
	SET HAS_SDK=true
) ELSE (
	SET HAS_SDK=false
)

>CON ECHO SDK Path is %SDK_PATH%
>CON ECHO HAS_SDK is set as %HAS_SDK%
>CON ECHO NvnTexpkg is at %NVN_TEXTPKG%
>CON ECHO texconv.exe is set at %TEXCONVEXE%
>CON ECHO textdiag.exe is set at %TEXTDIAG%
>CON ECHO nvddsinfo.exe is set at %NVDDSINFOEXE%
>CON ECHO XTX-Extractor-master is set at %XTRACTOR%
>CON ECHO convert_mod.py is set at %CONVERT_MOD_PY%

>CON ECHO Akkrand's Mod Converter v1.0.3
PAUSE

>CON ECHO Finding Python 3.x path
>CON CALL FIND_PYTHON_PATH
IF ERRORLEVEL 1 GOTO pythonError

>CON ECHO Found Python 3.x path

>CON ECHO Making "%DUPLICATE%"
ROBOCOPY "%EMPTY%" "%DUPLICATE%" /MIR
ROBOCOPY "%ORIGINAL%" "%DUPLICATE_DATA%" /MIR

>"%LOG%" %PYTHON3% %CONVERT_MOD_PY% "%ORIGINAL%" "%DUPLICATE%" %BSARCH% %HAS_SDK%
PAUSE

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path