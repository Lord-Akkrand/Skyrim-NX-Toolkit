Clear-Host

$ErrorActionPreference = 'Stop'

$Global:SNXT = @{}
$Global:SNXT.HomeLocation = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Write-Host ("Global:SNXT.HomeLocation [{0}]" -f $Global:SNXT.HomeLocation)
Push-Location $Global:SNXT.HomeLocation
$VerbosePreference = 'SilentlyContinue'
$DebugPreference = 'SilentlyContinue'

Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue

Get-ExternalUtilites