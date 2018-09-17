@ECHO OFF
:: Check for texdiag.exe installation
IF NOT EXIST "%TOOLKIT_PATH%Utilities\texdiag.exe" GOTO download
ECHO texdiag.exe exists in Utilites path >CON

EXIT /B 0

:download
ECHO texdiag.exe not found >CON

%TOOLKIT_EXE% download_file https://github.com/Microsoft/DirectXTex/releases/download/aug2018/texdiag.exe "%TOOLKIT_PATH%Utilities\texdiag.exe"

IF EXIST "%TOOLKIT_PATH%Utilities\texdiag.exe" EXIT /B 0
EXIT /B 1