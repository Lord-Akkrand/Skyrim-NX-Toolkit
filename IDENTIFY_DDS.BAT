@ECHO OFF
ECHO Identify DDS "%~f1" (%~z1)
%NVDDSINFOEXE% %1 >%1.ddsinfo.txt
%PYTHON3% %IDENTIFIER_DDS_PY% "%ORIGINAL%" %1 %1.ddsinfo.txt %OUTPUT_CSV%
TYPE %1.ddsinfo.txt
%TEXTDIAG% info %1 2>&1
ERASE %1.ddsinfo.txt



