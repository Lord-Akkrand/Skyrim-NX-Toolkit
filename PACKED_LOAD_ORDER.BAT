@ECHO OFF

SET LOG=%~d1%~p1%~n1_Log.TXT
SET SCRIPTS_PATH=%~d0%~p0
SET LOAD_ORDER_PY="%SCRIPTS_PATH%packed_load_order.py"
SET BSARCH="%SCRIPTS_PATH%bsarch.exe"

SET ORIGINAL=%~f1
SET DUPLICATE=%~f1_Converted

SET PATH=%PATH%;%SCRIPTS_PATH%

>CON ECHO Starting up...
>CON ECHO SCRIPTS_PATH is %SCRIPTS_PATH%
>CON ECHO bsarch.exe is set at %BSARCH%

>CON ECHO packed_load_order.py is set at %LOAD_ORDER_PY%

>CON ECHO Akkrand's Load Order Script v1.0.0
PAUSE

>CON ECHO Finding Python 3.x path
>CON CALL FIND_PYTHON_PATH
IF ERRORLEVEL 1 GOTO pythonError

>CON ECHO Found Python 3.x path

>"%LOG%" %PYTHON3% %LOAD_ORDER_PY% "%ORIGINAL%" "%DUPLICATE%" %BSARCH%
PAUSE

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path