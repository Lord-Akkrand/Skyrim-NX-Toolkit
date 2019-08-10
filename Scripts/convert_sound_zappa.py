#! python3

import os
import util
import time

def GetVGAudioCli():
	utilities_path = util.GetUtilitiesPath()
	VGAudioCli = os.path.join(utilities_path, "VGAudioCli.exe")
	return VGAudioCli

def GetFFMpeg():
	utilities_path = util.GetUtilitiesPath()
	FFMpeg = os.path.join(utilities_path, "ffmpeg.exe")
	return FFMpeg

def NormalizeAudio(filename_input_audio, filename_output_wav, is_nxopus):
	""" Normalizes the WAV file to be a proper PCM16 with a correct sample rate for VGAudioCli """

	FFMpeg = GetFFMpeg()
	filename_temp = filename_input_audio[:-4] + "TEMP" + filename_input_audio[-4:]
	if is_nxopus:
		commandLine = [FFMpeg, "-hide_banner", "-y", "-i", filename_temp, "-ac", "1", "-ar", "48000", filename_output_wav]
	else:
		commandLine = [FFMpeg, "-hide_banner", "-y", "-i", filename_temp, "-ar", "44100", filename_output_wav]
	util.RenameFile(filename_input_audio, filename_temp)
	util.RunCommandLine(commandLine)
	util.RemoveFile(filename_temp)
	util.LogDebug("INFO: Normalized WAV <{}>".format(filename_output_wav))

def ConvertAudio(filename_wav, is_nxopus):
	""" creates MCADPCM from WAVE """

	VGAudioCli = GetVGAudioCli()
	filename_temp = filename_wav[:-4]
	if is_nxopus:
		commandLine = [VGAudioCli, "-c", "--opusheader",  "Skyrim", "-i:0", filename_wav, filename_temp + '.fuz']
	else:
		commandLine = [VGAudioCli, "-c", filename_wav, filename_temp + '.mcadpcm']
	util.RunCommandLine(commandLine)
	util.RemoveFile(filename_wav)
	util.LogDebug("INFO: Converted WAV <{}>".format(filename_wav))

def ConvertSound_Internal(filepath_without_extension):
	""" Converts PC SSE sound files to be compatible with NX SSE supported codecs """

	filename_wav = filepath_without_extension + ".wav"
	filename_xwm = filepath_without_extension + ".xwm"
	filename_lip = filepath_without_extension + ".lip"
	filename_fuz = filepath_without_extension + ".fuz"

	has_wav = os.path.exists(filename_wav)
	has_xwm = os.path.exists(filename_xwm)
	has_lip = os.path.exists(filename_lip)
	has_fuz = os.path.exists(filename_fuz)

	util.LogDebug("INFO: Convert Sound <{}> WAV:{} XWM:{} LIP:{} FUZ:{}".format(filepath_without_extension, has_wav, has_xwm, has_lip, has_fuz))

	# UNFUZ Audio
	if has_fuz:
		try:
			with open(filename_fuz, "rb") as fuz_file:
				fuz_file.seek(0x08)
				lip_size = int.from_bytes(fuz_file.read(0x04), byteorder = 'little', signed = False)
				lip_data = fuz_file.read(lip_size)
				audio_data = fuz_file.read()
		except:
			util.LogInfo("ERROR: failed to open FUZ <{}>.".format(filename_lip))
			return False

		# determine AUDIO format
		audio_format = audio_data[0x08:0x0C]
		if audio_format == b'WAVE':
			has_wav = True
			filename_audio = filename_wav
		elif audio_format == b'XWMA':
			has_xwm = True
			filename_audio = filename_xwm
		else:
			util.LogInfo("ERROR: unknown audio format {} on FUZ <{}>.".format(audio_format, filename_fuz))
			return False

		# save LIP contents
		if lip_size > 0:
			try:
				with open(filename_lip, "wb") as lip_file:
					lip_file.write(lip_data)
					has_lip = True
					util.LogDebug("INFO: LIP created on disk from FUZ {}.".format(filename_fuz))
			except:
				util.LogDebug("ERROR: failed to create intermediate LIP <{}>.".format(filename_lip))
				return False

		# save AUDIO contents
		try:
			with open(filename_audio, "wb") as audio_file:
				audio_file.write(audio_data)
				util.LogDebug("INFO: AUDIO created on disk from FUZ {}.".format(filename_fuz))
		except:
		 	util.LogDebug("ERROR: failed to create intermediate AUDIO <{}>.".format(filename_audio))
		 	return False

		# get rid of the source PC FUZ file
		util.RemoveFile(filename_fuz)

	elif has_xwm:
		filename_audio = filename_xwm

	elif has_wav:
		filename_audio = filename_wav

	else:
		util.LogDebug("PANIC: IT SHOULD NEVER REACH THIS BRANCH...")
		return False

	# Force anything VOICE to use OPUS codec
	is_nxopus = "\\sound\\voice\\" in filepath_without_extension.lower()

	# Normalize Audio
	NormalizeAudio(filename_audio, filename_wav, is_nxopus)

	# Convert Audio
	ConvertAudio(filename_wav, is_nxopus)

	# clean up LIP file if any
	if has_lip:
		util.RemoveFile(filename_lip)

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
	util.SetScriptPath(sys.argv[2])
	util.LogInfo("Skyrim-NX-Toolkit {} - convert_sound_zappa".format(util.GetToolkitVersion()))
	retValue = ConvertSound_Internal(filepath)
	tempLog = util.GetTempLog()
	for msg in tempLog:
		print(msg)
	if not retValue:
		sys.exit(1)
	sys.exit(0)