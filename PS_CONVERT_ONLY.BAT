@pushd "%~p0"
@POWERSHELL -NoProfile -ExecutionPolicy ByPass -File SNXT-COM/Convert-Only.ps1 "%~f1"
@popd