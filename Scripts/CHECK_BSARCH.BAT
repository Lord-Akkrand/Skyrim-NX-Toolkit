@ECHO OFF
:: Check for bsarch.exe installation
IF NOT EXIST "%TOOLKIT_PATH%Utilities\bsarch.exe" GOTO notFound
ECHO bsarch.exe exists in Utilites path >CON

EXIT /B 0

:notFound
ECHO bsarch.exe not found >CON
ECHO you need to download it from Nexus at https://www.nexusmods.com/newvegas/mods/64745?tab=files >CON
ECHO And put it in your "Utilities" folder >CON

EXIT /B 1