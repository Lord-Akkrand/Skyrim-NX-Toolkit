@ECHO OFF
SETLOCAL
SET SCRIPTS_PATH=%~d0%~p0
SET ARCHIVE_BSA_PY="%SCRIPTS_PATH%archive_bsa.py"

SET ORIGINAL=%~f1
SET DUPLICATE=%~f1_Archived

SET PATH=%PATH%;%SCRIPTS_PATH%
>CON ECHO Starting up...

>CON ECHO archive_bsa.py is set at %ARCHIVE_BSA_PY%

>CON ECHO Akkrand's Archive Utility v1.0.0
PAUSE

>CON ECHO Finding Python 3.x path
>CON CALL FIND_PYTHON_PATH
IF ERRORLEVEL 1 GOTO pythonError

>CON ECHO Found Python 3.x path

>CON ECHO Making "%DUPLICATE%"
ROBOCOPY "%ORIGINAL%" "%DUPLICATE%" /MIR

%PYTHON3% %ARCHIVE_BSA_PY% "%DUPLICATE%" "%ORIGINAL%"
PAUSE

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path