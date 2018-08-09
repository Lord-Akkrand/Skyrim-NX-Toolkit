@ECHO OFF

SETLOCAL

SET TOOLKIT_PATH=%~d0%~p0
SET SCRIPTS_PATH=%TOOLKIT_PATH%Scripts\
SET TOOLKIT_MENU_PY="%SCRIPTS_PATH%toolkit_menu.py"

>CON ECHO Akkrand's Skyrim-NX Toolkit Script v1.0.0

>CON ECHO Finding Python 3.x path
>CON CALL FIND_PYTHON_PATH
IF ERRORLEVEL 1 GOTO pythonError

%PYTHON3% %TOOLKIT_MENU_PY% %1

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path