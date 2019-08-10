﻿
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue

<#""" Normalizes the input audio """#>
function NormalizeAudio([string] $filename_input_audio, [string] $filepath_without_extension, [boolean] $isNxOpus)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $filename_input_audio
        $LogTreeFilename = Get-LogTreeFilename $filename_input_audio
        Trace-Debug ('NormalizeAudio RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        $startTime = Get-Date
    }

    Process
    {
        $FFMpegExe = Get-Utility "ffmpeg.exe"
        $FFMpeg = ""
        $filename_temp = $filename_input_audio.Split(".")[0] + ".TEMP" + $filename_input_audio.Split(".")[-1]
        $filename_output = $filepath_without_extension + ".wav"
        Move-Item -Path $filename_input_audio -Destination $filename_temp -Force
        if ($isNxOpus)\
        {
            $FFMpeg =  [string] (& "-hide_banner" "-y" "-i" $filename_temp "-ac" "1" "-ar" "48000" $filename_output 2>&1)
        } else {
            $FFMpeg =  [string] (& "-hide_banner" "-y" "-i" $filename_temp "-ar" "44100" $filename_output 2>&1)
        }
        Remove-Item -Path $filename_temp
        Trace-Verbose ('FFMpeg Output="{0}"' -f $FFMpeg) $LogTreeFilename
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('NormalizeAudio-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug 'NormalizeAudio' $LogTreeFilename -1
    }
}

<#""" Converts the normalized audio """#>
function ConvertAudio([string] $filename_input_audio, [string] $filepath_without_extension, [boolean] $isNxOpus)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $filename_input_audio
        $LogTreeFilename = Get-LogTreeFilename $filename_input_audio
        Trace-Debug ('ConvertAudio RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        $startTime = Get-Date
    }

    Process
    {
        $VGAudioCliExe = Get-Utility "VGAudioCli.exe"
        $VGAudioCLi = ""
        if ($isNxOpus)\
        {
            $filename_output = $filepath_without_extension + ".fuz"
            $VGAudioCli =  [string] (& $VGAudioCliExe -c --opusheader Skyrim -i:0 $filename_input_audio $filename_output 2>&1)
        } else {
            $filename_output = $filepath_without_extension + ".mcadpcm"
            $VGAudioCli =  [string] (& $VGAudioCliExe -c $filename_input_audio $filename_output 2>&1)
        }
        Remove-Item -Path $filename_input_audio
        Trace-Verbose ('VGAudioCLi Output="{0}"' -f $VGAudioCli) $LogTreeFilename
    }

    End
    {
        $endTime = Get-Date
        $timeSpan = New-TimeSpan -Start $startTime -End $endTime
        $timeString = Get-FormattedTime $timeSpan
        Trace-Verbose ('ConvertAudio-Time{0}' -f $timeString) $LogTreeFilename
        Trace-Debug 'ConvertAudio' $LogTreeFilename -1
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

            # get rid of PC FUZ
            Remove-Item -Path $filename_fuz

        } else if ($has_xwm)
        {
            $filename_audio = $filename_xwm
        } else if ($has_wav) {
            $filename_audio = $filename_wav
        } else {
            Trace-Warn ('Error this logic branch should be unreachable ="{0}"' -f $filepath_without_extension) $LogTreeFilename
            $retValue['Success'] = $False
            return $retValue
        }

        NormalizeAudio $filename_audio $filepath_without_extension $is_nxopus
        ConverAudio $filename_audio $filepath_without_extension $is_nxopus

        if ($has_lip)
        {
            Remove-Item -Path $filename_lip
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