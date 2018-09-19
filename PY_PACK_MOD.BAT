@ECHO OFF
SETLOCAL

SET TOOLKIT_PATH=%~d0%~p0
SET SCRIPTS_PATH=%TOOLKIT_PATH%Scripts\
SET PACK_MOD_PY="%SCRIPTS_PATH%pack_mod.py"

SET ORIGINAL=%~f1
SET TARGET=%~f1_Packed
SET MOD_NAME=%~n1
SET EMPTY=%TOOLKIT_PATH%Empty

SET PATH=%PATH%;%SCRIPTS_PATH%
>CON ECHO Starting up...

>CON ECHO pack_mod.py is set at %PACK_MOD_PY%

>CON ECHO Akkrand's Mod Packing Utility v1.0.0
PAUSE

>CON ECHO Finding Python 3.x path
>CON CALL "%SCRIPTS_PATH%FIND_PYTHON_PATH"
IF ERRORLEVEL 1 GOTO pythonError
>CON ECHO Found Python 3.x path

>CON CALL "%SCRIPTS_PATH%CHECK_BSARCH"
IF ERRORLEVEL 1 GOTO utilityError

>CON ECHO Making "%TARGET%"
ROBOCOPY "%ORIGINAL%" "%TARGET%" /MIR

"%PYTHON3%" %PACK_MOD_PY% "%MOD_NAME%" "%TARGET%"
PAUSE

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path
GOTO :EOF

:utilityError
>CON ECHO There was an error finding a 3rd-party tool.  Aborting.
GOTO :EOF