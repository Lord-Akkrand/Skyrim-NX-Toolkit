@ECHO OFF
SETLOCAL

SET TOOLKIT_PATH=%~d0%~p0
SET SCRIPTS_PATH=%TOOLKIT_PATH%Scripts\
SET RECONCILE_HKX_PY="%SCRIPTS_PATH%reconcile_hkx.py"

SET ORIGINAL=%~f1
SET TARGET=%~f1_Reconciled
SET OLDRIM=%~f2

SET PATH=%PATH%;%SCRIPTS_PATH%

>CON ECHO Starting up...

>CON ECHO reconcile_hkx.py is set at %RECONCILE_HKX_PY%
PAUSE

>CON ECHO Finding Python 3.x path
>CON CALL "%SCRIPTS_PATH%FIND_PYTHON_PATH"
IF ERRORLEVEL 1 GOTO pythonError
ROBOCOPY "%ORIGINAL%" "%TARGET%" /MIR

"%PYTHON3%" %RECONCILE_HKX_PY% "%TARGET%" "%OLDRIM%"
PAUSE

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path
GOTO :EOF

:utilityError
>CON ECHO There was an error finding a 3rd-party tool.  Aborting.
GOTO :EOF