
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue


function Unpack-BSAs([string[]] $bsaPaths, [string] $targetPath)
{
    Begin
    {
        Trace-Verbose ('Unpack-BSAs Count="{0}" TargetPath="{1}"' -f $bsaPaths.Count, $targetPath) $Global:SNXT.Logfile 1 
        $bsaarchexe = Get-Utility "bsarch.exe"
    }
    
    Process
    {
        Trace-Verbose ('BSAList') $Global:SNXT.Logfile 1
        foreach ($bsaFile in $bsaFiles)
        {
            Trace-Verbose ('Unpack-BSA File="{0}"' -f $bsaFile) $Global:SNXT.Logfile 1
            $bsarch = [string[]] (& $bsaarchexe unpack $bsaFile $targetPath 2>&1)
            $bsarch = $bsarch -replace '"', "'"
            foreach ($line in $bsarch)
            {
                Trace-Verbose ('bsarch Output="{0}"' -f $line) $Global:SNXT.Logfile
            }

            Trace-Verbose ('Unpack-BSA' -f $bsaFile) $Global:SNXT.Logfile -1
        }
        Trace-Verbose ('BSAList') $Global:SNXT.Logfile -1
    }

    End
    {
        Trace-Verbose 'Unpack-BSAs' $Global:SNXT.Logfile -1
    }
}

function Remove-NoESP([string[]] $espFiles, [string] $targetPath)
{
    Begin
    {
        Trace-Verbose ('Remove-ESP Count="{0}" TargetPath="{1}"' -f $espFiles.Count, $targetPath) $Global:SNXT.Logfile 1 
    }
    
    Process
    {
        
    }

    End
    {
        Trace-Verbose 'Remove-ESP' $Global:SNXT.Logfile -1
    }
}

function Copy-Loose([string[]] $allTheFiles, [string] $targetPath)
{
    Begin
    {
        Trace-Verbose ('Copy-Loose FileCount="{0}" TargetPath="{1}"' -f $allTheFiles.Count, $targetPath) $Global:SNXT.Logfile 1 
    }
    
    Process
    {
        $copyCandidates = $copyCandidates | Where { $_.Extension -ne ".bsa" -and !($_.PSIsContainer) } | Select-Object -ExpandProperty FullName
        $pluginFiles = $copyCandidates | Where { $_.Extension -eq ".esp" -or $_.Extension -eq ".esm" -or $_.Extension -eq ".esl" } | Select-Object -ExpandProperty Name
        $pluginRegexes = [System.Collections.ArrayList]@()
        foreach ($pluginFile in $pluginFiles)
        {
            $pluginRegexes += ('*{0}*' -f $pluginFile)
        }
        $pluginRegexes += "*skyrim.esm*"
        $pluginRegexes += "*dawnguard.esm*"
        $pluginRegexes += "*hearthfires.esm*"
        $pluginRegexes += "*dragonborn.esm*"
        
        foreach ($item in $copyCandidates)
        {
            $relativeFilename = Get-RelativeFilename $item
            $allowCopy = $True
            if ($relativeFilename -like "*.esp*" -or $relativeFilename -like "*.esm*" -or $relativeFilename -like "*.esl*")
            {
                $allowCopy = $False
                foreach ($pluginRegex in $pluginRegexes)
                {
                    if ($relativeFilename -like $pluginRegex)
                    {
                        $allowCopy = $True
                        break
                    }
                }
            }
            if ($allowCopy)
            {
                $target = Join-Path -Path $targetPath -ChildPath $relativeFilename
                $relativeTarget = Get-RelativeFilename $target
                Trace-Verbose ('Copy Origin="{0}" Target="{1}"' -f $relativeFilename, $relativeTarget) $Global:SNXT.Logfile
                Copy-Item -Path $item -Destination $target -Recurse
            }
            else {
                Write-Host ('Not copying {0} because no plugins are present for it' -f $relativeFilename)
            }
        }
    }

    End
    {
        Trace-Verbose 'Copy-Loose' $Global:SNXT.Logfile -1
    }
}

function Unpack-Mod([string] $pristinePath, [string] $convertedPath)
{
    Begin
    {
        Trace-Verbose ('Unpack-Mod Pristine="{0}" Converted="{0}"' -f $pristinePath, $convertedPath) $Global:SNXT.Logfile 1 
    }
    
    Process
    {
        # Get a list of all the files in the path
        $AllTheFiles = Get-ChildItem $convertedPath -Recurse 
        $LocalFiles = Get-ChildItem $convertedPath
        # Filter it to all the textures
        $looseFiles = $LocalFiles | Where { $_.Extension -ne ".bsa" -and !($_.PSIsContainer) } | Select-Object -ExpandProperty FullName
        $looseDirectories = $LocalFiles | Where { $_.PSIsContainer } | Select-Object -ExpandProperty FullName

        $pluginFiles = $AllTheFiles | Where { $_.Extension -eq ".esp" -or $_.Extension -eq ".esm" -or $_.Extension -eq ".esl" } | Select-Object -ExpandProperty FullName
        
        $bsaFiles = $AllTheFiles | Where { $_.Extension -eq ".bsa" } | Select-Object -ExpandProperty FullName
        Trace-Verbose ('BSAs Count="{0}"' -f $bsaFiles.Count) $Global:SNXT.Logfile
        if ($bsaFiles.Count -gt 0)
        {
            Unpack-BSAs $bsaFiles $pristinePath $convertedPath
            Remove-NoESP $pluginFiles $convertedPath 
        }

        Copy-Loose $AllTheFiles $convertedPath
    }

    End
    {
        Trace-Verbose 'Unpack-Mod' $Global:SNXT.Logfile -1
    }
}

Export-ModuleMember -Function Unpack-Mod
