
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue

function Convert-SND([string] $fullpath, [hashtable] $info)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $fullpath
        $LogTreeFilename = Get-LogTreeFilename $fullpath
        Trace-Debug ('Convert-SND RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        $startTime = Get-Date
    }
    
    Process
    {
        $retValue = @{}
        
        $convert_sound_zappaexe = Get-Utility "convert_sound_zappa.exe"
        $scriptPath = Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "Scripts"
        $convert_sound_zappa = [string] (& $convert_sound_zappaexe $fullpath $scriptPath 2>&1)

        Trace-Verbose ('convert_sound_zappa Output="{0}"' -f $convert_sound_zappa) $LogTreeFilename
        $retValue.Success = $True
        Trace-Debug ('Success Value="{0}"' -f $retValue.Success) $LogTreeFilename
        return $retValue
    }
    
    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-SND-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug 'Convert-SND' $LogTreeFilename -1
    }
}

Export-ModuleMember -Function Convert-SND
