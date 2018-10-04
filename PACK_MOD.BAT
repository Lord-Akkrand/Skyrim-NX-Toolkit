@ECHO OFF
SETLOCAL

SET TOOLKIT_PATH=%~d0%~p0
SET SCRIPTS_PATH=%TOOLKIT_PATH%Scripts\
SET DIST_PATH=%SCRIPTS_PATH%dist\
SET TOOLKIT_EXE="%DIST_PATH%toolkit.exe"

SET ORIGINAL=%~f1
SET TARGET=%~f1_Packed
SET MOD_NAME=%~n1
SET EMPTY=%TOOLKIT_PATH%Empty

SET PATH=%PATH%;%SCRIPTS_PATH%
>CON ECHO Starting up...

>CON ECHO toolkit.exe is set at %TOOLKIT_EXE%

>CON ECHO Making "%TARGET%"
ROBOCOPY "%ORIGINAL%" "%TARGET%" /MIR

PUSHD "%SCRIPTS_PATH%"
%TOOLKIT_EXE% pack_mod "%MOD_NAME%" "%TARGET%"
POPD

GOTO :EOF

:pythonError
>CON ECHO Error finding Python path
GOTO :EOF

:utilityError
>CON ECHO There was an error finding a 3rd-party tool.  Aborting.
GOTO :EOF