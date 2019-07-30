$ErrorActionPreference = 'Stop'

$Global:SNXT = @{}

$Global:SNXT.HomeLocation = Split-Path $MyInvocation.MyCommand.Path
Push-Location $Global:SNXT.HomeLocation
$VerbosePreference = 'SilentlyContinue'
$DebugPreference = 'SilentlyContinue'

Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Path\SNXT-Path.psm1") -Force -WarningAction SilentlyContinue
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-BSA\SNXT-BSA.psm1") -Force -WarningAction SilentlyContinue
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Job\SNXT-Job.psm1") -Force -WarningAction SilentlyContinue

$UnitTest = "Unit Test NIF"

$UnitTests = Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "Unit Tests"
$UnitTestPath = Join-Path -Path $UnitTests -ChildPath $UnitTest
$Global:SNXT.BasePath = $UnitTestPath + "_Processed"

$Global:SNXT.Settings = @{}
$Global:SNXT.Settings.Meshes = @{}
$Global:SNXT.Settings.Meshes.RemoveEditorMarker = $True
$Global:SNXT.Settings.Meshes.PrettySortBlocks = $True
$Global:SNXT.Settings.Meshes.TrimTexturesPath = $True
$Global:SNXT.Settings.Meshes.OptimizeForSSE = $False

$Global:SNXT.Logfile = Join-Path -Path $UnitTests -ChildPath ($UnitTest + ".xml")
$Global:SNXT.LogBase = Join-Path -Path $Global:SNXT.BasePath -ChildPath "LogTree"
$Global:SNXT.MaxJobs = 24
$Global:SNXT.BatchSize = -96
$Global:SNXT.DebugResize = $False

ROBOCOPY $UnitTestPath $Global:SNXT.BasePath /MIR
if (Test-Path $Global:SNXT.Logfile) 
{
    Remove-Item -Path $Global:SNXT.Logfile
}
function Process-Mod
{
    Trace-Debug ("Process-Mod") $Global:SNXT.Logfile
    Unpack-Mod $Global:SNXT.BasePath
    Convert-Path
    Trace-Debug ("Process-Mod") $Global:SNXT.Logfile -1
}

$time = Measure-Command { Process-Mod } | Select-Object -Property TotalSeconds
Write-Host ('Process-Mod Time = {0} seconds' -f $time.TotalSeconds)

