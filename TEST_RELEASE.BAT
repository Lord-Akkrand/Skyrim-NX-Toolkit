@ECHO OFF


CALL :convertMod
CALL :loadOrder
CALL :packMod
CALL :unpackMod

GOTO :EOF

:convertMod
PUSHD "Examples\Convert Mod"
CALL TEST_CONVERT_MOD.BAT
IF ERRORLEVEL 1 GOTO :error
POPD
EXIT /B

:loadOrder
PUSHD "Examples\Load Order"
CALL MAIN_LOAD_ORDER.BAT
IF ERRORLEVEL 1 GOTO :error
CALL TEST_LOAD_ORDER.BAT
IF ERRORLEVEL 1 GOTO :error
POPD
EXIT /B

:packMod
PUSHD "Examples\Pack Mod"
CALL TEST_PACK_MOD.BAT
IF ERRORLEVEL 1 GOTO :error
POPD
EXIT /B

:unpackMod
PUSHD "Examples\Unpack Mod"
CALL TEST_UNPACK_MOD.BAT
IF ERRORLEVEL 1 GOTO :error
POPD
EXIT /B

:error
ECHO Error whilst testing