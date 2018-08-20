@ECHO OFF
:: Check for bsarch.exe installation
IF NOT EXIST "%TOOLKIT_PATH%Utilities\archive.exe" GOTO notFound
ECHO archive.exe exists in Utilites path >CON

EXIT /B 0

:notFound
ECHO archive.exe not found >CON
ECHO you need to install the Bethesda Launcher, and from that, the Skyrim Construction Kit >CON
ECHO Then put the archive.exe in your "Utilities" folder >CON

EXIT /B 1