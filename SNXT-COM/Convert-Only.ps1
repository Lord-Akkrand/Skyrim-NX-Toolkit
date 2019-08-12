param
(
    [String]$ModPath=""
)

Clear-Host

$ErrorActionPreference = 'Stop'

if ($ModPath -eq "")
{
    Write-Host ('Usage')
    Write-Host ('PS_CONVERT_ONLY "<ModPath>"')
    Write-Host ('Example:')
    Write-Host ('PS_CONVERT_ONLY "C:\Skyrim Switch\Skyrim-NX-Toolkit\Inigo"')
    return
}

$Global:SNXT = @{}
$Global:SNXT.HomeLocation = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Write-Host ("Global:SNXT.HomeLocation [{0}]" -f $Global:SNXT.HomeLocation)
Write-Host ("ModPath [{0}]" -f $ModPath)
$ModName = Split-Path -Leaf $ModPath
Write-Host ("ModName [{0}]" -f $ModName)

Push-Location $Global:SNXT.HomeLocation
$VerbosePreference = 'SilentlyContinue'
$DebugPreference = 'SilentlyContinue'

Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Path\SNXT-Path.psm1") -Force -WarningAction SilentlyContinue
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-BSA\SNXT-BSA.psm1") -Force -WarningAction SilentlyContinue
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Job\SNXT-Job.psm1") -Force -WarningAction SilentlyContinue

Get-ExternalUtilites

$Global:SNXT.BasePath = $ModPath + "_Processed"

Write-Host ("BasePath [{0}]" -f $Global:SNXT.BasePath)

Set-Config

function Convert-Mod
{
    Begin
    {
        $startTime = Get-Date
        Create-Empty $Global:SNXT.BasePath
        Create-LogTree $ModName
        Trace-Verbose ("Convert-Mod") $Global:SNXT.Logfile 1
    }

    Process
    {
        Unpack-Mod $ModPath $Global:SNXT.BasePath
        Convert-Path
    }
    
    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-Mod-Time{0}' -f $timeString) $Global:SNXT.Logfile
        Trace-Verbose ("Convert-Mod") $Global:SNXT.Logfile -1
        Write-Host ('Convert-Mod Time{0}' -f $timeString)
    }
}

Convert-Mod
