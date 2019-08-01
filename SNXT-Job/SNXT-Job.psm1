﻿Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force

$RunningJobs = @{}
$JobQueue = New-Object System.Collections.Queue 

function Add-JobToQueue($task)
{
    #Write-Host "Task added to queue"
    $JobQueue.Enqueue($task)
}

function Get-BatchSize($assetCount)
{
    $numberThreads = $Global:SNXT.Config.Performance.MaxThreads
    
    $spreadOut = $assetCount / $numberThreads
    $multipleThreads = [Math]::ceiling($spreadOut / $Global:SNXT.Config.Performance.BatchesPerThread)
    $batchSize = [Math]::max($Global:SNXT.Config.Performance.MinBatchSize, $multipleThreads)
    $batchSize = [Math]::min($Global:SNXT.Config.Performance.MaxBatchSize, $batchSize)
    
    return [int]$batchSize
}
function Submit-JobQueue([string] $progressTitle, [string]$BatchName, $Id)
{
    Trace-Verbose ('Submit-JobQueue Count="{0}"' -f $JobQueue.Count) $Global:SNXT.Logfile 1

    $started = 0
    $finished = 0
    $successCount = 0
    $skippedCount = 0
    $errorCount = 0
    $total = $JobQueue.Count
    $changed = $True
    While ($RunningJobs.Count -gt 0 -or $JobQueue.Count -gt 0)
    {
        $VerbosePreference = 'SilentlyContinue'
        $DebugPreference = 'SilentlyContinue'
        #Write-Host ("Submit-JobQueue {0}/{1}" -f $RunningJobs.Count, $JobQueue.Count)
        $jobsToRemove = @()
        foreach ($jobInfo in $RunningJobs.GetEnumerator())
        {
            $jobName = $jobInfo.key
            $task = $jobInfo.value
            $job = $task.Job
            if ($job.State -eq "Completed")
            {
                $hashOutput = Receive-Job $job
                
                foreach ($assetName in $hashOutput.Keys)
                {
                    $LogTreeFilename = Get-LogTreeFilename $assetName

                    $assetLog = Get-Content -Path $LogTreeFilename
                    $mainLog = ""
                    $newAssetLog = ""
                    foreach ($line in $assetLog)
                    {
                        $addToMainLog = ($line -like "*SNXTDebug_*")
                        $displayToScreen = ($line -like "*SNXTWarning_*")
                        $line = $line -replace "SNXTDebug_", "" -replace "SNXTWarning_", ""
                        $line += "`n"
                        if ($addToMainLog -or $displayToScreen)
                        {
                            $mainLog += $line 
                        }
                        if ($displayToScreen)
                        {
                            Write-Host ($line -replace "`n","" -replace "`r", "")
                        }
                        $newAssetLog += $line
                    }
                    Set-Content -Path $LogTreeFilename -Value $newAssetLog
                    $mainLog | Out-File $Global:SNXT.Logfile -Append -NoNewLine
                    #Wait-Command {Add-Content -Path $Global:SNXT.Logfile -Value $mainLog -NoNewLine}
                    
                    $assetReturn = $hashOutput[$assetName]
                    if ($assetReturn.Success -eq $True)
                    {
                        $successCount++
                    }
                    elseif ($assetReturn.Skipped -eq $True)
                    {
                        $skippedCount++
                    }
                    else
                    {
                        $errorCount++
                    }
                }
                Remove-Job -Job $job
                $jobsToRemove += $jobName
                $finished++
                $changed = $True
            }
        }
        foreach ($jobName in $jobsToRemove)
        {
            $RunningJobs.Remove($jobName)
        }

        $VerbosePreference = 'Continue'
        $DebugPreference = 'Continue'
        
        while ($RunningJobs.Count -lt $Global:SNXT.Config.Performance.MaxThreads -and $JobQueue.Count -gt 0)
        {
            #Write-Host "Starting job"
            $task = $JobQueue.DeQueue()
            $job = Start-Job -ScriptBlock $task.ScriptBlock -ArgumentList $task.Arguments
            $jobName = $job.Name
            $RunningJobs[$jobName] = @{
                Job = $job
            }
            $started++
            $changed = $True
        }
        Start-Sleep -Seconds 0.125

        if ($changed)
        {
            $status = ("Batches Started/Complete/Total {0}/{1}/{2} Assets Success/Skipped/Error {3}/{4}/{5}" -f $started, $finished, $total, $total, $successCount, $skippedCount, $errorCount)
            $percentComplete = ($finished / $total) * 100
            Write-Progress -Activity $progressTitle -Status $status -Id $Id -PercentComplete $percentComplete
        }
        $changed = $False
    }
    Write-Host ('JobsComplete Job="{0}" Count="{1}" Success="{2}" Errors="{3}" Skipped="{4}"' -f $BatchName, $total, $successCount, $errorCount, $skippedCount)
    Trace-Verbose 'Submit-JobQueue' $Global:SNXT.Logfile -1
}

function Submit-Jobs([string] $progressTitle, [string]$BatchName, $Id)
{
    Submit-JobQueue $progressTitle $BatchName $Id
}