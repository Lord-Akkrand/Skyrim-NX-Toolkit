@ECHO OFF
ECHO Convert DDS "%~f1" (%~z1)
ECHO INFO_DDS - %1
ECHO CONVERT_DDS v2.0
%NVDDSINFOEXE% %1 >%1.ddsinfo.txt 
%TEXTDIAG% info %1 >%1.texdiag.txt
"%PYTHON3%" %CONVERT_DDS_PY% %TEXCONVEXE% "%DUPLICATE%" %1 %1.ddsinfo.txt %1.texdiag.txt %HAS_SDK%

ERASE %1.ddsinfo.txt 2>&1
ERASE %1.texdiag.txt 2>&1
ECHO Converting from DDS to XTX
IF EXIST %NVN_TEXTPKG% (
	ECHO Found NvnTextpkg
	%NVN_TEXTPKG% -i %1 -v --printinfo 2>&1	

	IF EXIST out.xtx (
		CALL :MOVE_ITEM out.xtx "%~n1".dds
	) ELSE (
		ECHO Something went wrong!
		>CON ECHO Something went wrong with %1  
	)
) ELSE (
	ECHO Did not find NvnTextpkg
	%PYTHON3% %XTRACTOR% %1
	CALL :MOVE_ITEM "%~n1".xtx "%~n1".dds
)

GOTO :EOF

:MOVE_ITEM
ECHO MOVE %1 %2
MOVE /Y %1 %2 2>&1
IF ERRORLEVEL 1 (GOTO MOVE_ITEM)

EXIT /B
