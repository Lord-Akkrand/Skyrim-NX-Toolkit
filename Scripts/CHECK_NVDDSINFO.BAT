@ECHO OFF
:: Check for nvddsinfo.exe installation
IF NOT EXIST "%TOOLKIT_PATH%Utilities\nvddsinfo.exe" GOTO download
ECHO nvddsinfo.exe exists in Utilites path >CON

EXIT /B 0

:download
ECHO nvddsinfo.exe not found >CON

py -3 "%SCRIPTS_PATH%\download_file.py" https://github.com/castano/nvidia-texture-tools/releases/download/2.1.1/nvidia-texture-tools-2.1.1-win64.zip "%TOOLKIT_PATH%Utilities\temp.zip"
py -3 "%SCRIPTS_PATH%\unzip_file.py" "%TOOLKIT_PATH%Utilities\temp.zip" "%TOOLKIT_PATH%Utilities\nvddsinfo.exe"
ERASE "%TOOLKIT_PATH%Utilities\temp.zip"

IF EXIST "%TOOLKIT_PATH%Utilities\nvddsinfo.exe" EXIT /B 0
EXIT /B 1