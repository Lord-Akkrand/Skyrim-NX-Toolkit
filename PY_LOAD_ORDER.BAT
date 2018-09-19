@ECHO OFF

SETLOCAL

SET TOOLKIT_PATH=%~d0%~p0
SET SCRIPTS_PATH=%TOOLKIT_PATH%Scripts\
SET LOAD_ORDER_PY="%SCRIPTS_PATH%load_order.py"
SET PRISTINE=%TOOLKIT_PATH%DefaultIniFiles

SET ORIGINAL=%~f1
SET TARGET=%~f2
SET LOAD_ORDER=%3

SET PATH=%PATH%;%SCRIPTS_PATH%

>CON ECHO Starting up...

>CON ECHO load_order.py is set at %LOAD_ORDER_PY%

>CON ECHO Akkrand's Load Order Script v1.0.2
PAUSE

>CON ECHO Finding Python 3.x path
>CON CALL "%SCRIPTS_PATH%FIND_PYTHON_PATH"
IF ERRORLEVEL 1 GOTO pythonError

>CON ECHO Found Python 3.x path

ROBOCOPY "%PRISTINE%" "%TARGET%" /MIR /XF .gitignore

"%PYTHON3%" %LOAD_ORDER_PY% "%ORIGINAL%" "%TARGET%" %LOAD_ORDER%
PAUSE

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path