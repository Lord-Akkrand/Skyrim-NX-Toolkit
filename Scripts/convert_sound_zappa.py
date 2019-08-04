#! python3

import os
import util
import time

def GetVGAudioCli():
	utilities_path = util.GetUtilitiesPath()
	VGAudioCli = os.path.join(utilities_path, "Sound", "VGAudioCli.exe")
	return VGAudioCli

def GetxWMAEncode():
	utilities_path = util.GetUtilitiesPath()
	xWMAEncode = os.path.join(utilities_path, "Sound", "xWMAEncode.exe")
	return xWMAEncode

def GetSndFileConvert():
	utilities_path = util.GetUtilitiesPath()
	SndFileConvert = os.path.join(utilities_path, "Sound", "sndfile-convert.exe")
	return SndFileConvert

def XWM2WAV(filename_xwm, filename_wav):
	""" converts the XWM file to WAV """

	xWMAEncode = GetxWMAEncode()
	commandLine = [xWMAEncode, filename_xwm, filename_wav]
	util.RunCommandLine(commandLine)

def WAV2PCM16WAV(filename_xwm, filename_wav, isNxOpus):
	""" Normalizes the WAV file to be a proper PCM16 with correct sample rate for VGAudioCli """

	try:
		with open(filename_wav, "rb") as wav_file:
			wav_header = wav_file.read(0x24)
	except:
		util.LogInfo("ERROR: failed to create intermediate WAV <{}>.".format(filename_wav))
		return False

	wav_audio_format = int.from_bytes(wav_header[0x14:0x16], byteorder = 'little', signed = False)
	wav_channel_count = int.from_bytes(wav_header[0x16:0x18], byteorder = 'little', signed = False)
	wav_sample_rate = int.from_bytes(wav_header[0x18:0x1C], byteorder = 'little', signed = False)
	wav_bits_per_sample = int.from_bytes(wav_header[0x22:0x24], byteorder = 'little', signed = False)

	# make the WAV file compatible with VGAudioCLi
	#
	# OPUS CODEC requires 24000 or 48000 sample rates from a mono PCM16 stream
	# DSPADPCM CODEC requires 22050 or 44100 sample rates from a mono or stereo PCM16 stream

	# get the closest ressampling RATE
	DESIRED_RATES = [24000, 48000] if isNxOpus else [22050, 44100]
	try:
		i = 0
		while wav_sample_rate >= DESIRED_RATES[i]:
			i += 1
	except:
		i = 1
	override_sample_rate = str(DESIRED_RATES[i])

	# ressample if required
	if not wav_sample_rate in DESIRED_RATES or wav_audio_format != 1 or wav_bits_per_sample != 16:
		filename_temp = filename_wav + "temp.wav"
		util.RemoveFile(filename_temp)
		util.RenameFile(filename_wav, filename_temp)
		SndFileConvert = GetSndFileConvert()
		commandLine = [SndFileConvert, "-override-sample-rate=" + override_sample_rate, "-pcm16", filename_temp, filename_wav]
		util.RunCommandLine(commandLine)
		util.RemoveFile(filename_temp)
		util.LogDebug("Converted WAV <{}>:\n FORMAT:{} CHANNELS:{} SAMPLE_RATE:{} BITS_PER_SAMPLE:{}".format(
			filename_wav, wav_audio_format, wav_channel_count, wav_sample_rate, wav_bits_per_sample
		)
	)

	return True

def WAV2MCADPCM(filename_wav, filename_mcadpcm):
	""" creates MCADPCM from WAVE """

	VGAudioCli = GetVGAudioCli()
	commandLine = [VGAudioCli, "-c", filename_wav, filename_mcadpcm]
	util.RunCommandLine(commandLine)

def WAV2FUZ(filename_wav, filename_fuz):
	""" creates FUZ from WAVE """

	# Only getting channel 0 from WAVE when creating OPUS
	VGAudioCli = GetVGAudioCli()
	commandLine = [VGAudioCli, "-c", "--opusheader",  "Skyrim", "-i:0", filename_wav, filename_fuz]
	util.RunCommandLine(commandLine)

def ConvertSound_Internal(filepath_without_extension):
	""" Converts PC SSE sound files to be compatible with NX SSE supported codecs """

	filename_mcadpcm = filepath_without_extension + ".mcadpcm"
	filename_wav = filepath_without_extension + ".wav"
	filename_xwm = filepath_without_extension + ".xwm"
	filename_lip = filepath_without_extension + ".lip"
	filename_fuz = filepath_without_extension + ".fuz"

	has_wav = os.path.exists(filename_wav)
	has_xwm = os.path.exists(filename_xwm)
	has_lip = os.path.exists(filename_lip)
	has_fuz = os.path.exists(filename_fuz)

	is_nxopus = "\\sound\\voice\\" in filepath_without_extension.lower()

	util.LogDebug("Convert Sound <{}> WAV:{} XWM:{} LIP:{} FUZ:{}".format(filepath_without_extension, has_wav, has_xwm, has_lip, has_fuz))

	# FUZ files always have precedence over loose WAV, XWM, LIP
	if has_fuz:
		try:
			with open(filename_fuz, "rb") as fuz_file:
				fuz_file.seek(0x08)
				lip_size = int.from_bytes(fuz_file.read(0x04), byteorder = 'little', signed = False)
				lip_data = fuz_file.read(lip_size)
				audio_data = fuz_file.read()

				# save LIP contents
				try:
					if lip_size == 0:
						util.LogDebug("INFO: FUZ {} has no LIP data.".format(filename_fuz))
					else:
						with open(filename_lip, "wb") as lip_file:
							lip_file.write(lip_data)
							has_lip = True
							util.LogDebug("INFO: LIP created on disk from FUZ {}.".format(filename_fuz))

				except:
					util.LogInfo("ERROR: failed to create intermediate LIP <{}>.".format(filename_xwm))
					return False

				# save AUDIO contents
				try:
					audio_format = audio_data[0x08:0x0C].decode()
					if audio_format == "WAVE":
						has_wav = True
						filename_audio = filename_wav
					elif audio_format == "XWMA":
						has_xwm = True
						filename_audio = filename_xwm
					with open(filename_audio, "wb") as audio_file:
						audio_file.write(audio_data)
						util.LogDebug("INFO: XWM created on disk from FUZ {}.".format(filename_fuz))

				except:
					util.LogInfo("ERROR: failed to create intermediate WMV <{}>.".format(filename_xwm))
					return False

		except:
			util.LogInfo("ERROR: failed to open FUZ <{}>.".format(filename_lip))
			return False

	# Convert the XWM to WAV
	if has_xwm:
		XWM2WAV(filename_xwm, filename_wav)

	# Normalize the WAV format
	if not WAV2PCM16WAV(filename_xwm, filename_wav, is_nxopus):
		return False

	# Convert the normalized WAV to final format
	if is_nxopus:
		WAV2FUZ(filename_wav, filename_fuz)
	else:
		WAV2MCADPCM(filename_wav, filename_mcadpcm)

	# clean up temporary files
	util.RemoveFile(filename_wav)
	if has_xwm:
		util.RemoveFile(filename_xwm)
	if has_lip:
		util.RemoveFile(filename_lip)
	if has_fuz and not is_nxopus:
		util.RemoveFile(filename_fuz)

	return True

def ConvertSound(target, filepath_without_extension):
	return ConvertSound_Internal(filepath_without_extension)

def ConvertSoundAsync(target, filename, logname, ret):
	util.InitialiseMPLog(logname)
	retVal = ConvertSound(target, filename)
	ret["retVal"] = retVal

if __name__ == '__main__':
	import sys
	filepath = sys.argv[1]
	util.InitialiseLog(filepath + ".log")
	util.StartTimer()
	util.LogInfo("Skyrim-NX-Toolkit {} - convert_txt".format(util.GetToolkitVersion()))
	ConvertSound_Internal(filepath)
	util.EndTimer()