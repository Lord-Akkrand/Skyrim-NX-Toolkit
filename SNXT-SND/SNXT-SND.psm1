
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue

<#""" converts the XWM file to WAV """#>
function Convert-XWM2WAV([string] $filename_xwm, [string] $filename_wav, [string] $filepath_without_extension)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $filepath_without_extension
        $LogTreeFilename = Get-LogTreeFilename $filepath_without_extension
        Trace-Debug ('Convert-XWM2WAV RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        $startTime = Get-Date
    }
	
    Process
    {
        $xWMAEncodeExe = Get-Utility "xWMAEncode.exe"
        $xWMAEncode =  [string] (& $xWMAEncodeExe $filename_xwm $filename_wav 2>&1)

        Trace-Verbose ('xWMAEncodeExe Output="{0}"' -f $xWMAEncode) $LogTreeFilename
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-XWM2WAV-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug 'Convert-XWM2WAV' $LogTreeFilename -1
    }	
}


function Convert-WAV2PCM16WAV([string] $filename_xwm, [string] $filename_wav, [boolean] $isNxOpus, [string] $filepath_without_extension)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $filepath_without_extension
        $LogTreeFilename = Get-LogTreeFilename $filepath_without_extension
        Trace-Debug ('Convert-WAV2PCM16WAV RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        $startTime = Get-Date
    }
	
    Process
    {
        [byte[]]$wav_header = $null
        try {
            $wav_header = [byte[]](Get-Content -Path $filename_wav -Encoding Byte -TotalCount 0x24)
        }
        catch {
            Trace-Warn ('Error FailedToOpen="{0}"' -f $filename_wav) $LogTreeFilename
            return $False
        }
        

        $wav_audio_format = Read-Bytes-LittleEndianUnsigned $wav_header 0x14 2
        $wav_channel_count = Read-Bytes-LittleEndianUnsigned $wav_header 0x16 2
        $wav_sample_rate = Read-Bytes-LittleEndianUnsigned $wav_header 0x18 4
        $wav_bits_per_sample = Read-Bytes-LittleEndianUnsigned $wav_header 0x22 2

        # make the WAV file compatible with VGAudioCLi
        #
        # OPUS CODEC requires 24000 or 48000 sample rates from a mono PCM16 stream
        # DSPADPCM CODEC requires 22050 or 44100 sample rates from a mono or stereo PCM16 stream

        # get the closest ressampling RATE
        $DESIRED_RATES = @(22050, 44100)
        if ($isNxOpus)
        {
            $DESIRED_RATES = @(24000, 48000)
        }

        $i = 0

        while ($wav_sample_rate -ge $DESIRED_RATES[$i])
        {
            $i += 1
            if ($i -gt 1)
            {
                $i = 1
                break
            }
        }

        $override_sample_rate = [string] $DESIRED_RATES[$i].ToString()

        # ressample if required
        if ($DESIRED_RATES.Contains($wav_sample_rate) -eq $False -or $wav_audio_format -ne 1 -or $wav_bits_per_sample -ne 16)
        {
            $filename_temp = $filename_wav + "temp.wav"
            Move-Item -Path $filename_wav -Destination $filename_temp -Force
            $sndfileconvertexe = Get-Utility "sndfile-convert.exe"
            $override_same_rate_argument = ('-override-sample-rate={0}' -f $override_sample_rate)
            $sndfileconvert = [string] (& $sndfileconvertexe $override_same_rate_argument -pcm16 $filename_temp $filename_wav 2>&1)

            Trace-Verbose ('sndfile-convert.exe Argument="{0}" Output="{1}"' -f $override_same_rate_argument, $sndfileconvert) $LogTreeFilename
            Remove-Item -Path $filename_temp
            Trace-Verbose ('Normalized WAV="{0}" Format="{1}" Channels="{2}" SampleRate="{3}" BitsPerSample="{4}"' -f $filename_wav, $wav_audio_format, $wav_channel_count, $wav_sample_rate, $wav_bits_per_sample) $LogTreeFilename
        }
        return $True
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-WAV2PCM16WAV-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug 'Convert-WAV2PCM16WAV' $LogTreeFilename -1
    }
}

<#""" creates MCADPCM from WAVE """#>
function Convert-WAV2MCADPCM([string] $filename_wav, [string] $filename_fuz, [string]$filepath_without_extension)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $filepath_without_extension
        $LogTreeFilename = Get-LogTreeFilename $filepath_without_extension
        Trace-Debug ('Convert-WAV2MCADPCM RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        $startTime = Get-Date
    }
	
    Process
    {
        $VGAudioCliExe = Get-Utility "VGAudioCli.exe"
        $VGAudioCli =  [string] (& $VGAudioCliExe -c $filename_wav $filename_mcadpcm 2>&1)

        Trace-Verbose ('VGAudioCliExe Output="{0}"' -f $VGAudioCli) $LogTreeFilename
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-WAV2MCADPCM-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug 'Convert-WAV2MCADPCM' $LogTreeFilename -1
    }	
}

<#""" creates FUZ from WAV """#>
function Convert-WAV2FUZ([string] $filename_wav, [string] $filename_fuz, [string]$filepath_without_extension)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $filepath_without_extension
        $LogTreeFilename = Get-LogTreeFilename $filepath_without_extension
        Trace-Debug ('Convert-WAV2FUZ RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        $startTime = Get-Date
    }
	
    Process
    {
        # Only getting channel 0 from WAVE when creating OPUS
        $VGAudioCliExe = Get-Utility "VGAudioCli.exe"
        $VGAudioCli =  [string] (& $VGAudioCliExe -c --opusheader Skyrim -i:0 $filename_wav $filename_fuz 2>&1)

        Trace-Verbose ('VGAudioCliExe Output="{0}"' -f $VGAudioCli) $LogTreeFilename
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-WAV2FUZ-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug 'Convert-WAV2FUZ' $LogTreeFilename -1
    }	
}

function Convert-SND([string] $filepath_without_extension, [hashtable] $info)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $filepath_without_extension
        $LogTreeFilename = Get-LogTreeFilename $filepath_without_extension
        Trace-Debug ('Convert-SND RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        $startTime = Get-Date
    }
    
    Process
    {

        <#
        $retValue = @{}
        $convert_sound_zappaexe = Get-Utility "convert_sound_zappa.exe"
        $scriptPath = Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "Scripts"
        $convert_sound_zappa = [string] (& $convert_sound_zappaexe $filepath_without_extension $scriptPath 2>&1)

        Trace-Verbose ('convert_sound_zappa Output="{0}"' -f $convert_sound_zappa) $LogTreeFilename
        $retValue.Success = $True
        Trace-Debug ('Success Value="{0}"' -f $retValue.Success) $LogTreeFilename
        return $retValue
        #>

        $retValue = @{}

        $filename_mcadpcm = $filepath_without_extension + ".mcadpcm"
        $filename_wav = $filepath_without_extension + ".wav"
        $filename_xwm = $filepath_without_extension + ".xwm"
        $filename_lip = $filepath_without_extension + ".lip"
        $filename_fuz = $filepath_without_extension + ".fuz"

        $has_wav = Test-Path -Path $filename_wav -PathType Leaf
        $has_xwm = Test-Path -Path $filename_xwm -PathType Leaf
        $has_lip = Test-Path -Path $filename_lip -PathType Leaf
        $has_fuz = Test-Path -Path $filename_fuz -PathType Leaf

        $nxopus_regex = ('*{0}sound{0}voice{0}*' -f [IO.Path]::DirectorySeparatorChar)
        $is_nxopus = $filepath_without_extension -like $nxopus_regex
        
        Trace-Verbose ('Has WAV="{0}"' -f $has_wav) $LogTreeFilename
        Trace-Verbose ('Has XWM="{0}"' -f $has_xwm) $LogTreeFilename
        Trace-Verbose ('Has LIP="{0}"' -f $has_lip) $LogTreeFilename
        Trace-Verbose ('Has FUZ="{0}"' -f $has_fuz) $LogTreeFilename

        $lip_size = 0
        $lip_data = $null
        $audio_data = $null
        $filename_audio = ''

        # FUZ files always have precedence over loose WAV, XWM, LIP
        if ($has_fuz)
        {
            try {
                [byte[]] $fuz_file = [System.Io.File]::ReadAllBytes( $filename_fuz )
                $lip_size = Read-Bytes-LittleEndianUnsigned $fuz_file 0x08 0x04
                $lip_data = Slice-ArrayPython $fuz_file 0x0C (0x0C+$lip_size)
                $audio_data = Slice-ArrayPython $fuz_file (0x0C+$lip_size) -1 
            }
            catch {
                Trace-Warn ('Error FailedToOpen="{0}"' -f $filename_fuz) $LogTreeFilename
                $retValue['Success'] = $False
                return $retValue
            }
            # determine AUDIO format
            $audio_format = Slice-ArrayPython $audio_data 0x08 0x0C
            $wave = [System.Text.Encoding]::ASCII.GetBytes('WAVE')
            Trace-Verbose ('Test WAVE="{0}"' -f [string]$wave) $LogTreeFilename
            $findWAVE = Find-FirstMatch $audio_format $wave
            if($findWAVE -ge 0)
            {
                $has_wav = $True
                $filename_audio = $filename_wav
            }
            else {
                $xwma = [System.Text.Encoding]::ASCII.GetBytes('XWMA')
                Trace-Verbose ('Test XWMA="{0}"' -f [string]$xwma) $LogTreeFilename
                $findXWMA = Find-FirstMatch $audio_format $xwma
                if ($findXWMA -ge 0)
                {
                    $has_xwm = $True
                    $filename_audio = $filename_xwm
                }
            }

            # save LIP contents
            if ($lip_size -gt 0)
            {
                try {
                    [System.Io.File]::WriteAllBytes( $filename_lip, $lip_data )
                    $has_lip = $True
                    Trace-Verbose ('Created NewFile="{0}" From="{1}"' -f $filename_lip, $filename_fuz) $LogTreeFilename
                }
                catch {
                    Trace-Warn ('Error FailedToCreateLIP="{0}"' -f $filename_lip) $LogTreeFilename
                    $retValue['Success'] = $False
                    return $retValue
                }
            }

            # save AUDIO contents
            try {
                [System.Io.File]::WriteAllBytes( $filename_audio, $audio_data )
                Trace-Verbose ('Created NewFile="{0}" From="{1}"' -f $filename_audio, $filename_fuz) $LogTreeFilename
            }
            catch {
                Trace-Warn ('Error FailedToCreateAudio="{0}"' -f $filename_audio) $LogTreeFilename
                $retValue['Success'] = $False
                return $retValue
            }
        }
        # Convert the XWM to WAV
        if ($has_xwm)
        {
            Convert-XWM2WAV $filename_xwm $filename_wav $filepath_without_extension
        }

        # Normalize the WAV format
	    $normalized = Convert-WAV2PCM16WAV $filename_xwm $filename_wav $is_nxopus $filepath_without_extension
        if ($normalized -eq $False)
        {
            $retValue['Success'] = $False
            return $retValue
        }

        # Convert the normalized WAV to final format
        if ($is_nxopus)
        {
            Convert-WAV2FUZ $filename_wav $filename_fuz $filepath_without_extension
        }
        else
        {
            Convert-WAV2MCADPCM $filename_wav $filename_mcadpcm $filepath_without_extension
        }

        # clean up temporary files
        Remove-Item -Path $filename_wav
        if ($has_xwm)
        {
            Remove-Item -Path $filename_xwm
        }
        if ($has_lip)
        {
            Remove-Item -Path $filename_lip
        }
        if ($has_fuz -and $is_nxopus -eq $False)
        {
            Remove-Item -Path $filename_fuz
        }
        $retValue['Success'] = $True
	    return $retValue
    }
    
    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('Convert-SND-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug 'Convert-SND' $LogTreeFilename -1
    }
}

Export-ModuleMember -Function Convert-SND
