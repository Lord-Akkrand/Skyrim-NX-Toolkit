@ECHO OFF
:: Check for Python Installation
py --version 2>NUL
if ERRORLEVEL 1 GOTO errorNoPython

ECHO Python is installed >CON
:: Reaching here means Python is installed.
:: Execute stuff...

py -3 --version >pythontemp.txt
FIND "Python 3" pythontemp.txt >NUL
IF %ERRORLEVEL% EQU 0 GOTO setPythonExe
ERASE pythontemp.txt
ECHO. >CON
ECHO Error^: Incorrect Python version installed (requires Python 3.x) >CON

EXIT /B 1

:errorNoPython
ECHO.
ECHO Error^: Python not installed (requires Python 3.x) >CON

EXIT /B 1

:setPythonExe
ERASE pythontemp.txt
py -3 "%SCRIPTS_PATH%\getpypath.py" >pythontemp.txt

SET /P PYTHON3=<pythontemp.txt
ECHO PYTHON3 is %PYTHON3% >CON
ERASE pythontemp.txt

EXIT /B 0