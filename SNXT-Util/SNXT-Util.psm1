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

function Get-RelativeFilename([string] $fullPath, [string]$opt_basePath="")
{
    $basePath = $Global:SNXT.BasePath
    if ($opt_basePath -ne "")
    {
        $basePath = $opt_basePath
    }
    $relativeFilename = $fullPath.Replace($basePath + [IO.Path]::DirectorySeparatorChar, "")
    return $relativeFilename
}

function Get-LogTreeFilename([string] $fullPath)
{
    $relativeFilename = Get-RelativeFilename $fullPath
    $logFilename = Join-Path -Path $Global:SNXT.LogBase -ChildPath ("{0}.xml" -f $relativeFilename)
    return $logFilename
}

function Get-FormattedTime($timeInfo)
{
    $timeString = ""
    $needMilliseconds = $True
    if ([int]$timeInfo.Hours -gt 0)
    {
        $timeString = (' Hours="{0}"' -f $timeInfo.Hours)
        $needMilliseconds = $False
    }
    if ([int]$timeInfo.Minutes -gt 0)
    {
        $timeString += (' Minutes="{0}"' -f $timeInfo.Minutes)
        $needMilliseconds = $False
    }
    if ([int]$timeInfo.Seconds -gt 0)
    {
        $timeString += (' Seconds="{0}"' -f $timeInfo.Seconds)
    }
    if ($needMilliseconds)
    {
        $timeString += (' Milliseconds="{0}"' -f $timeInfo.Milliseconds)
    }
    return $timeString
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

function Find-FirstMatch([byte[]] $source, [byte []]$target)
{
    $sourceLen = $source.Length
    $targetLen = $target.Length
    for ($i=0; $i -lt $sourceLen; $i++)
    {
        if ($source[$i] -eq $target[0])
        {
            $matchIndex = $i
            for ($j=1; $j -lt $targetLen; $j++)
            {
                $sourceIndex = $i+$j
                if ($sourceIndex -ge $sourceLen)
                {
                    #Write-Host ('Reached sourceIndex {0} at sourceLen {1}' -f $sourceIndex, $sourceLen)
                    $matchIndex = -1
                    break
                }
                if ($source[$sourceIndex] -ne $target[$j])
                {
                    #Write-Host ('source[{0}]{1} ne target[{2}]{3}' -f $sourceIndex, $source[$sourceIndex], $j, $target[$j])
                    $matchIndex = -1
                    break
                }
            }
            if ($matchIndex -ge 0)
            {
                return $matchIndex
            }
        }
    }
    return -1
}

function Toggle-Endian
{
    ################################################################
    #.Synopsis
    # Swaps the ordering of bytes in an array where each swappable
    # unit can be one or more bytes, and, if more than one, the
    # ordering of the bytes within that unit is NOT swapped. Can
    # be used to toggle between little- and big-endian formats.
    # Cannot be used to swap nibbles or bits within a single byte.
    #.Parameter ByteArray
    # System.Byte[] array of bytes to be rearranged. If you
    # pipe this array in, you must pipe the [Ref] to the array, but
    # a new array will be returned (originally array untouched).
    #.Parameter SubWidthInBytes
    # Defaults to 1 byte. Defines the number of bytes in each unit
    # (or atomic element) which is swapped, but no swapping occurs
    # within that unit. The number of bytes in the ByteArray must
    # be evenly divisible by SubWidthInBytes.
    #.Example
    # $bytearray = toggle-endian $bytearray
    #.Example
    # [Ref] $bytearray | toggle-endian -SubWidthInBytes 2
    ################################################################
    [CmdletBinding()] Param (
    [Parameter(Mandatory = $True, ValueFromPipeline = $True)] [System.Byte[]] $ByteArray,
    [Parameter()] [Int] $SubWidthInBytes = 1 )
    
    if ($ByteArray.count -eq 1 -or $ByteArray.count -eq 0)
    { $ByteArray ; return }
    
    if ($SubWidthInBytes -eq 1)
    { [System.Array]::Reverse($ByteArray); $ByteArray ; return }
    
    if ($ByteArray.count % $SubWidthInBytes -ne 0)
    { throw "ByteArray size must be an even multiple of SubWidthInBytes!" ; return }
    
    $newarray = new-object System.Byte[] $ByteArray.count
    
    # $i tracks ByteArray from head, $j tracks NewArray from end.
    for ($($i = 0; $j = $newarray.count - 1) ;
    $i -lt $ByteArray.count ;
    $($i += $SubWidthInBytes; $j -= $SubWidthInBytes))
    {
        for ($k = 0 ; $k -lt $SubWidthInBytes ; $k++)
        { 
            $newarray[$j - ($SubWidthInBytes - 1) + $k] = $ByteArray[$i + $k] 
        }
    }
    $newarray
}

function Slice-ArrayPython([byte []] $data, [int]$startSlice, [int]$endSlice)
{
    if ($startSlice -lt 0)
    {
        $startSlice = $data.Length + $startSlice + 1
    }
    if ($endSlice -lt 0)
    {
        $endSlice = $data.Length + $endSlice + 1
    }
    #python slicing doesn't include the last entry in a slice
    $endSlice -= 1
    return $data[$startSlice..$endSlice]
}

function Read-Bytes-LittleEndianUnsigned([byte []] $data, [int]$startSlice, [int]$byteCount)
{
    $bytes = Slice-ArrayPython $data $startSlice ($startSlice + $byteCount)
    if ([BitConverter]::IsLittleEndian -ne $True)
    {
        $bytes = Toggle-Endian $bytes
    }
    
    if ($byteCount -eq 2)
    {
        return [bitconverter]::ToUInt16($bytes, 0)
    }
    if ($byteCount -eq 4)
    {
        return [bitconverter]::ToUInt32($bytes, 0)
    }
}

function Slice-StringPython([string] $data, [int]$startSlice, [int]$endSlice)
{
    if ($startSlice -lt 0)
    {
        $startSlice = $data.Length + $startSlice + 1
    }
    if ($endSlice -lt 0)
    {
        $endSlice = $data.Length + $endSlice + 1
    }
    #python slicing doesn't include the last entry in a slice
    $endSlice -= 1
    return $data[$startSlice..$endSlice]
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
            $retMsg = ("<{0}{1} />`n" -f $level, $msg)
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
function Get-ConfigPath
{
    $configPath = Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Config.xml"
    return $configPath
}

function Set-Config
{
    $configPath = Get-ConfigPath
    [xml]$configXML = $null
    if (Test-Path $configPath -PathType Leaf)
    {
         $configXML = Get-Content -Path $configPath
    }
    else
    {
        $defaultConfigPath = Join-Path -Path $HomeLocation -ChildPath "SNXT-Config.xml"
        $configXML = Get-Content -Path $defaultConfigPath
        $configXML.Save($configPath)
    }
    $Global:SNXT.Config = @{}
    foreach ($category in $configXML.Config.ChildNodes)
    {
        #Write-Host ('Config Category [{0}]' -f $category.Name)
        $Global:SNXT.Config.Add($category.Name, @{})
        foreach ($item in $category.ChildNodes)
        {
            $itemValue = $item.Value
            if ($item.Type -eq "Integer")
            {
                $itemValue = $itemValue -as [Int]
            }
            elseif ($item.Type -eq "Boolean")
            {
                $itemValue = [System.Convert]::ToBoolean($itemValue)
            }
            $Global:SNXT.Config[$category.Name].Add($item.Name, $itemValue)
            #Write-Host ('Config Item [{0}] is [{1}]' -f $item.Name, $itemValue)
        }
    }
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