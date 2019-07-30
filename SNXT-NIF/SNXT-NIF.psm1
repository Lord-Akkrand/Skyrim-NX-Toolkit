
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue

function Convert-NIF([string] $fullpath, [hashtable] $info)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $fullpath
        $LogTreeFilename = Get-LogTreeFilename $fullpath
        Trace-Debug ('Convert-NIF RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
    }
    
    Process
    {
        $retValue = @{}
        
        $nswnifoptexe = Get-Utility "nswnifopt.exe"
        
        $removeEditorMarker = ""
        if ($Global:SNXT.Settings.Meshes.RemoveEditorMarker -eq $True) {$removeEditorMarker = "--remove-editor-marker" }

	    $prettySortBlocks = ""
        if ($Global:SNXT.Settings.Meshes.PrettySortBlocks -eq $True) {$prettySortBlocks = "--pretty-sort-blocks" }

	    $trimTexturesPath = ""
        if ($Global:SNXT.Settings.Meshes.TrimTexturesPath -eq $True) {$trimTexturesPath = "--trim-textures-path" }

	    $optimizeForSSE = ""
        if ($Global:SNXT.Settings.Meshes.OptimizeForSSE -eq $True) {$optimizeForSSE = "--optimize-for-sse" }
    
        $nswnifopt = [string] (& $nswnifoptexe -i $fullpath -o $fullpath $removeEditorMarker $prettySortBlocks $trimTexturesPath $optimizeForSSE 2>&1)

        Trace-Verbose ('nswnifopt Output="{0}"' -f $nswnifopt) $LogTreeFilename
        $retValue.Success = $True
        return $retValue
    }
    
    End
    {
        Trace-Debug 'Convert-NIF' $LogTreeFilename -1
    }
}

Export-ModuleMember -Function Convert-NIF
