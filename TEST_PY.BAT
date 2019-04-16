@ECHO OFF


CALL :convertMod
CALL :loadOrder
CALL :packMod
CALL :unpackMod

GOTO :EOF

:convertMod
PUSHD "Examples\Convert Mod"
CALL PY_TEST_CONVERT_MOD.BAT
POPD
EXIT /B

:loadOrder
PUSHD "Examples\Load Order"
CALL PY_MAIN_LOAD_ORDER.BAT
CALL PY_TEST_LOAD_ORDER.BAT
POPD
EXIT /B

:packMod
PUSHD "Examples\Pack Mod"
CALL PY_TEST_PACK_MOD.BAT
POPD
EXIT /B

:unpackMod
PUSHD "Examples\Unpack Mod"
CALL PY_TEST_UNPACK_MOD.BAT
POPD
EXIT /B