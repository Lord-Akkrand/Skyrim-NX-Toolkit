@ECHO OFF

SETLOCAL

SET LOG=%~d1%~p1%~n1_Log.TXT
SET TOOLKIT_PATH=%~d0%~p0
SET SCRIPTS_PATH=%TOOLKIT_PATH%Scripts\
SET LOAD_ORDER_PY="%SCRIPTS_PATH%packed_load_order.py"
SET PRISTINE=%TOOLKIT_PATH%DefaultIniFiles

SET ORIGINAL=%~dp1
SET TARGET=%~f2
SET LOAD_ORDER=%~n1

SET PATH=%PATH%;%SCRIPTS_PATH%

>CON ECHO Starting up...

>CON ECHO load_order.py is set at %LOAD_ORDER_PY%

>CON ECHO Akkrand's Packed Load Order Script v2.0.0
PAUSE

>CON ECHO Finding Python 3.x path
>CON CALL "%SCRIPTS_PATH%FIND_PYTHON_PATH"
IF ERRORLEVEL 1 GOTO pythonError

>CON ECHO Found Python 3.x path

>CON CALL "%SCRIPTS_PATH%CHECK_BSARCH"
IF ERRORLEVEL 1 GOTO utilityError
>CON CALL "%SCRIPTS_PATH%CHECK_ARCHIVE"
IF ERRORLEVEL 1 GOTO utilityError

ROBOCOPY "%PRISTINE%" "%TARGET%" /MIR /XF .gitignore

>"%LOG%" "%PYTHON3%" %LOAD_ORDER_PY% "%ORIGINAL%" "%TARGET%" %LOAD_ORDER% 1
PAUSE

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path
GOTO :EOF

:utilityError
>CON ECHO There was an error finding a 3rd-party tool.  Aborting.
GOTO :EOF