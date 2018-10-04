@ECHO OFF
SETLOCAL

SET TOOLKIT_PATH=%~d0%~p0
SET SCRIPTS_PATH=%TOOLKIT_PATH%Scripts\
SET TOOLKIT_PY="%SCRIPTS_PATH%toolkit.py"

SET ORIGINAL=%~f1
SET TARGET=%~f1_Unpacked
SET EMPTY=%TOOLKIT_PATH%Empty

SET PATH=%PATH%;%SCRIPTS_PATH%
>CON ECHO Starting up...

>CON ECHO toolkit.py is set at %TOOLKIT_PY%

>CON ECHO Finding Python 3.x path
>CON CALL "%SCRIPTS_PATH%FIND_PYTHON_PATH"
IF ERRORLEVEL 1 GOTO pythonError

>CON ECHO Found Python 3.x path

>CON ECHO Making "%TARGET%"
ROBOCOPY "%EMPTY%" "%TARGET%" /MIR /PURGE /XF .gitignore

"%PYTHON3%" %TOOLKIT_PY% unpack_mod "%ORIGINAL%" "%TARGET%"

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path
GOTO :EOF

:utilityError
>CON ECHO There was an error finding a 3rd-party tool.  Aborting.
GOTO :EOF