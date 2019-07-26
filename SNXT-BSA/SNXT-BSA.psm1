
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

function Stash-Loose([string[]] $files, [string[]] $directories, [string] $targetPath)
{
    Begin
    {
        Trace-Verbose ('Stash-Loose FileCount="{0}" DirectoryCount="{1}" TargetPath="{2}"' -f $files.Count, $directories.Count, $targetPath) $Global:SNXT.Logfile 1 
        $bsaarchexe = Get-Utility "bsarch.exe"
    }
    
    Process
    {
        $stashPath = Join-Path -Path $targetPath -ChildPath "LooseStash"
        $created = $(New-Item $stashPath -ItemType Directory)

        $allItems = [array]$files + $directories
        foreach ($item in $allItems)
        {
            $relativeFilename = Get-RelativeFilename $item
            $target = Join-Path -Path $stashPath -ChildPath $relativeFilename
            $relativeTarget = Get-RelativeFilename $target
            Trace-Verbose ('Stash Origin="{0}" Target="{1}"' -f $relativeFilename, $relativeTarget) $Global:SNXT.Logfile
            Move-Item -Path $item -Destination $target
        }
    }

    End
    {
        Trace-Verbose 'Stash-Loose' $Global:SNXT.Logfile -1
    }
}

function Restore-Stash([string] $targetPath)
{
    Begin
    {
        Trace-Verbose ('Restore-Stash') $Global:SNXT.Logfile 1 
    }
    
    Process
    {
        $stashPath = Join-Path -Path $targetPath -ChildPath "LooseStash"
        $originPath = ("{0}{1}*" -f $stashPath, [IO.Path]::DirectorySeparatorChar)
        Trace-Verbose ('Origin Path="{0}"' -f $originPath) $Global:SNXT.Logfile
        Trace-Verbose ('Target Path="{0}"' -f $targetPath) $Global:SNXT.Logfile
        $AllTheItems = Get-ChildItem $originPath -Recurse 
        $allTheFiles = $AllTheItems | Where { !($_.PSIsContainer) } | Select-Object -ExpandProperty FullName
        foreach ($file in $allTheFiles)
        {
            $target = $file.Replace($stashPath, $targetPath)
            Trace-Verbose ('Move Origin="{0}" Target="{1}"' -f (Get-RelativeFilename $file), (Get-RelativeFilename $target)) $Global:SNXT.Logfile
            Move-Item -Path $file -Destination $target -Force
        }
        Remove-Item $stashPath -Force -Recurse
    }

    End
    {
        Trace-Verbose 'Restore-Stash' $Global:SNXT.Logfile -1
    }
}

function Unpack-Mod([string] $modPath)
{
    Begin
    {
        Trace-Verbose ('Unpack-Mod Path="{0}"' -f $modPath) $Global:SNXT.Logfile 1 
    }
    
    Process
    {
        # Get a list of all the files in the path
        $AllTheFiles = Get-ChildItem $modPath -Recurse 
        $LocalFiles = Get-ChildItem $modPath
        # Filter it to all the textures
        $looseFiles = $LocalFiles | Where { $_.Extension -ne ".bsa" -and !($_.PSIsContainer) } | Select-Object -ExpandProperty FullName
        $looseDirectories = $LocalFiles | Where { $_.PSIsContainer } | Select-Object -ExpandProperty FullName
        
        $bsaFiles = $AllTheFiles | Where { $_.Extension -eq ".bsa" } | Select-Object -ExpandProperty FullName
        $hasBSAs = $bsaFiles.Count -gt 0
        Trace-Verbose ('HasBSAs Value="{0}"' -f $hasBSAs) $Global:SNXT.Logfile
        if ($hasBSAs)
        {
            Report-Measure { Stash-Loose $looseFiles $looseDirectories $modPath } "Stash-Loose"

            Report-Measure { Unpack-BSAs $bsaFiles $modPath } "Unpack-BSAs"

            Report-Measure { Restore-Stash $modPath } "Restore-Stash"
        }
        

        $pluginFiles = $AllTheFiles | Where { $_.Extension -eq ".esp" -or $_.Extension -eq ".esm" -or $_.Extension -eq ".esl" } | Select-Object -ExpandProperty FullName
    }

    End
    {
        Trace-Verbose 'Unpack-Mod' $Global:SNXT.Logfile -1
    }
}

Export-ModuleMember -Function Unpack-BSA, Unpack-Mod
