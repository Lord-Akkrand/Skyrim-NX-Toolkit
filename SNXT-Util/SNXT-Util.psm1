$HomeLocation = Split-Path $MyInvocation.MyCommand.Path
$BaseLocation = Split-Path -Parent $HomeLocation

$Utilities = Join-Path -Path $BaseLocation -ChildPath "Utilities"
$Sound = Join-Path -Path $Utilities -ChildPath "Sound"
$GraphicsTools = Join-Path -Path $BaseLocation -ChildPath "GraphicsTools"
$NvnTools = Join-Path -Path $BaseLocation -ChildPath "NvnTools"

$ToolsPaths = $Utilities, $Sound, $GraphicsTools, $NvnTools

function Get-Utility([string] $util)
{
    #Write-Host ("Get-Utility " + $util + " at " + $HomeLocation)
    foreach ($path in $ToolsPaths)
    {
        $testPath = Join-Path -Path $path -ChildPath $util
        #Write-Host ("Get-Utility test " + $testPath)
        if (Test-Path $testPath -PathType Leaf)
        {
            return $testPath
        }
    } 
    return $False
}

function Get-RelativeFilename([string] $fullPath)
{
    $relativeFilename = $fullPath.Replace($Global:SNXT.BasePath + [IO.Path]::DirectorySeparatorChar, "")
    return $relativeFilename
}

function Get-LogTreeFilename([string] $fullPath)
{
    $relativeFilename = Get-RelativeFilename($fullPath)
    $logFilename = Join-Path -Path $Global:SNXT.LogBase -ChildPath ("{0}.xml" -f $relativeFilename)
    return $logFilename
}

function Report-Measure([scriptblock] $script, [string] $title)
{
    $time = Measure-Command { Invoke-Command -ScriptBlock $script } | Select-Object -Property TotalSeconds
    Trace-Verbose ('{0} Time="{1}"' -f $title, $time.TotalSeconds) $Global:SNXT.Logfile
}

function Test-SDK
{
    $sdkPath = Get-Utility "NvnTexpkg.exe"
    return ($sdkPath -ne $False)
}

function Get-Magic($spellbook, $data)
{
    foreach ($key in $spellbook.Keys) 
    {
        $magic = $spellbook.$key
        $isType = $True
        for ($i=0; $i -lt $magic.length; $i++)
        {
            $local = $data[$i]
            $target = $magic[$i]
            if ($local -ne $target)
            {
                $isType = $False
                break
            }
        }
        if ($isType -eq $True)
        {
            return $key
        }
    }
    
    return "UNKNOWN"
}

function Resolve-Message([string] $msg, [string] $level, [int] $opt_Begin)
{
    #Write-Host ("[{0}] {1}" -f $msg, $opt_Begin)
    if ($opt_Begin -eq $null) { $opt_Begin = 0 }
    $retMsg = $msg
    
    switch ($opt_Begin)
    {
        -1 { 
            $retMsg = ("</{0}{1}>`n" -f $level, $msg)
            Break 
        }
        0 { 
            $retMsg = ("<{0}{1}/>`n" -f $level, $msg)
            Break 
        }
        1 { 
            $retMsg = ("<{0}{1}>`n" -f $level, $msg)
            Break 
        }
    }

    return $retMsg
}

# Trace-Verbose is the lowest level logging - for things that only exist in an asset's logfile.
function Trace-Verbose([string] $oMsg, [string] $logFile, [int] $opt_Begin)
{
    $msg = Resolve-Message $oMsg "" $opt_Begin
    $msg | Out-File $logfile -Append -NoNewLine
    #Wait-Command {Add-Content -Path $logfile -Value $msg -NoNewLine}
}

# Trace-Debug is the most used level of logging.  It appears in the main log file.
function Trace-Debug([string] $oMsg, [string] $logFile, [int] $opt_Begin)
{
    $msg = Resolve-Message $oMsg "SNXTDebug_" $opt_Begin
    $msg | Out-File $logfile -Append -NoNewLine
    #Wait-Command {Add-Content -Path $logfile -Value $msg -NoNewLine}
}

# Trace-Warn is for problems that should be fixed.  It appears in the main log file, and will display in the console.
function Trace-Warn([string] $oMsg, [string] $logFile, [int] $opt_Begin)
{
    $msg = Resolve-Message $oMsg "SNXTWarning_" $opt_Begin
    $msg | Out-File $logfile -Append -NoNewLine
    #Wait-Command {Add-Content -Path $logfile -Value $msg -NoNewLine}
}

# Trace Error is for problems that cannot be rectified.  They are essentially fatal.
function Trace-Error([string] $oMsg, [string] $logFile, [int] $opt_Begin)
{
    $msg = Resolve-Message $oMsg "SNXTError_" $opt_Begin
    $msg | Out-File $logfile -Append -NoNewLine
    #Wait-Command {Add-Content -Path $logfile -Value $msg -NoNewLine}
}

function Start-Executable {
  param(
    [String] $FilePath,
    [String[]] $ArgumentList
  )
  $OFS = " "
  $process = New-Object System.Diagnostics.Process
  $process.StartInfo.FileName = $FilePath
  $process.StartInfo.Arguments = $ArgumentList
  $process.StartInfo.UseShellExecute = $false
  $process.StartInfo.RedirectStandardOutput = $true
  if ( $process.Start() ) {
    $output = $process.StandardOutput.ReadToEnd() `
      -replace "\r\n$",""
    if ( $output ) {
      if ( $output.Contains("`r`n") ) {
        $output -split "`r`n"
      }
      elseif ( $output.Contains("`n") ) {
        $output -split "`n"
      }
      else {
        $output
      }
    }
    $process.WaitForExit()
    & "$Env:SystemRoot\system32\cmd.exe" `
      /c exit $process.ExitCode
  }
}

function Wait-Command {
    [CmdletBinding()]
    Param(
        [Parameter(Position=0, Mandatory=$true)]
        [scriptblock]$ScriptBlock,

        [Parameter(Position=1, Mandatory=$false)]
        [int]$Maximum = 10
    )

    Begin {
        $cnt = 0
    }

    Process {
        $ErrorActionPreference = 'Continue'
        do {
            $cnt++
            try {
                $ScriptBlock.Invoke()
                return
            } catch {}
        } while ($cnt -lt $Maximum)
        $ErrorActionPreference = 'Stop'

        # Throw an error after $Maximum unsuccessful invocations. Doesn't need
        # a condition, since the function returns upon successful invocation.
        throw 'Execution failed.'
    }
}