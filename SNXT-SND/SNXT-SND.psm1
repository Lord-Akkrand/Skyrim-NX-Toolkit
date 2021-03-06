﻿
Import-Module $(Join-Path -Path $Global:SNXT.HomeLocation -ChildPath "SNXT-Util\SNXT-Util.psm1") -Force -WarningAction SilentlyContinue

<#""" Normalizes the input audio """#>
function NormalizeAudio([string] $filename_input_audio, [string] $filepath_without_extension, [boolean] $isNxOpus)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $filepath_without_extension
        $LogTreeFilename = Get-LogTreeFilename $filepath_without_extension
        Trace-Debug ('NormalizeAudio RelativeFilename="{0}"' -f $filename_input_audio) $LogTreeFilename 1
        $startTime = Get-Date
    }

    Process
    {
        $FFMpegExe = Get-Utility "ffmpeg.exe"
        $FFMpeg = ""
        $filename_temp = $filepath_without_extension + ".temp.wav"
        $filename_output = $filepath_without_extension + ".wav"
        if ($isNxOpus)
        {
            $FFMpeg =  [string] (& $FFMpegExe "-hide_banner" "-y" "-i" $filename_input_audio "-ac" "1" "-ar" "48000" $filename_temp 2>&1)
        }
        else
        {
            $FFMpeg =  [string] (& $FFMpegExe "-hide_banner" "-y" "-i" $filename_input_audio "-ar" "44100" $filename_temp 2>&1)
        }
        Trace-Verbose ('FFMpeg Output="{0}"' -f $FFMpeg) $LogTreeFilename
        try {
            Remove-Item -Path $filename_input_audio
            Rename-Item -Path $filename_temp -NewName $filename_output
            return $True
        }
        catch {
            Trace-Warn ('Error FailedToNormalize="{0}"' -f $filepath_without_extension) $LogTreeFilename
            return $False
        }
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
function ConvertAudio([string] $filename_input_audio, [string] $filepath_without_extension, [boolean] $isNxOpus, [boolean] $has_lip)
{
    Begin
    {
        $relativeFilename = Get-RelativeFilename $filepath_without_extension
        $LogTreeFilename = Get-LogTreeFilename $filepath_without_extension
        Trace-Debug ('ConvertAudio RelativeFilename="{0}"' -f $relativeFilename) $LogTreeFilename 1
        $startTime = Get-Date
    }

    Process
    {
        $VGAudioCliExe = Get-Utility "VGAudioCli.exe"
        $VGAudioCLi = ""
        $filename_temp = ""
        $filename_output = ""
        $filename_temp_lip = ""
        if ($isNxOpus -and $has_lip) {
            $filename_temp_lip = $filepath_without_extension + ".temp.lip"
            $filename_lip = $filepath_without_extension + ".lip"
            Rename-Item -Path $filename_lip -NewName $filename_temp_lip
        }
        if ($isNxOpus)
        {
            $filename_temp = $filepath_without_extension + ".temp.fuz"
            $filename_output = $filepath_without_extension + ".fuz"
            $VGAudioCli =  [string] (& $VGAudioCliExe -c --opusheader Skyrim -i:0 $filename_input_audio $filename_temp 2>&1)
        }
        else
        {
            $filename_temp = $filepath_without_extension + ".temp.mcadpcm"
            $filename_output = $filepath_without_extension + ".mcadpcm"
            $VGAudioCli =  [string] (& $VGAudioCliExe -c $filename_input_audio $filename_temp 2>&1)
        }
        Trace-Verbose ('VGAudioCLi Output="{0}"' -f $VGAudioCli) $LogTreeFilename
        try {
            if ($is_nxopus -and $has_lip)
            {
                Remove-Item -Path $filename_temp_lip
            }
            Remove-Item -Path $filename_input_audio
            Rename-Item -Path $filename_temp -NewName $filename_output
            return $True
        }
        catch {
            Trace-Warn ('Error FailedToConvert="{0}"' -f $filepath_without_extension) $LogTreeFilename
            return $False
        }
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
        $lip_version = 0
        $lip_data = $null
        $audio_data = $null
        $filename_audio = ''

        if ($has_fuz)
        {
            try {
                [byte[]] $fuz_file = [System.Io.File]::ReadAllBytes( $filename_fuz )
                $lip_version = Read-Bytes-LittleEndianUnsigned $fuz_file 0x0C 0x04
                # check if already converted
                if ($lip_version -ne 0x00000001 -and $lip_version -ne 0x46464952)
                {
                    $retValue['Skipped'] = $True
                    return $retValue
                }
                $lip_size = Read-Bytes-LittleEndianUnsigned $fuz_file 0x08 0x04
                $lip_data = Slice-ArrayPython $fuz_file 0x0C (0x0C+$lip_size)
                $audio_data = Slice-ArrayPython $fuz_file (0x0C+$lip_size) -1
            }
            catch {
                Trace-Warn ('Error FailedToOpen="{0}"' -f $filename_fuz) $LogTreeFilename
                $retValue['Success'] = $False
                return $retValue
            }

            # determine AUDIO format in FUZ
            $audio_format = Slice-ArrayPython $audio_data 0x08 0x0C
            $xwma = [System.Text.Encoding]::ASCII.GetBytes('XWMA')
            $wave = [System.Text.Encoding]::ASCII.GetBytes('WAVE')
            Trace-Verbose ('Test XWMA="{0}"' -f [string]$xwma) $LogTreeFilename
            Trace-Verbose ('Test WAVE="{0}"' -f [string]$wave) $LogTreeFilename
            $findXWMA = Find-FirstMatch $audio_format $xwma
            $findWAVE = Find-FirstMatch $audio_format $wave

            # determine which audio file to use (loose WAV > loose XWM > FUZ)
            $save_audio_from_fuz = $True
            if ($has_wav)
            {
                $filename_audio = $filename_wav
                $save_audio_from_fuz = $False
            }
            elseif ($findWAVE -ge 0)
            {
                $has_wav = $True
                $filename_audio = $filename_wav
            }
            elseif ($has_xwm)
            {
                $filename_audio = $filename_xwm
                $save_audio_from_fuz = $False
            }
            elseif ($findXWMA -ge 0)
            {
                $has_xwm = $True
                $filename_audio = $filename_xwm
            }

            # save AUDIO contents
            if ($save_audio_from_fuz)
            {
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

            # save LIP contents
            if ($lip_size -gt 0 -and -not $has_lip)
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

            # get rid of PC FUZ
            Remove-Item -Path $filename_fuz
        }
        elseif ($has_wav)
        {
            $filename_audio = $filename_wav
        }
        elseif ($has_xwm)
        {
            $filename_audio = $filename_xwm
        }
        else
        {
            Trace-Warn ('Error UnreachableCodeBranch="{0}"' -f $filepath_without_extension) $LogTreeFilename
            $retValue['Success'] = $False
            return $retValue
        }

        if ($has_wav -and $has_xwm)
        {
            Remove-Item -Path $filename_xwm
        }

        $ok = NormalizeAudio $filename_audio $filepath_without_extension $is_nxopus
        if ($ok)
        {
            $ok = ConvertAudio $filename_wav $filepath_without_extension $is_nxopus $has_lip
        }

        $retValue['Success'] = $ok
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