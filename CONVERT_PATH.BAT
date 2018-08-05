@ECHO OFF
SET STARTTIME=%TIME%

SET /A DDS_COUNT=0
SET /A XWM_COUNT=0
SET /A DDS_PROCESSED=0
SET /A XWM_PROCESSED=0
CD %1
SET /A DEPTH=0
ECHO Count Tree %1
CALL :countTree
IF DDS_COUNT GTR 0 (
	ECHO Found %DDS_COUNT% DDS Files
	ECHO Process DDS
	CALL :ddsProcess
)
IF DDS_COUNT GTR 0 (
	ECHO Found %XWM_COUNT% XWM Files
	ECHO Process XWM
	CALL :xwmProcess
)

CD..
SET ENDTIME=%TIME%
PAUSE
GOTO :TIMER

:countTree
SET /A DEPTH=DEPTH+1
FOR %%I IN (*.dds) DO (
	SET /A DDS_COUNT=DDS_COUNT+1
)
FOR %%I IN (*.xwm) DO (
	SET /A XWM_COUNT=XWM_COUNT+1
)
FOR /D %%d IN (*) DO (
    CD "%%d"
    CALL :countTree
    CD ..
)
SET /A DEPTH=DEPTH-1
EXIT /b

:ddsProcess
FOR %%I IN (*.dds) DO CALL :convertDDS "%%I"

FOR /D %%d IN (*) DO (
    CD "%%d"
    CALL :ddsProcess
    CD ..
)
EXIT /b

:convertDDS
CALL CONVERT_DDS.BAT "%~f1"
ECHO %1 CONVERTED
SET /A DDS_PROCESSED=DDS_PROCESSED+1
>CON ECHO DDS Processing %DDS_PROCESSED%/%DDS_COUNT%
ECHO DDS Processing %DDS_PROCESSED%/%DDS_COUNT%
EXIT /B

:xwmProcess
FOR %%I IN (*.xwm) DO CALL :convertXWM %%I

FOR /D %%d IN (*) DO (
    CD "%%d"
    CALL :xwmProcess
    CD ..
)
EXIT /b

:convertXWM
ECHO Found an audio file %1
CALL CONVERT_XWM.BAT "%~f1"
ECHO %1 CONVERTED
SET /A XWM_PROCESSED=XWM_PROCESSED+1
>CON ECHO DDS Processing %XWM_PROCESSED%/%XWM_COUNT%
EXIT /B

:TIMER
rem Change formatting for the start and end times
for /F "tokens=1-4 delims=:.," %%a in ("%STARTTIME%") do (
    set /A "start=(((%%a*60)+1%%b %% 100)*60+1%%c %% 100)*100+1%%d %% 100"
)

for /F "tokens=1-4 delims=:.," %%a in ("%ENDTIME%") do (
    set /A "end=(((%%a*60)+1%%b %% 100)*60+1%%c %% 100)*100+1%%d %% 100"
)

rem Calculate the elapsed time by subtracting values
set /A elapsed=end-start

rem Format the results for output
set /A hh=elapsed/(60*60*100), rest=elapsed%%(60*60*100), mm=rest/(60*100), rest%%=60*100, ss=rest/100, cc=rest%%100
if %hh% lss 10 set hh=0%hh%
if %mm% lss 10 set mm=0%mm%
if %ss% lss 10 set ss=0%ss%
if %cc% lss 10 set cc=0%cc%

set DURATION=%hh%:%mm%:%ss%.%cc%

echo Start    : %STARTTIME%
echo Finish   : %ENDTIME%
echo          ---------------
echo Duration : %DURATION% 