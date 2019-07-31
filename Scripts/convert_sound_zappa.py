#! python3

import os
import util
import time
import toolkit_config
from io import BytesIO

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

def XWM2WAV(filename_xwm, filename_wav, isNxOpus):
	""" converts the XWM file to WAV and prepare the WAV file to be a proper PCM16 for VGAudioCli """

	xWMAEncode = GetxWMAEncode()
	commandLine = [xWMAEncode, filename_xwm, filename_wav]

	util.RunCommandLine(commandLine)

	with open(filename_wav, "rb") as wav_file:
		wav_header = wav_file.read(0xFF)
		wav_format = wav_header[0x08:0x0C].decode()

	# check for a collateral case where Mod Authors save XWM with WAV extension
	if wav_format == "XWMA":
		util.LogInfo("Zappa says, <{}> has WAV extension but is a XWMA. Fixing.".format(filename_wav))
		filename_temp = filename_wav + "temp.wav"
		util.RemoveFile(filename_temp)
		util.RenameFile(filename_wav, filename_temp)
		commandLine = [xWMAEncode, filename_temp, filename_wav]
		util.RunCommandLine(commandLine)
		util.RemoveFile(filename_temp)

		with open(filename_wav, "rb") as wav_file:
			wav_header = wav_file.read(0xFF)
			wav_format = wav_header[0x08:0x0C].decode()

	wav_audio_format = int.from_bytes(wav_header[0x14:0x16], byteorder = 'little', signed = False)
	wav_channel_count = int.from_bytes(wav_header[0x16:0x18], byteorder = 'little', signed = False)
	wav_sample_rate = int.from_bytes(wav_header[0x18:0x1C], byteorder = 'little', signed = False)
	wav_bits_per_sample = int.from_bytes(wav_header[0x22:0x24], byteorder = 'little', signed = False)

	#
	# make the WAV file compatible with VGAudioCLi
	#

	# get the closest ressampling RATE
	RATES = [24000, 48000] if isNxOpus else [22050, 44100]
	try:
		i = 0
		while wav_sample_rate >= RATES[i]:
			i += 1
	except:
		i = 1
	override_sample_rate = str(RATES[i])

	#
	# Possible temporary fix for issues with Faye Mod which has voices in stereo
	#
	if (isNxOpus and wav_channel_count == 1) or wav_audio_format != 1 or wav_bits_per_sample != 16:
		filename_temp = filename_wav + "temp.wav"
		util.RemoveFile(filename_temp)
		util.RenameFile(filename_wav, filename_temp)
		SndFileConvert = GetSndFileConvert()
		commandLine = [SndFileConvert, "-override-sample-rate=" + override_sample_rate, "-pcm16", filename_temp, filename_wav]
		util.RunCommandLine(commandLine)
		util.RemoveFile(filename_temp)

		# really need to open one last time...
		with open(filename_wav, "rb") as wav_file:
			wav_header = wav_file.read(0xFF)
			wav_sample_rate = int.from_bytes(wav_header[0x18:0x1C], byteorder = 'little', signed = False)
			wav_bits_per_sample = int.from_bytes(wav_header[0x22:0x24], byteorder = 'little', signed = False)

	wav_channel_count = int.from_bytes(wav_header[0x16:0x18], byteorder = 'little', signed = False)
	try:
		data_size_offset = wav_header.find(b'\x64\x61\x74\x61') + 0x04
		wav_data_size = int.from_bytes(wav_header[data_size_offset:data_size_offset+0x04], byteorder = 'little', signed = False)
		wav_duration_ms = int(float(wav_data_size * 1000) / float(wav_sample_rate * wav_channel_count * wav_bits_per_sample / 8))
	except:
		wav_duration_ms = 0

	util.LogDebug(
		"Converted WAVE <{}>:\n  DURATION:{} FORMAT:{} CHANNELS:{} SAMPLE_RATE:{} BITS_PER_SAMPLE:{} DATA_SIZE:{}".format(
			filename_wav, wav_duration_ms, wav_audio_format, wav_channel_count, wav_sample_rate, wav_bits_per_sample, wav_data_size)
	)

	return (wav_channel_count, wav_duration_ms)

def WAV2NXOPUS(filename_wav, filename_nxopus):
	""" creates NXOPUS from WAVE """

	VGAudioCli = GetVGAudioCli()
	commandLine = [VGAudioCli, "-c", "--opusheader",  "Standard", filename_wav, filename_nxopus]
	util.RunCommandLine(commandLine)

def WAV2DSP(filename_wav, filename_dsp0, filename_dsp1, wav_channel_count = 1):
	""" creates DSPMCADPCM from WAVE (2 files if stereo) but unfortunately in big-endian """

	VGAudioCli = GetVGAudioCli()
	commandLine = [VGAudioCli, "-i:0", filename_wav, filename_dsp0]
	util.RunCommandLine(commandLine)

	if wav_channel_count > 1:
		commandLine = [VGAudioCli, "-i:1", filename_wav, filename_dsp1]
		util.RunCommandLine(commandLine)

def ConvertDSP(dsp_data, base):
	""" fix from big-endian to little-endian. not 100% correct as there are some 16 bit fields on the header but as far as I found all 0x00 """

	dsp_data[base+0x00:base+0x19:4], dsp_data[base+0x01:base+0x1A:4], dsp_data[base+0x02:base+0x1B:4], dsp_data[base+0x03:base+0x1C:4] = \
	dsp_data[base+0x03:base+0x1C:4], dsp_data[base+0x02:base+0x1B:4], dsp_data[base+0x01:base+0x1A:4], dsp_data[base+0x00:base+0x19:4]
	dsp_data[base+0x1C:base+0x5F:2], dsp_data[base+0x1D:base+0x60:2] = \
	dsp_data[base+0x1D:base+0x60:2], dsp_data[base+0x1C:base+0x5F:2]

def NXOPUS2FUZ(filename_nxopus, channel_count, sound_duration, sound_file):
	""" adds required NX SSE header to a nxopus sound """

	with open(filename_nxopus, "rb") as nxopus_file: nxopus_data = bytearray(nxopus_file.read())
	nxopus_size = len(nxopus_data)

	nx_sse_opus_header_size = b'\x14\x00\x00\x00'
	nx_sse_opus_signature = b'\x0A\x8D\xD5\xFF'

	sound_file.write(nx_sse_opus_signature)
	sound_file.write(sound_duration.to_bytes(4, byteorder = 'little', signed = False))
	sound_file.write(channel_count.to_bytes(4, byteorder = 'little', signed = False))
	sound_file.write(nx_sse_opus_header_size)
	sound_file.write(nxopus_size.to_bytes(4, byteorder = 'little', signed = False))
	sound_file.write(nxopus_data)

def DSP2MCADPCM(filename_dsp0, filename_dsp1, channel_count, sound_file):
	""" creates a MCADPCM file from DSPADPCM ones """

	with open(filename_dsp0, "rb") as dsp0_file: dsp0_data = bytearray(dsp0_file.read())
	dsp0_size = len(dsp0_data)
	ConvertDSP(dsp0_data, 0x00)

	if channel_count > 1:
		with open(filename_dsp1, "rb") as dsp1_file: dsp1_data = bytearray(dsp1_file.read())
		dsp1_size = len(dsp1_data)
		dsp1_offset = 0x14 + dsp0_size
		ConvertDSP(dsp1_data, 0x00)

		header_stereo = b'\x02\x00\x00\x00\x14\x00\x00\x00'
		sound_file.write(header_stereo)
		sound_file.write(dsp0_size.to_bytes(4, byteorder = 'little', signed = False))
		sound_file.write(dsp1_offset.to_bytes(4, byteorder = 'little', signed = False))
		sound_file.write(dsp1_size.to_bytes(4, byteorder = 'little', signed = False))
		sound_file.write(dsp0_data)
		sound_file.write(dsp1_data)

	else:
		header_single = b'\x01\x00\x00\x00\x0C\x00\x00\x00'
		sound_file.write(header_single)
		sound_file.write(dsp0_size.to_bytes(4, byteorder = 'little', signed = False))
		sound_file.write(dsp0_data)

def ConvertSound_Internal(filepath_without_extension):
	""" Converts PC SSE sound files to be compatible with NX SSE supported codecs """

	filename_mcadpcm = filepath_without_extension + ".mcadpcm"
	filename_nxopus = filepath_without_extension + ".lopus"
	filename_dsp0 = filepath_without_extension + "_CH0_.dsp"
	filename_dsp1 = filepath_without_extension + "_CH1_.dsp"
	filename_wav = filepath_without_extension + ".wav"
	filename_xwm = filepath_without_extension + ".xwm"
	filename_lip = filepath_without_extension + ".lip"
	filename_fuz = filepath_without_extension + ".fuz"

	has_wav = os.path.exists(filename_wav)
	has_xwm = os.path.exists(filename_xwm)
	has_lip = os.path.exists(filename_lip)
	has_fuz = os.path.exists(filename_fuz)

	# get the desired CODEC
	if "\\music\\" in filepath_without_extension.lower():
		codec = toolkit_config.get_setting("Sounds", "music")
	elif "\\sound\\fx\\" in filepath_without_extension.lower():
		codec = toolkit_config.get_setting("Sounds", "fx")
	elif "\\sound\\voice\\" in filepath_without_extension.lower():
		codec = toolkit_config.get_setting("Sounds", "voice")
	else:
		codec = "nxopus"
	is_nxopus = codec.lower() == "nxopus"

	util.LogDebug("Convert Sound <{}> WAV:{} XWM:{} LIP:{} FUZ:{} CODEC:{}".format(filepath_without_extension, has_wav, has_xwm, has_lip, has_fuz, codec))

	# FUZ files always have precedence over loose WAV, XWM or LIP
	lip_size = 0
	if has_fuz:
		with open(filename_fuz, "rb") as fuz_file:
			fuz_file.seek(0x08)
			lip_size = int.from_bytes(fuz_file.read(0x04), byteorder = 'little', signed = False)
			lip_data = fuz_file.read(lip_size)

			util.LogDebug("FUZ {} has a 0 bytes LIP data.".format(filename_fuz))

			with open(filename_xwm, "wb") as xwm_file:
				xwm_file.write(fuz_file.read())
				has_xwm = True

			util.LogDebug("XWM created on disk from FUZ {}.".format(filename_fuz))

	# Load LIP from disk in the rare case the LIP in FUZ is empty
	if lip_size == 0 and has_lip:
		with open(filename_lip, "rb") as lip_file:
			lip_data = lip_file.read()
			lip_size = len(lip_data)

	# Convert the XWM to WAV
	(channel_count, sound_duration) = XWM2WAV(filename_xwm, filename_wav, is_nxopus)

	# Converte the WAV to NXOPUS or MCADPCM
	if is_nxopus and channel_count == 1:
		WAV2NXOPUS(filename_wav, filename_nxopus)
	else:
		WAV2DSP(filename_wav, filename_dsp0, filename_dsp1, channel_count)

	# write a FUZ container
	if lip_size > 0 or is_nxopus and channel_count == 1:
		lip_padding = lip_size % 4
		if lip_padding != 0: lip_padding = 4 - lip_padding
		voice_offset = 0x10 + lip_size + lip_padding

		fuz_nx_payload = BytesIO()
		header_fuz = b'\x46\x55\x5A\x45\x01\x00\x00\x00'
		fuz_nx_payload.write(header_fuz)
		fuz_nx_payload.write(lip_size.to_bytes(4, byteorder = 'little', signed = False))
		fuz_nx_payload.write(voice_offset.to_bytes(4, byteorder = 'little', signed = False))
		if lip_size > 0: fuz_nx_payload.write(lip_data)
		fuz_nx_payload.write(b'\x00' * lip_padding)

		# write the SOUND content and force stereo to MCADPCM
		if is_nxopus and channel_count == 1:
			NXOPUS2FUZ(filename_nxopus, channel_count, sound_duration, fuz_nx_payload)
		else:
			DSP2MCADPCM(filename_dsp0, filename_dsp1, channel_count, fuz_nx_payload)

		# pad the FUZ content to the closest uint32
		fuz_padding = fuz_nx_payload.getbuffer().nbytes % 4
		if fuz_padding != 0: fuz_padding = 4 - fuz_padding
		fuz_nx_payload.write(b'\x00' * fuz_padding)

		with open(filename_fuz, "wb") as fuz_nx_file:
			fuz_nx_file.write(fuz_nx_payload.getbuffer())

	# write a MCADPCM container
	else:
		with open(filename_mcadpcm, "wb") as mcadpcm_file:
			DSP2MCADPCM(filename_dsp0, filename_dsp1, channel_count, mcadpcm_file)

	# clean up temporary files
	util.RemoveFile(filename_wav)
	if has_xwm:
		util.RemoveFile(filename_xwm)
	if has_lip:
		util.RemoveFile(filename_lip)
	if (is_nxopus and channel_count == 1):
		util.RemoveFile(filename_nxopus)
	else:
		util.RemoveFile(filename_dsp0)
		if channel_count > 1:
			util.RemoveFile(filename_dsp1)
		if has_fuz and lip_size == 0:
			util.RemoveFile(filename_fuz)

	return (channel_count > 0)

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