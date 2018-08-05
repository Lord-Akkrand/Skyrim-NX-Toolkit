@ECHO OFF

SET /A DDS_COUNT=0
SET /A DDS_PROCESSED=0
CD %1
SET /A DEPTH=0
ECHO Count Tree %1
CALL :countTree
IF DDS_COUNT GTR 0 (
	ECHO Found %DDS_COUNT% DDS Files
	ECHO Process DDS
	CALL :ddsProcess
)

CD..
PAUSE
GOTO :EOF

:countTree
SET /A DEPTH=DEPTH+1
FOR %%I IN (*.dds) DO (
	SET /A DDS_COUNT=DDS_COUNT+1
)

FOR /D %%d IN (*) DO (
    CD "%%d"
    CALL :countTree
    CD ..
)
SET /A DEPTH=DEPTH-1
EXIT /b

:ddsProcess
FOR %%I IN (*.dds) DO CALL :identifyDDS "%%I"

FOR /D %%d IN (*) DO (
    CD "%%d"
    CALL :ddsProcess
    CD ..
)
EXIT /b

:identifyDDS
CALL IDENTIFY_DDS.BAT "%~f1"
SET /A DDS_PROCESSED=DDS_PROCESSED+1
>CON ECHO DDS Processing %DDS_PROCESSED%/%DDS_COUNT%
EXIT /B
