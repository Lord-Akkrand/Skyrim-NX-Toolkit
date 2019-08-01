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

$UnitTest = "Akkrandrim"

$UnitTests = Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "Unit Tests"
$UnitTestPath = Join-Path -Path $UnitTests -ChildPath $UnitTest
$Global:SNXT.BasePath = $UnitTestPath + "_Processed"

Set-Config

$Global:SNXT.Logfile = Join-Path -Path $UnitTests -ChildPath ($UnitTest + ".xml")
$Global:SNXT.LogBase = Join-Path -Path $Global:SNXT.BasePath -ChildPath "LogTree"

ROBOCOPY $UnitTestPath $Global:SNXT.BasePath /MIR
if (Test-Path $Global:SNXT.Logfile) 
{
    Remove-Item -Path $Global:SNXT.Logfile
}
function Process-Mod
{
    Begin
    {
        Trace-Verbose ("Process-Mod") $Global:SNXT.Logfile
        $startTime = Get-Date
    }

    Process
    {
        Unpack-Mod $Global:SNXT.BasePath
        Convert-Path
    }
    
    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Process-Mod-Time{0}' -f $timeString) $Global:SNXT.Logfile
        Trace-Verbose ("Process-Mod") $Global:SNXT.Logfile -1
    }
}


$timeInfo = Measure-Command { Process-Mod }
$timeString = Get-FormattedTime $timeInfo
Write-Host ('Process-Mod Time{0}' -f $timeString)
