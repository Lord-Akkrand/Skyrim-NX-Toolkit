@ECHO OFF

>CON ECHO Starting up...
SET TOOLKIT_PATH=%~d0%~p0
SET SCRIPTS_PATH=%TOOLKIT_PATH%Scripts\

SET CONVERT_PATH_PY="%SCRIPTS_PATH%convert_path.py"
>CON ECHO convert_path.py is set at %CONVERT_PATH_PY%

SET PATH=%PATH%;%SCRIPTS_PATH%

>CON ECHO Finding Python 3.x path
>CON CALL "%SCRIPTS_PATH%FIND_PYTHON_PATH"
IF ERRORLEVEL 1 GOTO pythonError

>CON ECHO Found Python 3.x path

>CON CALL "%TOOLKIT_PATH%PS_GET_UTILITIES"
IF ERRORLEVEL 1 GOTO utilityError

SET ORIGINAL=%~f1
SET MOD_NAME=%~n1
SET TARGET=%~f1_Converted

SET startTime=%time%

>CON ECHO Making "%TARGET%"
ROBOCOPY "%ORIGINAL%" "%TARGET%" /MIR

>CON ECHO Converting "%TARGET%"
"%PYTHON3%" %CONVERT_PATH_PY% "%MOD_NAME%" "%TARGET%"
>CON ECHO Done

>CON ECHO Start Time: %startTime%
>CON ECHO Finish Time: %time%

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path
GOTO :EOF

:utilityError
>CON ECHO There was an error finding a 3rd-party tool.  Aborting.
GOTO :EOF
