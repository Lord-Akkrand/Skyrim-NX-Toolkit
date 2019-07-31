
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue

function Convert-NIF([string] $fullpath, [hashtable] $info)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $fullpath
        $LogTreeFilename = Get-LogTreeFilename $fullpath
        Trace-Debug ('Convert-NIF RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        $startTime = Get-Date
    }
    
    Process
    {
        $retValue = @{}
        
        $nswnifoptexe = Get-Utility "nswnifopt.exe"
        
        $removeEditorMarker = ""
        if ($Global:SNXT.Config.Meshes.RemoveEditorMarker -eq $True) {$removeEditorMarker = "--remove-editor-marker" }

	    $prettySortBlocks = ""
        if ($Global:SNXT.Config.Meshes.PrettySortBlocks -eq $True) {$prettySortBlocks = "--pretty-sort-blocks" }

	    $trimTexturesPath = ""
        if ($Global:SNXT.Config.Meshes.TrimTexturesPath -eq $True) {$trimTexturesPath = "--trim-textures-path" }

	    $optimizeForSSE = ""
        if ($Global:SNXT.Config.Meshes.OptimizeForSSE -eq $True) {$optimizeForSSE = "--optimize-for-sse" }
    
        Trace-Verbose ('nswnifopt CommandLine="{0}"' -f ("{0} -i {1} -o {1} {2} {3} {4} {5}" -f $nswnifoptexe, $fullpath, $removeEditorMarker, $prettySortBlocks, $trimTexturesPath, $optimizeForSSE)) $LogTreeFilename
        $nswnifopt = [string] (& $nswnifoptexe -i $fullpath -o $fullpath $removeEditorMarker $prettySortBlocks $trimTexturesPath $optimizeForSSE 2>&1)

        Trace-Verbose ('nswnifopt Output="{0}"' -f $nswnifopt) $LogTreeFilename
        $retValue.Success = $True
        Trace-Debug ('Success Value="{0}"' -f $retValue.Success) $LogTreeFilename
        return $retValue
    }
    
    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-NIF-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug 'Convert-NIF' $LogTreeFilename -1
    }
}

Export-ModuleMember -Function Convert-NIF
