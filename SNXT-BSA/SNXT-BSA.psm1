
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue


function Unpack-BSAs([string[]] $bsaPaths, [string] $targetPath)
{
    Begin
    {
        Trace-Verbose ('Unpack-BSAs Count="{0}" TargetPath="{1}"' -f $bsaPaths.Count, $targetPath) $Global:SNXT.Logfile 1 
        $bsaarchexe = Get-Utility "bsarch.exe"
        $startTime = Get-Date
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
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Unpack-BSAs-Time{0}' -f $timeString) $Global:SNXT.Logfile
        Trace-Verbose 'Unpack-BSAs' $Global:SNXT.Logfile -1
    }
}

function Remove-NoESP([string[]] $espFiles, [string] $targetPath)
{
    Begin
    {
        Trace-Verbose ('Remove-ESP Count="{0}" TargetPath="{1}"' -f $espFiles.Count, $targetPath) $Global:SNXT.Logfile 1 
        $startTime = Get-Date
    }
    
    Process
    {
        Trace-Verbose ('WARNING ThisFunctionIsPlaceholder="ItDoesNotWorkYet"') $Global:SNXT.Logfile
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Remove-ESP-Time{0}' -f $timeString) $Global:SNXT.Logfile
        Trace-Verbose 'Remove-ESP' $Global:SNXT.Logfile -1
    }
}

function Copy-Loose($allTheFiles, [string] $originPath, [string] $targetPath)
{
    Begin
    {
        Trace-Verbose ('Copy-Loose FileCount="{0}" TargetPath="{1}"' -f $allTheFiles.Count, $targetPath) $Global:SNXT.Logfile 1 
        $startTime = Get-Date
    }
    
    Process
    {
        Trace-Verbose ('Candidates FileCount="{0}"' -f $copyCandidates.Count) $Global:SNXT.Logfile
        $pluginFiles = $allTheFiles | Where-Object { !($_.PSIsContainer) -and ($_.Extension -eq ".esp" -or $_.Extension -eq ".esm" -or $_.Extension -eq ".esl") } | Select-Object -ExpandProperty Name
        $pluginFolders = $allTheFiles | Where-Object { ($_.PSIsContainer) -and ($_.Extension -eq ".esp" -or $_.Extension -eq ".esm" -or $_.Extension -eq ".esl") } | Select-Object -ExpandProperty FullName
        Trace-Verbose ('Plugins FileCount="{0}"' -f $pluginFiles.Count) $Global:SNXT.Logfile
        $pluginRegexes = [System.Collections.ArrayList]@()
        foreach ($pluginFile in $pluginFiles)
        {
            $pluginRegexes += $pluginFile.ToLower()
        }
        $pluginRegexes += "skyrim.esm"
        $pluginRegexes += "dawnguard.esm"
        $pluginRegexes += "hearthfires.esm"
        $pluginRegexes += "dragonborn.esm"
        Trace-Verbose ('PluginRegexes') $Global:SNXT.Logfile 1
        $skipPluginFolders = $pluginFolders | Where-Object { 
            $leaf = Split-Path -Path $_ -Leaf
            return !($pluginRegexes.Contains($leaf.ToLower())) 
        }
       
        $skipLeaves = $skipPluginFolders | Split-Path -Leaf | Select-Object -Unique
        Trace-Verbose ('SkipPlugins') $Global:SNXT.Logfile 1
        $skippedRegexes = [System.Collections.ArrayList]@()
        foreach ($pluginFolder in $skipLeaves)
        {
            Trace-Verbose ('SkipPlugin Directory="{0}"' -f $pluginFolder) $Global:SNXT.Logfile
            $skippedRegexes += ('*{0}*' -f $pluginFolder)
        }
        Trace-Verbose ('SkipPlugins') $Global:SNXT.Logfile -1
        
        $copyCandidates = $allTheFiles | Where-Object { $_.Extension -ne ".bsa" -and !($_.PSIsContainer) } | Select-Object -ExpandProperty FullName
        $copyLength = $copyCandidates.Count
        $assetNumber = 0
        $copied = 0
        $skipped = 0
        $Activity = "Copy Pristine Files"
        $MyProgressId = 1
        
        foreach ($item in $copyCandidates)
        {
            $relativeFilename = Get-RelativeFilename $item $originPath
            $relativePathname = Get-RelativeFilename (Split-Path $item) $originPath
            $allowCopy = $True
            foreach ($skippedRegex in $skippedRegexes)
            {
                if ($relativeFilename -like $skippedRegex)
                {
                    $allowCopy = $False
                }
            }
            
            if ($allowCopy)
            {
                $target = Join-Path -Path $targetPath -ChildPath $relativeFilename
                $filePath = Split-Path $target
                if (!(Test-Path $filePath))
                {
                    #Trace-Verbose ('Create Path="{0}"' -f $filePath) $Global:SNXT.Logfile
                    $created = $(New-Item $filePath -ItemType Directory)
                }
                #Trace-Verbose ('Copy Origin="{0}" Target="{1}"' -f $item, $target) $Global:SNXT.Logfile
                Copy-Item -Path $item -Destination $filePath -Force
                $copied += 1
            }
            else {
                #Trace-Verbose ('Not copying {0} because no plugins are present for it' -f $relativeFilename) $Global:SNXT.Logfile
                $skipped += 1
            }
            # Update Progress Bar
            $percentComplete = ($assetNumber++ / $copyLength) * 100
            $status = ('Total Files {0} Copied {1} Skipped {2} CurrentFile [{3}]' -f $copyLength, $copied, $skipped, $relativeFilename)
            Write-Progress -Activity $Activity -Status $status -Id $MyProgressId -PercentComplete $percentComplete
        }
        Trace-Verbose ('CopyStatus TotalFiles="{0}" Copied="{1}" Skipped="{2}"' -f $copyLength, $copied, $skipped) $Global:SNXT.Logfile
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Copy-Loose-Time{0}' -f $timeString) $Global:SNXT.Logfile
        Trace-Verbose 'Copy-Loose' $Global:SNXT.Logfile -1
    }
}

function Unpack-Mod([string] $pristinePath, [string] $convertedPath)
{
    Begin
    {
        Trace-Verbose ('Unpack-Mod Pristine="{0}" Converted="{1}"' -f $pristinePath, $convertedPath) $Global:SNXT.Logfile 1 
        $startTime = Get-Date
    }
    
    Process
    {
        # Get a list of all the files in the path
        $AllTheFiles = Get-ChildItem $pristinePath -Recurse 
        $LocalFiles = Get-ChildItem $pristinePath
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

        Copy-Loose $AllTheFiles $pristinePath $convertedPath
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Unpack-Mod-Time{0}' -f $timeString) $Global:SNXT.Logfile
        Trace-Verbose 'Unpack-Mod' $Global:SNXT.Logfile -1
    }
}

Export-ModuleMember -Function Unpack-Mod
