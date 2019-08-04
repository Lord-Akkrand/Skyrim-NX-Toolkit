#! python3

import os
import util
import time
from io import BytesIO
import toolkit_config

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
			wav_header = wav_file.read(0xFF)
			wav_format = wav_header[0x08:0x0C].decode()
	except:
		util.LogInfo("ERROR: failed to create intermediate WAV <{}>.".format(filename_wav))
		return (True, None, None)

	# check for a collateral case where Mod Authors save XWM with WAV extension
	if wav_format == "XWMA":
		util.LogInfo("WARNING: <{}> has WAV extension but is a XWMA. Fixing it.".format(filename_wav))
		filename_temp = filename_wav + "temp.wav"
		util.RemoveFile(filename_temp)
		util.RenameFile(filename_wav, filename_temp)
		xWMAEncode = GetxWMAEncode()
		commandLine = [xWMAEncode, filename_temp, filename_wav]
		util.RunCommandLine(commandLine)
		util.RemoveFile(filename_temp)

		try:
			with open(filename_wav, "rb") as wav_file:
				wav_header = wav_file.read(0xFF)
				wav_format = wav_header[0x08:0x0C].decode()
		except:
			util.LogInfo("ERROR: failed to fix collateral case on WAV <{}>.".format(filename_wav))
			return (True, None, None)

	wav_audio_format = int.from_bytes(wav_header[0x14:0x16], byteorder = 'little', signed = False)
	wav_sample_rate = int.from_bytes(wav_header[0x18:0x1C], byteorder = 'little', signed = False)
	wav_bits_per_sample = int.from_bytes(wav_header[0x22:0x24], byteorder = 'little', signed = False)

	#
	# make the WAV file compatible with VGAudioCLi
	#
	# OPUS CODEC requires 24000 or 48000 sample rates from a PCM16 stream
	# DSPADPCM CODEC requires 22050 or 44100 sample rates from a PCM16 stream
	#

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
	if (isNxOpus and not wav_sample_rate in DESIRED_RATES) or wav_audio_format != 1 or wav_bits_per_sample != 16:
		filename_temp = filename_wav + "temp.wav"
		util.RemoveFile(filename_temp)
		util.RenameFile(filename_wav, filename_temp)
		SndFileConvert = GetSndFileConvert()
		commandLine = [SndFileConvert, "-override-sample-rate=" + override_sample_rate, "-pcm16", filename_temp, filename_wav]
		util.RunCommandLine(commandLine)
		util.RemoveFile(filename_temp)

		# really need to open one last time to get the metadata right
		try:
			with open(filename_wav, "rb") as wav_file:
				wav_header = wav_file.read(0xFF)
				wav_sample_rate = int.from_bytes(wav_header[0x18:0x1C], byteorder = 'little', signed = False)
				wav_bits_per_sample = int.from_bytes(wav_header[0x22:0x24], byteorder = 'little', signed = False)
		except:
			util.LogInfo("ERROR: failed to create normalized WAV <{}>.".format(filename_wav))
			return (True, None, None)

	wav_channel_count = int.from_bytes(wav_header[0x16:0x18], byteorder = 'little', signed = False)
	try:
		data_size_offset = wav_header.find(b'\x64\x61\x74\x61') + 0x04
		wav_data_size = int.from_bytes(wav_header[data_size_offset:data_size_offset+0x04], byteorder = 'little', signed = False)
		wav_duration_ms = int(float(wav_data_size * 1000) / float(wav_sample_rate * wav_channel_count * wav_bits_per_sample / 8))
	except:
		wav_duration_ms = 0

	util.LogDebug(
		"Converted WAV <{}>:\n  DURATION:{} FORMAT:{} CHANNELS:{} SAMPLE_RATE:{} BITS_PER_SAMPLE:{} DATA_SIZE:{}".format(
			filename_wav, wav_duration_ms, wav_audio_format, wav_channel_count, wav_sample_rate, wav_bits_per_sample, wav_data_size)
	)

	return (False, wav_channel_count, wav_duration_ms)

def WAV2NXOPUS(filename_wav, filename_nxopus):
	""" creates NXOPUS from WAVE """

	# Only getting channel 0 from WAVE when creating OPUS. Vanilla Skyrim mainly use NXOPUS on mono sources (voice folder)
	VGAudioCli = GetVGAudioCli()
	commandLine = [VGAudioCli, "-c", "--opusheader",  "Standard", "-i:0", filename_wav, filename_nxopus]
	util.RunCommandLine(commandLine)

def WAV2DSP(filename_wav, filename_dsp0, filename_dsp1, channel_count = 1):
	""" creates DSPMCADPCM from WAVE (2 files if stereo) but unfortunately in big-endian """

	VGAudioCli = GetVGAudioCli()
	commandLine = [VGAudioCli, "-c", "-i:0", filename_wav, filename_dsp0]
	util.RunCommandLine(commandLine)

	if channel_count > 1:
		commandLine = [VGAudioCli, "-c", "-i:1", filename_wav, filename_dsp1]
		util.RunCommandLine(commandLine)

def DSP2LITTLE_ENDIAN(dsp_data, base):
	""" swaps DSPMCADPM header data from big-endian to little-endian

		typedef struct
		{
			uint32_t num_samples;
			uint32_t num_nibbles;
			uint32_t sample_rate;
			uint16_t loop_flag;
			uint16_t format; /* 0 for ADPCM */
			uint32_t loop_start;
			uint32_t loop_end;
			uint32_t ca;
			int16_t coef[16];
			int16_t gain;
			int16_t ps;
			int16_t hist1;
			int16_t hist2;
			int16_t loop_ps;
			int16_t loop_hist1;
			int16_t loop_hist2;
			uint16_t pad[11];
		} ADPCM_HEADER;
	"""

	# swaps num_samples, num_nibbles, sample_rate
	dsp_data[base+0x00:base+0x0C:4], dsp_data[base+0x01:base+0x0D:4], dsp_data[base+0x02:base+0x0E:4], dsp_data[base+0x03:base+0x0F:4] = \
	dsp_data[base+0x03:base+0x0F:4], dsp_data[base+0x02:base+0x0E:4], dsp_data[base+0x01:base+0x0D:4], dsp_data[base+0x00:base+0x0C:4]

	# swaps loop_flag, format
	dsp_data[base+0x0C:base+0x10:2], dsp_data[base+0x0D:base+0x11:2] = \
	dsp_data[base+0x0D:base+0x11:2], dsp_data[base+0x0C:base+0x10:2]

	# swaps loop_start, loop_end, ca
	dsp_data[base+0x10:base+0x1C:4], dsp_data[base+0x11:base+0x1D:4], dsp_data[base+0x12:base+0x1E:4], dsp_data[base+0x13:base+0x1F:4] = \
	dsp_data[base+0x13:base+0x1F:4], dsp_data[base+0x12:base+0x1E:4], dsp_data[base+0x11:base+0x1D:4], dsp_data[base+0x10:base+0x1C:4]

	# swaps all 16 coef, gain, ps, hist1, hist2, loop_ps, loop_hist1, loop_hist2
	dsp_data[base+0x1C:base+0x5F:2], dsp_data[base+0x1D:base+0x60:2] = \
	dsp_data[base+0x1D:base+0x60:2], dsp_data[base+0x1C:base+0x5F:2]

def NXOPUS2FUZ(filename_nxopus, channel_count, sound_duration_ms, sound_file):
	""" adds required NX SSE header to a nxopus sound """

	try:
		with open(filename_nxopus, "rb") as nxopus_file:
			nxopus_data = bytearray(nxopus_file.read())
			nxopus_size = len(nxopus_data)
	except:
		util.LogInfo("ERROR: failed to open intermediate NXOPUS <{}>.".format(filename_nxopus))
		return True

	nx_sse_opus_header_size = b'\x14\x00\x00\x00'
	nx_sse_opus_signature = b'\x0A\x8D\xD5\xFF'

	sound_file.write(nx_sse_opus_signature)
	sound_file.write(sound_duration_ms.to_bytes(4, byteorder = 'little', signed = False))
	sound_file.write(channel_count.to_bytes(4, byteorder = 'little', signed = False))
	sound_file.write(nx_sse_opus_header_size)
	sound_file.write(nxopus_size.to_bytes(4, byteorder = 'little', signed = False))
	sound_file.write(nxopus_data)

	return False

def DSP2MCADPCM(filename_dsp0, filename_dsp1, channel_count, sound_file):
	""" creates a MCADPCM file from DSPADPCM ones """

	try:
		with open(filename_dsp0, "rb") as dsp0_file:
			dsp0_data = bytearray(dsp0_file.read())
			dsp0_size = len(dsp0_data)
			DSP2LITTLE_ENDIAN(dsp0_data, 0x00)
	except:
		util.LogInfo("ERROR: failed to open intermediate DSP <{}>.".format(filename_dsp0))
		return True

	if channel_count > 1:
		try:
			with open(filename_dsp1, "rb") as dsp1_file:
				dsp1_data = bytearray(dsp1_file.read())
				dsp1_size = len(dsp1_data)
				dsp1_offset = 0x14 + dsp0_size
				DSP2LITTLE_ENDIAN(dsp1_data, 0x00)
		except:
			util.LogInfo("ERROR: failed to open intermediate DSP <{}>.".format(filename_dsp1))
			return True

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

	return False

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
		try:
			with open(filename_fuz, "rb") as fuz_file:
				fuz_file.seek(0x08)
				lip_size = int.from_bytes(fuz_file.read(0x04), byteorder = 'little', signed = False)
				lip_data = fuz_file.read(lip_size)

				if lip_size == 0:
					util.LogDebug("INFO: FUZ {} has a 0 bytes LIP data.".format(filename_fuz))

				try:
					with open(filename_xwm, "wb") as xwm_file:
						xwm_file.write(fuz_file.read())
						has_xwm = True
				except:
					util.LogInfo("ERROR: failed to create intermediate WMV <{}>.".format(filename_xwm))
					return False

				util.LogDebug("INFO: XWM created on disk from FUZ {}.".format(filename_fuz))
		except:
			util.LogInfo("ERROR: failed to open FUZ <{}>.".format(filename_lip))
			return False

	# Load LIP from disk in the rare case the LIP in FUZ is empty
	if lip_size == 0 and has_lip:
		try:
			with open(filename_lip, "rb") as lip_file:
				lip_data = lip_file.read()
				lip_size = len(lip_data)
		except:
			util.LogInfo("ERROR: failed to open LIP <{}>.".format(filename_lip))
			return False

	# Convert the XWM to WAV
	if has_xwm:
		XWM2WAV(filename_xwm, filename_wav)

	# Normalizes the WAV format
	(err, channel_count, sound_duration_ms) = WAV2PCM16WAV(filename_xwm, filename_wav, is_nxopus)
	if err:
		return False

	# Converte the WAV to NXOPUS or MCADPCM
	if is_nxopus:
		WAV2NXOPUS(filename_wav, filename_nxopus)
	else:
		WAV2DSP(filename_wav, filename_dsp0, filename_dsp1, channel_count)

	# write a FUZ container
	if lip_size > 0 or is_nxopus:
		lip_padding = lip_size % 4
		if lip_padding != 0: lip_padding = 4 - lip_padding
		voice_offset = 0x10 + lip_size + lip_padding

		# write the FUZ header
		#
		# on PC a FUZ header has 0x0A bytes. NX adds an additional uint32_t to header end
		# it represents the offset where the SOUND content starts as NX pads LIP content
		#
		fuz_nx_payload = BytesIO()
		header_fuz = b'\x46\x55\x5A\x45\x01\x00\x00\x00'
		fuz_nx_payload.write(header_fuz)
		fuz_nx_payload.write(lip_size.to_bytes(4, byteorder = 'little', signed = False))
		fuz_nx_payload.write(voice_offset.to_bytes(4, byteorder = 'little', signed = False))

		# write the LIP content
		if lip_size > 0: fuz_nx_payload.write(lip_data)
		fuz_nx_payload.write(b'\x00' * lip_padding)

		# write the SOUND content
		if is_nxopus:
			err = NXOPUS2FUZ(filename_nxopus, channel_count, sound_duration_ms, fuz_nx_payload)
		else:
			err = DSP2MCADPCM(filename_dsp0, filename_dsp1, channel_count, fuz_nx_payload)
		if err:
			return False

		# pad the FUZ content to the closest uint32
		fuz_padding = fuz_nx_payload.getbuffer().nbytes % 4
		if fuz_padding != 0: fuz_padding = 4 - fuz_padding
		fuz_nx_payload.write(b'\x00' * fuz_padding)

		try:
			with open(filename_fuz, "wb") as fuz_nx_file:
				fuz_nx_file.write(fuz_nx_payload.getbuffer())
		except:
			util.LogInfo("ERROR: failed to create final FUZ <{}>.".format(filename_fuz))
			return False

	# write a MCADPCM container
	else:
		try:
			with open(filename_mcadpcm, "wb") as mcadpcm_file:
				DSP2MCADPCM(filename_dsp0, filename_dsp1, channel_count, mcadpcm_file)
		except:
			util.LogInfo("ERROR: failed to create final MCADPCM <{}>.".format(filename_mcadpcm))
			return False

	# clean up temporary files
	util.RemoveFile(filename_wav)
	if has_xwm:
		util.RemoveFile(filename_xwm)
	if has_lip:
		util.RemoveFile(filename_lip)
	if is_nxopus:
		util.RemoveFile(filename_nxopus)
	else:
		util.RemoveFile(filename_dsp0)
		if channel_count > 1:
			util.RemoveFile(filename_dsp1)
		if has_fuz and lip_size == 0:
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