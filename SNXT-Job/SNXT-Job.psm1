Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force

$RunningJobs = @{}
$JobQueue = New-Object System.Collections.Queue 

function Add-JobToQueue($task)
{
    #Write-Host "Task added to queue"
    $JobQueue.Enqueue($task)
}
function Submit-ThreadJobQueue([string] $progressTitle, [string]$BatchName, $Id)
{
    Trace-Debug ('Submit-ThreadJobQueue Count="{0}"' -f $JobQueue.Count) $True $null 1

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
                $jobOutput = $(Receive-Job $job) 6>&1 5>&1 4>&1 3>&1 2>&1

                Wait-Command {Add-Content -Path $Global:SNXT.Logfile -Value $jobOutput -NoNewLine}
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
            $job = Start-ThreadJob -ScriptBlock $task.ScriptBlock -ArgumentList $task.Arguments
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
    Trace-Debug 'Submit-ThreadJobQueue' $True $null -1
}
function Submit-JobQueue([string] $progressTitle, [string]$BatchName, $Id)
{
    Trace-Debug ('Submit-JobQueue Count="{0}"' -f $JobQueue.Count) $True $null 1

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
    Trace-Debug 'Submit-JobQueue' $True $null -1
}

function Submit-ProcessQueue([string] $progressTitle, [string]$BatchName, $Id)
{
    Trace-Debug ('Submit-ProcessQueue Count="{0}"' -f $JobQueue.Count) $True $null 1
    $started = 0
    $finished = 0
    $successCount = 0
    $errorCount = 0
    $total = $JobQueue.Count
    $changed = $True
    While ($RunningJobs.Count -gt 0 -or $JobQueue.Count -gt 0)
    {
        #Write-Host ("Submit-RunspaceQueue {0}/{1}" -f $RunningJobs.Count, $JobQueue.Count)
        $jobsToRemove = @()
        foreach ($jobInfo in $RunningJobs.GetEnumerator())
        {
            $jobName = $jobInfo.key
            $task = $jobInfo.value
            $job = $task.Job
            if ($job.IsCompleted)
            {
                $newPowerShell = $task.NewPowerShell
                $result = $newPowershell.EndInvoke($job)
                $newPowerShell.Dispose()
                $jobOutput = $result[0]

                $allOutput = ""
                foreach ($blah in $jobOutput)
                {
                    $allOutput += $blah
                }
                Wait-Command {Add-Content -Path $Global:SNXT.Logfile -Value $allOutput -NoNewLine}
                $jobsToRemove += $jobName
                $finished++
                $changed = $True
            }
        }
        foreach ($jobName in $jobsToRemove)
        {
            $RunningJobs.Remove($jobName)
        }

        while ($RunningJobs.Count -lt $Global:SNXT.MaxJobs -and $JobQueue.Count -gt 0)
        {
            $jobName = New-Guid
            $task = $JobQueue.DeQueue()
            $newPowerShell = [PowerShell]::Create().AddScript($task.ScriptBlock)
            foreach ($arg in $task.Arguments)
            {
                $newPowerShell.AddArgument($arg) >$null
            }
            $job = $newPowerShell.BeginInvoke()
            
            $RunningJobs[$jobName] = @{
                Job = $job
                NewPowershell = $newPowerShell
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
    Trace-Debug 'Submit-ProcessQueue' $True $null -1
}

function Submit-RunspaceQueue([string] $progressTitle, [string]$BatchName, $Id)
{
    Trace-Debug ('Submit-RunspaceQueue Count="{0}"' -f $JobQueue.Count) $True $null 1
    $started = 0
    $finished = 0
    $successCount = 0
    $errorCount = 0
    $total = $JobQueue.Count
    $changed = $True
    $RSP = [runspacefactory]::CreateRunspacePool(1, $Global:SNXT.MaxJobs)
    $newPowershell = [powershell]::Create()
    $newPowershell.RunspacePool = $RSP
    $RSP.Open()

    while ($JobQueue.Count -gt 0)
    {
        $task = $JobQueue.DeQueue()
        $psa = [powershell]::Create()
        $psa.RunspacePool = $RSP

        $psa.AddScript($task.ScriptBlock) >$null
        foreach ($arg in $task.Arguments)
        {
            $psa.AddParameter($arg) >$null
        }
        $handle = $psa.BeginInvoke()

        $jobName = New-Guid
        $RunningJobs[$jobName] = @{
            NewPowershell = $psa
            Handle = $handle
        }
        $started++
        $changed = $True
    }

    While ($RunningJobs.Count -gt 0)
    {
        $jobsToRemove = @()
        foreach ($jobInfo in $RunningJobs.GetEnumerator())
        {
            $jobName = $jobInfo.key
            $task = $jobInfo.value
            $handle = $task.Handle
            if ($handle.IsCompleted)
            {
                $newPowerShell = $task.NewPowerShell
                $result = $newPowershell.EndInvoke($handle)
                $newPowerShell.Dispose()
                $jobOutput = $result[0]
                Wait-Command {Add-Content -Path $Global:SNXT.Logfile -Value $jobOutput -NoNewLine}
                $jobsToRemove += $jobName
                $finished++
                $changed = $True
            }
        }
        foreach ($jobName in $jobsToRemove)
        {
            $RunningJobs.Remove($jobName)
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
    Trace-Debug 'Submit-RunspaceQueue' $True $null -1
}

function Submit-MainThreadQueue([string] $progressTitle, [string]$BatchName, $Id)
{
    Trace-Debug ('Submit-MainThreadQueue Count="{0}"' -f $JobQueue.Count) $True $null 1
    $started = 0
    $finished = 0
    $successCount = 0
    $errorCount = 0
    $total = $JobQueue.Count
    $changed = $True

    while ($JobQueue.Count -gt 0)
    {
        $task = $JobQueue.DeQueue()
        
        $result = Invoke-Command -ScriptBlock $task.ScriptBlock -ArgumentList $task.Arguments
        $started++
    
        Wait-Command {Add-Content -Path $Global:SNXT.Logfile -Value $result -NoNewLine}
        $finished++

        $status = ("{0}/{1} [{2}]" -f $started, $total, $finished)
        $percentComplete = ($finished / $total) * 100
        Write-Progress -Activity $progressTitle -Status $status -Id $Id -PercentComplete $percentComplete
    }
    Write-Host ('JobsComplete Job="{0}" Count="{1}" Success="{2}" Errors="{3}"' -f $BatchName, $total, $successCount, $errorCount)
    Trace-Debug 'Submit-MainThreadQueue' $True $null -1
}


function Submit-Jobs([string] $progressTitle, [string]$BatchName, $Id)
{
    if ($Global:SNXT.JobMethod -eq "ThreadJob")
    {
        Submit-ThreadJobQueue $progressTitle $BatchName $Id
    }
    elseif ($Global:SNXT.JobMethod -eq "Job")
    {
        Submit-JobQueue $progressTitle $BatchName $Id
    }
    elseif ($Global:SNXT.JobMethod -eq "NewPowershell")
    {
        Submit-ProcessQueue $progressTitle $BatchName $Id
    }
    elseif ($Global:SNXT.JobMethod -eq "RunspacePool")
    {
        Submit-RunspaceQueue $progressTitle $BatchName $Id
    }
    elseif ($Global:SNXT.JobMethod -eq "MainThread")
    {
        Submit-MainThreadQueue $progressTitle $BatchName $Id
    }
}