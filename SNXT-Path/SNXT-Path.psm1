﻿
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

            #Trace-Verbose ('Create Logfile="{0}"' -f $LogTreeFilename) $Global:SNXT.Logfile
            $created = $(New-Item -Path $logPath -Name $logFilename -Value "" -Force)
        }
        Trace-Verbose ('Created LogfileCount="{0}"' -f $assetsLength) $Global:SNXT.Logfile
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Open-LogTree-Time{0}' -f $timeString) $Global:SNXT.Logfile
        Trace-Verbose ("Open-LogTree") $Global:SNXT.Logfile -1
        Write-Host ('Open-LogTree Time{0}' -f $timeString)
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

    # Read the texture information
    foreach ($texture in $jobBatch)
    {
        $startTime = Get-Date
        $textureInfo = @{}
        $relativeFilename = Get-RelativeFilename $texture
        $LogTreeFilename = Get-LogTreeFilename $texture

        Trace-Debug ('Process-DDS RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1

        Trace-Verbose ('SNXT ToolkitVersion="{0}"' -f $Global:SNXT.Config.Version.ToolkitVersion) $LogTreeFilename

        $textureRet = @{}
        $textureRet.AssetName = $texture
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
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Debug ('Process-DDS-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug ('Process-DDS' -f $relativeFilename) $LogTreeFilename -1
        $textureRet
    }
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
                #Write-Host ('Batch {0} Queued Job="{1}" Assets="{2}"' -f $batchCount, $JobName, $jobBatch.Count)
            }
        }
        Submit-Jobs "Textures Processing" $JobName $MyProgressId $texturesLength
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-DDSs-Time{0}' -f $timeString) $Global:SNXT.Logfile
        Trace-Verbose ("Convert-DDSs") $Global:SNXT.Logfile -1
        Write-Host ('Convert-DDSs Time{0}' -f $timeString)
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

    # Read the asset information
    foreach ($asset in $jobBatch)
    {
        $startTime = Get-Date
        $assetInfo = @{}
        $relativeFilename = Get-RelativeFilename $asset
        $LogTreeFilename = Get-LogTreeFilename $asset

        Trace-Debug ('Process-HKX RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1

        Trace-Verbose ('SNXT ToolkitVersion="{0}"' -f $Global:SNXT.Config.Version.ToolkitVersion) $LogTreeFilename

        $assetRet = @{}
        $assetRet.AssetName = $asset
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

        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Debug ('Process-HKX-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug ('Process-HKX' -f $relativeFilename) $LogTreeFilename -1
        $assetRet
    }
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
                #Write-Host ('Batch {0} Queued Job="{1}" Assets="{2}"' -f $batchCount, $JobName, $jobBatch.Count)
            }
        }
        Submit-Jobs "HKX Processing" $JobName $MyProgressId $assetsLength
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-HKXs-Time{0}' -f $timeString) $Global:SNXT.Logfile
        Trace-Verbose ("Convert-HKXs") $Global:SNXT.Logfile -1
        Write-Host ('Convert-HKXs Time{0}' -f $timeString)
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

    # Read the asset information
    foreach ($asset in $jobBatch)
    {
        $startTime = Get-Date
        $assetInfo = @{}
        $relativeFilename = Get-RelativeFilename $asset
        $LogTreeFilename = Get-LogTreeFilename $asset

        Trace-Debug ('Process-NIF RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1

        Trace-Verbose ('SNXT ToolkitVersion="{0}"' -f $Global:SNXT.Config.Version.ToolkitVersion) $LogTreeFilename

        $assetRet = @{}
        $assetRet.AssetName = $asset
        # Read the asset information
        $assetRet.Convert = Convert-NIF $asset $assetInfo

        $assetRet['Success'] = $assetRet.Convert['Success']

        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Debug ('Process-NIF-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug ('Process-NIF' -f $relativeFilename) $LogTreeFilename -1
        $assetRet
    }
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
                #Write-Host ('Batch {0} Queued Job="{1}" Assets="{2}"' -f $batchCount, $JobName, $jobBatch.Count)
            }
        }
        Submit-Jobs "NIF Processing" $JobName $MyProgressId $assetsLength
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-NIFs-Time{0}' -f $timeString) $Global:SNXT.Logfile
        Trace-Verbose ("Convert-NIFs") $Global:SNXT.Logfile -1
        Write-Host ('Convert-NIFs Time{0}' -f $timeString)
    }
}

$ProcessSNDScriptBlock = {
    param($globals, [System.Collections.ArrayList]$jobBatch)
    $Global:SNXT = $globals

    $VerbosePreference = 'SilentlyContinue'
    $DebugPreference = 'SilentlyContinue'

    Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath 'SNXT-SND\SNXT-SND.psm1') -Force -WarningAction SilentlyContinue
    Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath 'SNXT-Util\SNXT-Util.psm1') -WarningAction SilentlyContinue

    $VerbosePreference = 'Continue'
    $DebugPreference = 'Continue'

    # Read the asset information
    foreach ($asset in $jobBatch)
    {
        $startTime = Get-Date
        $assetInfo = @{}
        $relativeFilename = Get-RelativeFilename $asset
        $LogTreeFilename = Get-LogTreeFilename $asset

        Trace-Debug ('Process-SND RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1

        Trace-Verbose ('SNXT ToolkitVersion="{0}"' -f $Global:SNXT.Config.Version.ToolkitVersion) $LogTreeFilename

        $assetRet = @{}
        $assetRet.AssetName = $asset
        # Read the asset information
        $assetRet.Convert = Convert-SND $asset $assetInfo

        $assetRet['Success'] = $assetRet.Convert['Success']
        $assetRet['Skipped'] = $assetRet.Convert['Skipped']

        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Debug ('Process-SND-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug ('Process-SND' -f $relativeFilename) $LogTreeFilename -1
        $assetRet
    }
}
function Convert-SNDs([array] $assets)
{
    Begin
    {
        Trace-Verbose ("Convert-SNDs") $Global:SNXT.Logfile 1
        $MyProgressId = $ProgressId++
        $JobName = "Convert-SND"
        $startTime = Get-Date
    }

    Process
    {
        # Progress Bar information
        $Activity = "Queuing SND Process"
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
                    ScriptBlock = $ProcessSNDScriptBlock
                    Arguments = @($Global:SNXT, $jobBatch)
                }

                $batchInProgress = [System.Collections.ArrayList]@()
                Add-JobToQueue $task

                $batchCount += 1
                #Write-Host ('Batch {0} Queued Job="{1}" Assets="{2}"' -f $batchCount, $JobName, $jobBatch.Count)
            }
        }
        Submit-Jobs "SND Processing" $JobName $MyProgressId $assetsLength
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-SNDs-Time{0}' -f $timeString) $Global:SNXT.Logfile
        Trace-Verbose ("Convert-SNDs") $Global:SNXT.Logfile -1
        Write-Host ('Convert-SNDs Time{0}' -f $timeString)
    }
}

function Get-SoundList([array] $allSounds)
{
    $sndsHash = @{}
    $assetNumber = 0
    $assetsLength = $allSounds.Count
    $MyProgressId = $ProgressId++
    $Activity = "Determining Sound List"
    $count = 0
    foreach ($sndfile in $allSounds)
    {
        $sndFileWExt = $sndFile.Substring(0, ($sndFile.length-4))

        if ($sndsHash.ContainsKey($sndFileWExt) -eq $False)
        {
            $sndsHash.Add($sndFileWExt, $True)
            $count += 1
        }
        $filename = ('Current File [{0}] Sound Files: {1}' -f (Split-Path -Leaf $sndfile), $count)
        $percentComplete = (++$assetNumber / $assetsLength) * 100
        Write-Progress -Activity $Activity -Status $filename -Id $MyProgressId -PercentComplete $percentComplete
    }
    return $sndsHash.Keys
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
        $allSounds = $AllTheFiles | Where-Object { $_.Extension -eq ".xwm" -or $_.Extension -eq ".fuz" -or $_.Extension -eq ".wav" } | Select-Object -ExpandProperty FullName
        $snds = Get-SoundList $allSounds
        $allAssets += $snds

        Open-LogTree $allAssets

        Convert-Textures $textures

        Convert-HKXs $hkxs

        Convert-NIFs $nifs

        Convert-SNDs $snds
    }

    End
    {
        Trace-Verbose ("Convert-Path") $Global:SNXT.Logfile -1
    }
}
