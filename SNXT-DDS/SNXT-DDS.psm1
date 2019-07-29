
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-DDS\DDS-Formats.ps1") -Force -WarningAction SilentlyContinue

$MagicBytes = @{}
$MagicBytes.PC = 68, 68, 83
$MagicBytes.NX = 68, 70, 118, 78

function Get-Pattern
{
    param(
        [string] $buffer,
        [string] $pattern
    )
    if ($buffer -match $pattern)
    {
        return $Matches[1]
    }
}

function Get-IntPattern
{
    param(
        [string] $buffer,
        [string] $name
    )
    $namePattern = ($name + ": ([\d]+)")
    $returnValue = Get-Pattern $buffer $namePattern
    return [int] $returnValue
}

function Read-DDS([string] $fullpath, [hashtable] $textureInfo)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $fullpath
        $LogTreeFilename = Get-LogTreeFilename $fullpath
        Trace-Debug ('Read-DDS RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1 
    }
    
    Process
    {
        $data = Get-Content -Path $fullpath -Encoding Byte -TotalCount 4
        
        Trace-Verbose ('Read MagicBytes="{0}"' -f [string]$data) $LogTreeFilename
        $textureInfo.SKU = "XXX"
        $textureInfo.SKU = Get-Magic $MagicBytes $data
        Trace-Debug ('Determine TextureSKU="{0}"' -f $textureInfo.SKU) $LogTreeFilename
        if ($textureInfo.SKU -eq "NX")
        {
            return $textureInfo
        }
    
        $nvddsinfoexe = Get-Utility "nvddsinfo.exe"

        $nvddsinfo = [string] (& $nvddsinfoexe $fullpath 2>&1)
        Trace-Verbose ('nvddsinfo Output="{0}"' -f $nvddsinfo) $LogTreeFilename

        $textureInfo.Width = Get-IntPattern $nvddsinfo "Width"
        $textureInfo.Height = Get-IntPattern $nvddsinfo "Height"
        $textureInfo.LinearSize = $textureInfo.Width * $textureInfo.Height
        $textureInfo.Mipmaps = Get-IntPattern $nvddsinfo "Mipmap count"

        Trace-Verbose ('Read Width="{0}"' -f $textureInfo.Width) $LogTreeFilename
        Trace-Verbose ('Read Height="{0}"' -f $textureInfo.Height) $LogTreeFilename
        Trace-Debug ('Determine LinearSize="{0}"' -f $textureInfo.LinearSize) $LogTreeFilename
        Trace-Verbose ('Read Mipmaps="{0}"' -f $textureInfo.Mipmaps) $LogTreeFilename

        $fourCC = Get-Pattern $nvddsinfo "FourCC: '(....)'"
        Trace-Debug ('Read FourCC="{0}"' -f $fourCC) $LogTreeFilename

        if (!$fourCC -or $fourCC -eq 'DX10')
        {
            $texdiagexe = Get-Utility "texdiag.exe"
            $textdiag = [string] (& $texdiagexe info $fullpath 2>&1)
            Trace-Verbose ('textdiag Output="{0}"' -f $textdiag) $LogTreeFilename
            $format = Get-Pattern $textdiag "format = \b([^ ]*)\b"
            Trace-Verbose ('Read TexDiagFormat="{0}"' -f $format) $LogTreeFilename
            foreach ($formatInfo in $Formats)
            {
                if ($format -eq $formatInfo[1])
                {
                    $fourCC = $formatInfo[0]
                    Trace-Debug ('Determine FourCC="{0}"' -f $fourCC) $LogTreeFilename
                }
            }
        }
        $textureInfo.FourCC = $fourCC

        return $textureInfo
    }

    End
    {
        Trace-Debug 'Read-DDS' $LogTreeFilename -1
    }
}

function Compress-DDS([string] $fullpath, [hashtable] $textureInfo, [int] $passNumber)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $fullpath
        $LogTreeFilename = Get-LogTreeFilename $fullpath
        Trace-Debug ('Compress-DDS Pass="{0}" RelativeFilename="{1}"' -f $passNumber, $relativeFilename) $LogTreeFilename 1
    }
    
    Process
    {
        $retValue = @{Pass=$passNumber}
        Trace-Verbose ('Check TextureSKU="{0}"' -f $textureInfo.SKU) $LogTreeFilename
        if ($textureInfo.SKU -eq "NX")
        {
            Trace-Verbose ('Return TextureSKU="{0}"' -f $textureInfo.SKU) $LogTreeFilename
            $retValue.Ignored = $True
            return retValue
        }
        
        $fourCC = $textureInfo.FourCC
        Trace-Debug ('Check FourCC="{0}"' -f $fourCC) $LogTreeFilename
        $ConvertRules = if (Test-SDK) { $ConvertFromToSDK } else { $ConvertFromTo }
        
        if ($fourCC -and $ConvertRules.ContainsKey($textureInfo.FourCC))
        {
            $convertFormat = $ConvertRules[$textureInfo.FourCC]
            $newFormat = $convertFormat[1]
            Trace-Debug ('Convert From="{0}" To="{1}"' -f $fourCC, $newFormat) $LogTreeFilename
            $texconvexe = Get-Utility "texconv.exe"
            $filepath = Split-Path -Path $fullpath
            $texconv = [string] (& $texconvexe -y -f $newFormat $fullpath -o $filepath 2>&1)
            Trace-Verbose ('texconv Output="{0}"' -f $texconv) $LogTreeFilename
            Trace-Verbose ('RunCommand Cmd="{0} -y -f {1} {2} -o {3}"' -f $texconvexe, $newFormat, $fullpath, $filepath) $LogTreeFilename
            Read-DDS $fullpath $textureInfo
            
            $retValue.ConvertFrom = $fourCC
            $retValue.ConvertTo = $newFormat
            $newPassNumber = ($passNumber + 1)
            $retValue[("Pass_{0}" -f $newPassNumber)] = Compress-DDS $fullpath $textureInfo $newPassNumber
            return $retValue
        }

        Trace-Verbose ('RelativePathList') $LogTreeFilename 1
        $relativePathList = $relativeFilename.Split([IO.Path]::DirectorySeparatorChar)
        
        foreach ($path in $relativePathList)
        {
           Trace-Verbose ('Path Node="{0}"' -f $path) $LogTreeFilename
        }
        Trace-Verbose 'RelativePathList' $LogTreeFilename -1

        # Work out which rules apply.  
        # Wow I hate this logic, but I can't seem to find a more elegant way.
        $ResizeRuleSet = "Base"
        $ResizeRules = $RuleSets[$ResizeRuleSet]
        $maxSize = $null
        foreach ($rule in $ResizeRules)
        {
            $rulePaths = $rule.Path
            $match = $False
            Trace-Verbose ('Test Rule="{0}"' -f $rule.Name) $LogTreeFilename

            for ($iP = 0; $iP -lt $relativePathList.length; ++$iP)
            {
                $path = $relativePathList[$iP]
                #Trace-Debug ("On the trail of {0}" -f $path)
                for ($iL = 0; $iL -lt $rulePaths.length; ++$iL)
                {
                    $pathOngoing = $rulePaths[$iL]
                    $internalIdx = 0
					while ($True)
                    {
                        #Trace-Debug (" inside loop iP {0} iL {1}" -f $iP, $iL)
						$nextIdx = $iP + $iL + $internalIdx
						if ($nextIdx -lt $relativePathList.Length)
						{
                            $nextPath = $relativePathList[$nextIdx]
                        }
						else
                        {
							$match = $False
							break
                        }
						$internalIdx++
						$m = $nextPath -match $pathOngoing
						$match = $m -ne $False
						#Trace-Debug (" ongoing into {0} == {1} is {2}" -f $nextPath, $pathOngoing, $m)
						if ($match -eq $True)
                        {
							break
                        }
                    }
					if ($match -eq $False)
                    {
						break
                    }
                }

                if ($match)
                {
				    Trace-Debug ('Apply Rule="{0}"' -f $rule.Name) $LogTreeFilename
				    if ($rule.Contains("Size"))
					{
                        $maxSize = $rule.Size
                    }
                    $retValue.ApplyRule = $rule.Name
				    break
                }
            }
        }
        Trace-Debug ('Test LinearSize="{0}" MaxSize="{1}"' -f $textureInfo.LinearSize, $maxSize) $LogTreeFilename

        $adpddsexe = Get-Utility "adpdds.exe"
        Trace-Debug ('Action ResizeFrom="{0}" ResizeTo="{1}"' -f $textureInfo.LinearSize, $maxSize) $LogTreeFilename

        $maxSingleSize = [math]::sqrt( $maxSize )
        $currentSingleSize = [math]::sqrt( $textureInfo.LinearSize )
        $numberRuns = 0
        while ($currentSingleSize -gt $maxSingleSize)
        {
            $numberRuns++
            $oldSingleSize = $currentSingleSize
            $currentSingleSize *= 0.5
            Trace-Debug ('Determine Run="{0}" ResizeFrom="{1}" ResizeTo="{2}"' -f $numberRuns, $oldSingleSize, $currentSingleSize) $LogTreeFilename
        }
        $numberRuns = [math]::max(1, $numberRuns)
        Trace-Debug ('Determine AdPDDSRuns="{0}"' -f $numberRuns) $LogTreeFilename
        $MyRules = $AdPDDsRuleSet.Clone()
        #Trace-Debug ('ResizeIfGT Default="{0}"' -f $MyRules.ResizeIf)
        if ($maxSize -le (256*256)) { $MyRules.ResizeIf = '256' }
        elseif ($maxSize -le (512*512)) { $MyRules.ResizeIf = '512' }
        elseif ($maxSize -le (1024*1024)) { $MyRules.ResizeIf = '1024' }
        elseif ($maxSize -le (2048*2048)) { $MyRules.ResizeIf = '2048' }
        elseif ($maxSize -le (4096*4096)) { $MyRules.ResizeIf = '4096' }
        elseif ($maxSize -le (8192*8192)) { $MyRules.ResizeIf = '8192' }
        Trace-Verbose ('ResizeIfGT Value="{0}"' -f $MyRules.ResizeIf) $LogTreeFilename

        for ($i=0; $i -lt $numberRuns; $i++)
        {
            if ($i -gt 0)
            {
                $MyRules.MakeMipmaps="Yes"
            }
            
            $adp_config = ""
            foreach ($rule in $AdPDDsRules)
            {
                $ruleOptions = $rule.Options
                $myRule = $MyRules[$rule.Name]
                $val = $ruleOptions[$myRule]
                $adp_config = $adp_config + $val
            }
            Trace-Verbose ('Determine AdPDDSParameters="{0}" Run="{1}"' -f $adp_config, $i) $LogTreeFilename
            $adpdds = [string] (& $adpddsexe $adp_config $fullpath 2>&1)
            Trace-Debug ('adpdds Output="{0}"' -f $adpdds) $LogTreeFilename
        } 
        
        #Write-LogTree (Resolve-Message ('adpdds Output="{0}"' -f $adpdds)) $LogTreeFilename
        if ($Global:SNXT.DebugResize -eq $True)
        {
            Read-DDS $fullpath $textureInfo
            $retValue.DebugNewSingleSize = [math]::sqrt( $textureInfo.LinearSize )
        }
        
        $retValue.NewSingleSize = $currentSingleSize
        
        return $retValue
    }
    
    End
    {
        Trace-Debug 'Compress-DDS' $LogTreeFilename -1
    }
    
}

function Convert-DDS([string] $fullpath, [hashtable] $textureInfo)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $fullpath
        $LogTreeFilename = Get-LogTreeFilename $fullpath
        Trace-Debug ('Convert-DDS RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
    }
    
    Process
    {
        $retValue = @{}
        Trace-Verbose ('Check TextureSKU="{0}"' -f $textureInfo.SKU) $LogTreeFilename
        if ($textureInfo.SKU -eq "NX")
        {
            Trace-Verbose ('Return TextureSKU="{0}"' -f $textureInfo.SKU) $LogTreeFilename
            $retValue.Ignored = $True
            return $retValue
        }
        $hasSdk = Test-SDK
        Trace-Debug ('Check SDK="{0}"' -f $hasSDK) $LogTreeFilename
        if ($hasSDK)
        {
            $nvntexpkgexe = Get-Utility("NvnTexpkg.exe")
            $out_filename = $fullpath + "out.xtx"
            #Set-Location -Path (Split-Path -Path $nvntexpkgexe -Parent)
            #$nvntexpkg = $(Start-Process -FilePath $nvntexpkgexe -WorkingDirectory (Split-Path -Path $nvntexpkgexe -Parent) -NoNewWindow -Wait -ArgumentList ('-i "{0}" -v --printinfo -o "{1}"' -f $fullpath, $out_filename)) 2>&1

    		$nvntexpkg = [string] (& $nvntexpkgexe -i $fullpath -v --printinfo -o $out_filename 2>&1) 
            $outSuccess = Test-Path -Path $out_filename
            Trace-Verbose ('NvnTexpkg Output="{0}"' -f $nvntexpkg) $LogTreeFilename
            Trace-Debug ('Output Success="{0}"' -f $outSuccess) $LogTreeFilename
		    if ($outSuccess)
            {
                Move-Item -Path $out_filename -Destination $fullpath -Force
            }
            $retValue.Success = $outSuccess
            return $retValue
        }
        else
        {
            $out_filename = $fullpath + "out.xtx"
		    
            $xtx_extractexe = Get-Utility("xtx_extract.exe")
			$xtx_extract = [string] (& $xtx_extractexe -o $out_filename $fullpath 2>&1) 
			$outSuccess = Test-Path -Path $out_filename
            Trace-Verbose ('xtx_extract Output="{0}"' -f $xtx_extract) $LogTreeFilename
            Trace-Debug ('Output Success="{0}"' -f $outSuccess) $LogTreeFilename
		    if ($outSuccess)
            {
                Move-Item -Path $out_filename -Destination $fullpath -Force
            }
            $retValue.Success = $outSuccess
            return $retValue
        }
        $retValue.Success = $False
        return $retValue
    }
    
    End
    {
        Trace-Debug 'Convert-DDS' $LogTreeFilename -1
    }
    
}

Export-ModuleMember -Function Read-DDS, Compress-DDS, Convert-DDS
