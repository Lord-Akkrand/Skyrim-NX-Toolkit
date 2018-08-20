@ECHO OFF
:: Check for texconv.exe installation
IF NOT EXIST "%TOOLKIT_PATH%Utilities\texconv.exe" GOTO download
ECHO texconv.exe exists in Utilites path >CON

EXIT /B 0

:download
ECHO texconv.exe not found >CON

py -3 "%SCRIPTS_PATH%\download_file.py" https://github.com/Microsoft/DirectXTex/releases/download/aug2018/texconv.exe "%TOOLKIT_PATH%Utilities\texconv.exe"

IF EXIST "%TOOLKIT_PATH%Utilities\texconv.exe" EXIT /B 0
EXIT /B 1