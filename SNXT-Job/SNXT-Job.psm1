Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force

$RunningJobs = @{}
$JobQueue = New-Object System.Collections.Queue 

function Add-JobToQueue($task)
{
    #Write-Host "Task added to queue"
    $JobQueue.Enqueue($task)
}

function Submit-JobQueue([string] $progressTitle, [string]$BatchName, $Id)
{
    Trace-Debug ('Submit-JobQueue Count="{0}"' -f $JobQueue.Count) $Global:SNXT.Logfile 1

    $started = 0
    $finished = 0
    $successCount = 0
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
                        $addToMainLog = ($line -like "*Debug_*")
                        $line = $line -replace "SNXTDebug_", "" -replace "SNXTWarning_", "" -replace "SNXTError_", ""
                        $line += "`n"
                        if ($addToMainLog)
                        {
                            $mainLog += $line 
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
                    else
                    {
                        $errorCount++
                    }
                }
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
        while ($RunningJobs.Count -lt $Global:SNXT.MaxJobs -and $JobQueue.Count -gt 0)
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
            $status = ("{0}/{1} [{2}]" -f $started, $total, $finished)
            $percentComplete = ($finished / $total) * 100
            Write-Progress -Activity $progressTitle -Status $status -Id $Id -PercentComplete $percentComplete
        }
        $changed = $False
    }
    Write-Host ('JobsComplete Job="{0}" Count="{1}" Success="{2}" Errors="{3}"' -f $BatchName, $total, $successCount, $errorCount)
    Trace-Debug 'Submit-JobQueue' $Global:SNXT.Logfile -1
}

function Submit-Jobs([string] $progressTitle, [string]$BatchName, $Id)
{
    Submit-JobQueue $progressTitle $BatchName $Id
}