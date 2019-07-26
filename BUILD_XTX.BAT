@ECHO OFF
SETLOCAL

SET TOOLKIT_PATH=%~d0%~p0
SET SCRIPTS_PATH=%TOOLKIT_PATH%Scripts\

SET PATH=%PATH%;%SCRIPTS_PATH%

>CON ECHO Starting up...

PAUSE

>CON ECHO Finding Python 3.x path
>CON CALL "%SCRIPTS_PATH%FIND_PYTHON_PATH"
IF ERRORLEVEL 1 GOTO pythonError

PUSHD "%SCRIPTS_PATH%"

:ToolKit
ECHO "%PYTHON3%" -m PyInstaller --onefile xtx_extract.py
"%PYTHON3%" -m PyInstaller --onefile xtx_extract.py
POPD
PAUSE

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path
GOTO :EOF

:utilityError
>CON ECHO There was an error finding a 3rd-party tool.  Aborting.
GOTO :EOF