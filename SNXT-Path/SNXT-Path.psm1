
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
        $startTime = Get-Date
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
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Open-LogTree-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Verbose ("Open-LogTree") $Global:SNXT.Logfile -1
    }
}

$ProcessDDSScriptBlock = {
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
        
        Trace-Verbose ('SNXT ToolkitVersion="{0}"' -f $Global:SNXT.Config.Version.ToolkitVersion) $LogTreeFilename

        $textureRet = @{}
        # Read the texture information
        $textureRet.Read = Read-DDS $texture $textureInfo 1

        if ($textureInfo.SKU -eq "NX")
        {
            $textureRet['Skipped'] = $True
        }
        else
        {
            # Change texture format and resize textures
            $textureRet.Compress = Compress-DDS $texture $textureInfo 1

            # Convert DDS to XTX
            $textureRet.Convert = Convert-DDS $texture $textureInfo

            $textureRet.Success = $textureRet.Convert.Success
        }
        $outputHash.Add($texture, $textureRet)
        Trace-Debug ('Process-Texture' -f $relativeFilename) $LogTreeFilename -1
    }
    return $outputHash
}
function Convert-Textures([array] $textures)
{
    Begin
    {
        Trace-Verbose ("Convert-DDSs") $Global:SNXT.Logfile 1
        $MyProgressId = $ProgressId++
        $JobName = "Convert-DDS"
        $startTime = Get-Date
    }

    Process
    {
        # Progress Bar information
        $Activity = "Queuing Texture Process"
        $Task = ""
        $texturesLength = $textures.length
        $textureNumber = 0
        $batchSize = Get-BatchSize $texturesLength

        $batchInProgress = [System.Collections.ArrayList]@()
        $batchCount = 0
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
                    ScriptBlock = $ProcessDDSScriptBlock
                    Arguments = @($Global:SNXT, $jobBatch)
                }

                $batchInProgress = [System.Collections.ArrayList]@()
                Add-JobToQueue $task
                $batchCount += 1
                Write-Host ('Batch Queued Job="{0}" Assets="{1}"' -f $JobName, $jobBatch.Count)
            }
        }
        Write-Host ('Jobs Queued Job="{0}" Batches="{1}"' -f $JobName, $batchCount)
        Submit-Jobs "Textures Processing" $JobName $MyProgressId
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-DDSs-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Verbose ("Convert-DDS") $Global:SNXT.Logfile -1
    }
}

$ProcessHKXScriptBlock = {
    param($globals, [System.Collections.ArrayList]$jobBatch)
    $Global:SNXT = $globals

    $VerbosePreference = 'SilentlyContinue'
    $DebugPreference = 'SilentlyContinue'

    Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath 'SNXT-HKX\SNXT-HKX.psm1') -Force -WarningAction SilentlyContinue
    Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath 'SNXT-Util\SNXT-Util.psm1') -WarningAction SilentlyContinue

    $VerbosePreference = 'Continue'
    $DebugPreference = 'Continue'
    
    $outputHash = @{}
    # Read the asset information
    foreach ($asset in $jobBatch)
    {
        $assetInfo = @{}
        $relativeFilename = Get-RelativeFilename $asset
        $LogTreeFilename = Get-LogTreeFilename $asset

        Trace-Debug ('Process-HKX RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        
        Trace-Verbose ('SNXT ToolkitVersion="{0}"' -f $Global:SNXT.Config.Version.ToolkitVersion) $LogTreeFilename

        $assetRet = @{}
        # Read the asset information
        $assetRet.Read = Read-HKX $asset $assetInfo

        if ($assetInfo.Type -eq "NX_64")
        {
            # This has already been converted, don't do it again.
            $assetRet['Skipped'] = $True
        }
        else
        {
            if ($assetInfo.Type -eq "PC_32" -or $assetInfo.Type -eq "PC_XML")
            {
                # Attempt 32-bit conversion
                $assetRet.Convert = Convert-HKX32 $asset $assetInfo
            }
            elseif ($assetInfo.Type -eq "PC_64")
            {
                # Attempt 64-bit conversion
                $assetRet.Convert = Convert-HKX64 $asset $assetInfo
            }

            $assetRet['Success'] = $assetRet.Convert['Success']
        }
       
        $outputHash.Add($asset, $assetRet)
        Trace-Debug ('Process-HKX' -f $relativeFilename) $LogTreeFilename -1
    }
    return $outputHash
}
function Convert-HKXs([array] $assets)
{
    Begin
    {
        Trace-Verbose ("Convert-HKXs") $Global:SNXT.Logfile 1
        $MyProgressId = $ProgressId++
        $JobName = "Convert-HKX"
        $startTime = Get-Date
    }

    Process
    {
        # Progress Bar information
        $Activity = "Queuing HKX Process"
        $Task = ""
        $assetsLength = $assets.length
        $assetNumber = 0
        $batchSize = Get-BatchSize $assetsLength

        $batchInProgress = [System.Collections.ArrayList]@()
        $batchCount = 0
        foreach ($asset in $assets)
        {
            # Update Progress Bar
            $filename = Split-Path -Leaf $asset
            $percentComplete = (++$assetNumber / $assetsLength) * 100
            Write-Progress -Activity $Activity -Status $filename -Id $MyProgressId -PercentComplete $percentComplete

            $batchInProgress += $asset
            if ($batchInProgress.Count -ge $batchSize -or $assetNumber -eq $assetsLength)
            {
                $jobBatch = [System.Collections.ArrayList]@() + $batchInProgress
                
                $task = @{
                    ScriptBlock = $ProcessHKXScriptBlock
                    Arguments = @($Global:SNXT, $jobBatch)
                }

                $batchInProgress = [System.Collections.ArrayList]@()
                Add-JobToQueue $task

                $batchCount += 1
                Write-Host ('Batch Queued Job="{0}" Assets="{1}"' -f $JobName, $jobBatch.Count)
            }
        }
        Write-Host ('Jobs Queued Job="{0}" Batches="{1}"' -f $JobName, $batchCount)
        Submit-Jobs "HKX Processing" $JobName $MyProgressId
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-HKXs-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Verbose ("Convert-HKXs") $Global:SNXT.Logfile -1
    }
}

$ProcessNIFScriptBlock = {
    param($globals, [System.Collections.ArrayList]$jobBatch)
    $Global:SNXT = $globals

    $VerbosePreference = 'SilentlyContinue'
    $DebugPreference = 'SilentlyContinue'

    Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath 'SNXT-NIF\SNXT-NIF.psm1') -Force -WarningAction SilentlyContinue
    Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath 'SNXT-Util\SNXT-Util.psm1') -WarningAction SilentlyContinue

    $VerbosePreference = 'Continue'
    $DebugPreference = 'Continue'
    
    $outputHash = @{}
    # Read the asset information
    foreach ($asset in $jobBatch)
    {
        $assetInfo = @{}
        $relativeFilename = Get-RelativeFilename $asset
        $LogTreeFilename = Get-LogTreeFilename $asset

        Trace-Debug ('Process-NIF RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        
        Trace-Verbose ('SNXT ToolkitVersion="{0}"' -f $Global:SNXT.Config.Version.ToolkitVersion) $LogTreeFilename

        $assetRet = @{}
        # Read the asset information
        $assetRet.Convert = Convert-NIF $asset $assetInfo

        $assetRet['Success'] = $assetRet.Convert['Success']
       
        $outputHash.Add($asset, $assetRet)
        Trace-Debug ('Process-NIF' -f $relativeFilename) $LogTreeFilename -1
    }
    return $outputHash
}
function Convert-NIFs([array] $assets)
{
    Begin
    {
        Trace-Verbose ("Convert-NIFs") $Global:SNXT.Logfile 1
        $MyProgressId = $ProgressId++
        $JobName = "Convert-NIF"
        $startTime = Get-Date
    }

    Process
    {
        # Progress Bar information
        $Activity = "Queuing NIF Process"
        $Task = ""
        $assetsLength = $assets.length
        $assetNumber = 0
        $batchSize = Get-BatchSize $assetsLength
        
        $batchInProgress = [System.Collections.ArrayList]@()
        $batchCount = 0
        foreach ($asset in $assets)
        {
            # Update Progress Bar
            $filename = Split-Path -Leaf $asset
            $percentComplete = (++$assetNumber / $assetsLength) * 100
            Write-Progress -Activity $Activity -Status $filename -Id $MyProgressId -PercentComplete $percentComplete

            $batchInProgress += $asset
            if ($batchInProgress.Count -ge $batchSize -or $assetNumber -eq $assetsLength)
            {
                $jobBatch = [System.Collections.ArrayList]@() + $batchInProgress
                
                $task = @{
                    ScriptBlock = $ProcessNIFScriptBlock
                    Arguments = @($Global:SNXT, $jobBatch)
                }

                $batchInProgress = [System.Collections.ArrayList]@()
                Add-JobToQueue $task

                $batchCount += 1
                Write-Host ('Batch Queued Job="{0}" Assets="{1}"' -f $JobName, $jobBatch.Count)
            }
        }
        Write-Host ('Jobs Queued Job="{0}" Batches="{1}"' -f $JobName, $batchCount)
        Submit-Jobs "NIF Processing" $JobName $MyProgressId
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-NIFs-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Verbose ("Convert-NIFs") $Global:SNXT.Logfile -1
    }
}

function Convert-Path
{
    Param 
    (
    )

    Begin
    {
        Trace-Verbose "Convert-Path" $Global:SNXT.Logfile 1
    }

    Process
    {
        # Get a list of all the files in the path
        $AllTheFiles = Get-ChildItem $Global:SNXT.BasePath -Recurse 

        # Filter it to all the textures
        [array]$allAssets = @()
        $textures = $AllTheFiles | Where-Object { $_.Extension -eq ".dds" } | Select-Object -ExpandProperty FullName
        $allAssets += $textures
        $hkxs = $AllTheFiles | Where-Object { $_.Extension -eq ".hkx" } | Select-Object -ExpandProperty FullName
        $allAssets += $hkxs
        $nifs = $AllTheFiles | Where-Object { $_.Extension -eq ".nif" } | Select-Object -ExpandProperty FullName
        $allAssets += $nifs
        
        Open-LogTree $allAssets

        Convert-Textures $textures

        Convert-HKXs $hkxs

        Convert-NIFs $nifs
    }

    End
    {
        Trace-Verbose ("Convert-Path") $Global:SNXT.Logfile -1
    }
}
