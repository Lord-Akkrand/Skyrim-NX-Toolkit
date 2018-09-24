@ECHO OFF
SETLOCAL

SET TOOLKIT_PATH=%~d0%~p0
SET SCRIPTS_PATH=%TOOLKIT_PATH%Scripts\
SET REPACK_MOD_PY="%SCRIPTS_PATH%repack_mod.py"

SET ORIGINAL=%~f1
SET TARGET=%~f1_Repacked
SET EMPTY=%TOOLKIT_PATH%Empty

SET PATH=%PATH%;%SCRIPTS_PATH%
>CON ECHO Starting up...

>CON ECHO repack_mod.py is set at %REPACK_MOD_PY%
PAUSE

>CON ECHO Finding Python 3.x path
>CON CALL "%SCRIPTS_PATH%FIND_PYTHON_PATH"
IF ERRORLEVEL 1 GOTO pythonError
>CON ECHO Found Python 3.x path

>CON CALL "%SCRIPTS_PATH%CHECK_BSARCH"
IF ERRORLEVEL 1 GOTO utilityError

>CON ECHO Making "%TARGET%"
ROBOCOPY "%ORIGINAL%" "%TARGET%" /MIR

"%PYTHON3%" %REPACK_MOD_PY% "%ORIGINAL%" "%TARGET%"
PAUSE

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path
GOTO :EOF

:utilityError
>CON ECHO There was an error finding a 3rd-party tool.  Aborting.
GOTO :EOF