@ECHO OFF
ECHO Convert DDS "%~f1" (%~z1)
ECHO INFO_DDS - %1
ECHO CONVERT_DDS v2.0
%NVDDSINFOEXE% %1 >%1.ddsinfo.txt 
%TEXTDIAG% info %1 >%1.texdiag.txt

