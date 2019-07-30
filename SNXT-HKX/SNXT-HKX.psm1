
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue

$MagicBytes = @{}
$MagicBytes.PC_XML = 60, 63, 120, 109, 108 # "<?xml"



function Read-HKX([string] $fullpath, [hashtable] $info)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $fullpath
        $LogTreeFilename = Get-LogTreeFilename $fullpath
        Trace-Debug ('Read-HKX RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1 
    }
    
    Process
    {
        $data = [array](Get-Content -Path $fullpath -Encoding Byte -TotalCount 20)
        Trace-Verbose ('Read MagicBytes="{0}"' -f [string]$data) $LogTreeFilename
        $info.Type = Get-Magic $MagicBytes $data 
        Trace-Debug ('Determine isXML="{0}"' -f ($info.Type -eq "PC_XML")) $LogTreeFilename
        if ($info.Type -eq "PC_XML")
        {
            return $info
        }
        $bitsFlag = $data[16]
        $nxFlag = $data[18]
        Trace-Verbose ("BF {0} NF {1}" -f $bitsFlag, $nxFlag) $LogTreeFilename
        if ($bitsFlag -eq 4)
        {
            if ($nxFlag -eq 0)
            {
                $info.Type = "PC_32"
                return $info
            }
        }
        elseif ($bitsFlag -eq 8)
        {
            if ($nxFlag -eq 0)
            {
                $info.Type = "PC_64"
                return $info
            }
            elseif ($nxFlag -eq 1)
            {
                $info.Type = "NX_64"
                return $info
            }
        }
        return $info
    }

    End
    {
        Trace-Debug ('Determine HKXType="{0}"' -f $info.Type) $LogTreeFilename
        Trace-Debug 'Read-HKX' $LogTreeFilename -1
    }
}


function Convert-HKX32([string] $fullpath, [hashtable] $info)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $fullpath
        $LogTreeFilename = Get-LogTreeFilename $fullpath
        Trace-Debug ('Convert-HKX32 RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
    }
    
    Process
    {
        $retValue = @{}
        
        $havokBPPexe = Get-Utility "HavokBehaviorPostProcess.exe"
        if ($havokBPPexe -eq $False)
        {
            Trace-Verbose ('Missing HavokBehaviorPostProcess.exe') $LogTreeFilename
            $retValue.MissingHBPP = $True
            $retValue.Success = $False
            return $retValue
        }
        $havokBPP = [string] (& $havokBPPexe --stripMeta --platformPS4 $fullpath $fullpath 2>&1)

        Trace-Verbose ('havokBPPexe Output="{0}"' -f $havokBPP) $LogTreeFilename
        $retValue.Success = $True
        return $retValue
    }
    
    End
    {
        Trace-Debug 'Convert-HKX32' $LogTreeFilename -1
    }
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

function Slice-Array([byte []] $data, [int]$startSlice, [int]$endSlice)
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

function Convert-HKX64([string] $fullpath, [hashtable] $info)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $fullpath
        $LogTreeFilename = Get-LogTreeFilename $fullpath
        Trace-Debug ('Convert-HKX64 RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
    }
    
    
    Process
    {
        $retValue = @{}
        
        Trace-Verbose ('Manually Fix="{0}"' -f $info.Type) $LogTreeFilename

        #$payload = [array](Get-Content -Path $fullpath -Encoding Byte)

        [byte[]] $payload = [System.Io.File]::ReadAllBytes( $fullpath )
        $hkaSkeleton = [System.Text.Encoding]::ASCII.GetBytes('hkaSkeleton')
        
        #Trace-Verbose ('Payload Bytes="{0}"' -f [string]$payload) $LogTreeFilename

        Trace-Verbose ('Test hkaSkeleton="{0}"' -f [string]$hkaSkeleton) $LogTreeFilename
        $findHkaSkeleton = Find-FirstMatch $payload $hkaSkeleton
        if($findHkaSkeleton -ge 0)
        {
            Trace-Debug('Warning hkaSkeleton="{0}"' -f $findHkaSkeleton) $LogTreeFilename
            $retValue.Sucess = $False
            return $retValue
        }

        $hkbBehavior = [System.Text.Encoding]::ASCII.GetBytes('hkbBehavior')
        Trace-Verbose ('Test hkbBehavior="{0}"' -f [string]$hkbBehavior) $LogTreeFilename
        $findHkaBehavior = Find-FirstMatch $payload $hkbBehavior
        if($findHkaBehavior -ge 0)
        {
            Trace-Debug('Warning hkbBehavior="{0}"' -f $findHkaBehavior) $LogTreeFilename
            $retValue.Sucess = $False
            return $retValue
        }

        [byte []] $header = (,0x00 * 15) + (,0x80) + (,0x00 * 48)
        Trace-Verbose ('Find header="{0}"' -f [string]$header) $LogTreeFilename

        $headerStartIndex = Find-FirstMatch $payload $header
        Trace-Verbose ('HeaderStartIndex Value="{0}"' -f $headerStartIndex) $LogTreeFilename
        if ($headerStartIndex -gt 0)
        {
            $hkbProjectData = [System.Text.Encoding]::ASCII.GetBytes('hkbProjectData')
            Trace-Verbose ('Test hkbProjectData="{0}"' -f [string]$hkbProjectData) $LogTreeFilename
            $offset = 76
            $findProjectData = Find-FirstMatch $payload $hkbProjectData
            if ($findProjectData -ge 0)
            {
                $offset = 72
            }
            [byte []] $newPayload = @()
            $newPayload += Slice-Array $payload 0 18
            $newPayload += 0x01
            $newPayload += Slice-Array $payload 19 ($headerStartIndex+16)
            $newPayload += Slice-Array $payload ($headerStartIndex+20) ($headerStartIndex+$offset)
            $newPayload += Slice-Array $payload ($headerStartIndex) ($headerStartIndex+4)
            $newPayload += Slice-Array $payload ($headerStartIndex+$offset) -1

            [System.Io.File]::WriteAllBytes( $fullpath, $newPayload )
        }
        $retValue.Success = $True
        return $retValue
    }
    
    End
    {
        Trace-Debug 'Convert-HKX64' $LogTreeFilename -1
    }
}

Export-ModuleMember -Function Read-HKX, Convert-HKX32, Convert-HKX64
