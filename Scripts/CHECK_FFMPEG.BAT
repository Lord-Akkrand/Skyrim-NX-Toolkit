@ECHO OFF
:: Check for ffmpeg.exe installation
IF NOT EXIST "%TOOLKIT_PATH%Utilities\ffmpeg.exe" GOTO download
ECHO texdiag.exe exists in Utilites path >CON

EXIT /B 0

:download
ECHO ffmpeg.exe not found >CON

%TOOLKIT_EXE% download_file https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-latest-win64-static.zip "%TOOLKIT_PATH%Utilities\ffmpeg.zip"
%TOOLKIT_EXE% unzip_file "%TOOLKIT_PATH%Utilities\ffmpeg.zip" "%TOOLKIT_PATH%Utilities\ffmpeg.exe"
ERASE "%TOOLKIT_PATH%Utilities\ffmpeg.zip"

IF EXIST "%TOOLKIT_PATH%Utilities\ffmpeg.exe" EXIT /B 0
EXIT /B 1