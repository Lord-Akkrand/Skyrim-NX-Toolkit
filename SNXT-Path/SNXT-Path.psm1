
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-DDS\SNXT-DDs.psm1") -Force -WarningAction SilentlyContinue
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Job\SNXT-Job.psm1") -Force -WarningAction SilentlyContinue

$ProgressId = 1

function Open-LogTree([array] $assets)
{
    Begin
    {
        Trace-Verbose ("Open-LogTree") $Global:SNXT.Logfile 1
        $MyProgressId = $ProgressId++
    }

    Process
    {
        # Progress Bar information
        $Activity = "Creating Log Tree"
        $Task = ""
        $assetsLength = $assets.length
        $assetNumber = 0
            
        foreach ($asset in $assets)
        {
            $LogTreeFilename = Get-LogTreeFilename $asset
            $logFilename = Split-Path -Leaf $LogTreeFilename 
            $logPath = Split-Path -Path $LogTreeFilename 

            # Update Progress Bar
            $percentComplete = ($assetNumber++ / $assetsLength) * 100
            Write-Progress -Activity $Activity -Status $logFilename -Id $MyProgressId -PercentComplete $percentComplete

            if (!(Test-Path $logPath))
            {
                $created = $(New-Item $logPath -ItemType Directory)
            }
            $relativeFilename = Get-RelativeFilename $asset
            $created = $(New-Item -Path $logPath -Name $logFilename -Value "" -Force)
            Trace-Verbose ('Create Logfile="{0}"' -f $LogTreeFilename) $Global:SNXT.Logfile
        }
    }

    End
    {
        Trace-Verbose ("Open-LogTree") $Global:SNXT.Logfile -1
    }
}

$ProcessScriptBlock = {
    param($globals, $jobBatch)
    $Global:SNXT = $globals

    $VerbosePreference = 'SilentlyContinue'
    $DebugPreference = 'SilentlyContinue'

    Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath 'SNXT-DDS\SNXT-DDS.psm1') -WarningAction SilentlyContinue
    Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath 'SNXT-Util\SNXT-Util.psm1') -WarningAction SilentlyContinue

    $VerbosePreference = 'Continue'
    $DebugPreference = 'Continue'
    
    $outputHash = @{}
    # Read the texture information
    foreach ($texture in $jobBatch)
    {
        $textureInfo = @{}
        $relativeFilename = Get-RelativeFilename $texture
        $LogTreeFilename = Get-LogTreeFilename $texture

        Trace-Debug ('Process-Texture RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        
        $textureRet = @{}
        # Read the texture information
        $textureRet.Read = Read-DDS $texture $textureInfo 1

        # Change texture format and resize textures
        $textureRet.Compress = Compress-DDS $texture $textureInfo 1

        # Convert DDS to XTX
        $textureRet.Convert = Convert-DDS $texture $textureInfo

        $textureRet.Success = $textureRet.Convert.Success
        
        $outputHash.Add($texture, $textureRet)
        Trace-Debug ('Process-Texture' -f $relativeFilename) $LogTreeFilename -1
    }
    return $outputHash
}
function Convert-Textures([array] $textures)
{
    Begin
    {
        Trace-Verbose ("Convert-Textures") $Global:SNXT.Logfile 1
        $MyProgressId = $ProgressId++
        $JobName = "Convert-DDS"
    }

    Process
    {
        # Progress Bar information
        $Activity = "Queuing Texture Process"
        $Task = ""
        $texturesLength = $textures.length
        $textureNumber = 0
        $batchSize = $Global:SNXT.BatchSize
        if ($batchSize -le 0)
        {
            $batchSize = [int]($texturesLength / (-$batchSize))
        }
        $batchInProgress = [System.Collections.ArrayList]@()
        foreach ($texture in $textures)
        {
            # Update Progress Bar
            $filename = Split-Path -Leaf $texture
            $percentComplete = (++$textureNumber / $texturesLength) * 100
            Write-Progress -Activity $Activity -Status $filename -Id $MyProgressId -PercentComplete $percentComplete

            $batchInProgress += $texture
            if ($batchInProgress.Count -ge $batchSize -or $textureNumber -eq $texturesLength)
            {
                $jobBatch = [System.Collections.ArrayList]@() + $batchInProgress
                
                $task = @{
                    ScriptBlock = $ProcessScriptBlock
                    Arguments = @($Global:SNXT, $jobBatch)
                }

                $batchInProgress = [System.Collections.ArrayList]@()
                Add-JobToQueue $task
            }
        }
        Write-Host ('JobQueued Job="{0}" Count="{1}"' -f $JobName, $textureNumber)
        Submit-Jobs "Textures Processing" $JobName $MyProgressId
    }

    End
    {
        Trace-Verbose ("Convert-Textures") $Global:SNXT.Logfile -1
    }
}

function Convert-Path
{
    Param 
    (
    )

    Begin
    {
        Trace-Debug "Convert-Path" $Global:SNXT.Logfile 1
    }

    Process
    {
        # Get a list of all the files in the path
        $AllTheFiles = Get-ChildItem $Global:SNXT.BasePath -Recurse 

        # Filter it to all the textures
        $textures = $AllTheFiles | Where-Object { $_.Extension -eq ".dds" } | Select-Object -ExpandProperty FullName

        Report-Measure { Open-LogTree $textures } "Open-LogTreeTime"

        Report-Measure { Convert-Textures $textures } "Convert-TexturesTime"
    }

    End
    {
        Trace-Debug ("Convert-Path") $Global:SNXT.Logfile -1
    }
}
