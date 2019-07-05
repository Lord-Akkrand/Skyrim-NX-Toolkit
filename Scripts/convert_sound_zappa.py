#! python3

import os
import util
import soundfile

def GetVGAudioCli():
	utilities_path = util.GetUtilitiesPath()
	VGAudioCli = os.path.join(utilities_path, "Sound", "VGAudioCli.exe")
	return VGAudioCli

def GetxWMAEncode():
	utilities_path = util.GetUtilitiesPath()
	xWMAEncode = os.path.join(utilities_path, "Sound", "xWMAEncode.exe")
	return xWMAEncode

def XWM2WAV(filename_xwm, filename_wav):
	xWMAEncode = GetxWMAEncode()
	commandLine = [xWMAEncode, filename_xwm, filename_wav]
	util.RunCommandLine(commandLine)

def WAV2DSP(filename_wav, filename_dsp0, filename_dsp1):
	with open(filename_wav, "rb") as wav_file:
		wav_header = wav_file.read(0x25)
		wav_format = wav_header[0x08:0x0C].decode()
		wav_audio_format = int.from_bytes(wav_header[0x14:0x16], byteorder = 'little', signed = False)
		wav_channel_count = int.from_bytes(wav_header[0x16:0x18], byteorder = 'little', signed = False)
		wav_bits_per_sample = int.from_bytes(wav_header[0x22:0x24], byteorder = 'little', signed = False)

	# checking for a collateral case where Mod Authors save XWM with WAV extension
	if wav_format == "XWMA":
		util.LogInfo("Warning, <{}> has WAV extension but is a XWMA. Fixing.".format(filename_wav))
		filename_temp = filename_wav + ".TEMP"
		util.RenameFile(filename_wav, filename_temp)
		XWM2WAV(filename_temp, filename_wav)
		util.RemoveFile(filename_temp)

	# make the WAV file compatible with VGAudioCLi whenever required
	elif wav_audio_format != 1 or not (wav_bits_per_sample == 8 or wav_bits_per_sample == 16):
		util.LogInfo("Warning, <{}> isn't compatible with VGAudioCLi. Fixing.".format(filename_wav))
		wav_data, wav_samplerate = soundfile.read(filename_wav)
		soundfile.write(filename_wav, wav_data, wav_samplerate, subtype='PCM_16')

	# relying on VGAudioCli to create the DSP streams
	VGAudioCli = GetVGAudioCli()
	commandLine = [VGAudioCli, "-i:0", filename_wav, filename_dsp0]
	util.RunCommandLine(commandLine)
	if wav_channel_count > 1:
		commandLine = [VGAudioCli, "-i:1", filename_wav, filename_dsp1]
		util.RunCommandLine(commandLine)
		wav_channel_count = 2
	return wav_channel_count

def ConvertDSP(dsp_data, base):
	dsp_data[base+0x00:base+0x19:4], dsp_data[base+0x01:base+0x1A:4], dsp_data[base+0x02:base+0x1B:4], dsp_data[base+0x03:base+0x1C:4] = \
	dsp_data[base+0x03:base+0x1C:4], dsp_data[base+0x02:base+0x1B:4], dsp_data[base+0x01:base+0x1A:4], dsp_data[base+0x00:base+0x19:4]
	dsp_data[base+0x1C:base+0x5F:2], dsp_data[base+0x1D:base+0x60:2] = \
	dsp_data[base+0x1D:base+0x60:2], dsp_data[base+0x1C:base+0x5F:2]

def DSP2MCADPCM(filename_dsp0, filename_dsp1, channels, sound_file):
	with open(filename_dsp0, "rb") as dsp0_file: dsp0_data = bytearray(dsp0_file.read())
	dsp0_size = len(dsp0_data)
	ConvertDSP(dsp0_data, 0x00)

	if channels == 2:
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

	elif channels == 1:
		header_single = b'\x01\x00\x00\x00\x0C\x00\x00\x00'
		sound_file.write(header_single)
		sound_file.write(dsp0_size.to_bytes(4, byteorder = 'little', signed = False))
		sound_file.write(dsp0_data)

def ConvertSound_Internal(filepath_without_extension):
	filename_mcadpcm = filepath_without_extension + ".mcadpcm"
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

	util.LogDebug("Convert Sound <{}> WAV:{} XWM:{} LIP:{} FUZ:{}".format(filepath_without_extension, has_wav, has_xwm, has_lip, has_fuz))

	# if there is a loose LIP load into memory
	if has_lip:
		with open(filename_lip, "rb") as lip_file:
			lip_data = lip_file.read()
			lip_size = len(lip_data)
	else:
		lip_size = 0

	#  - loose WAV files take precedence over FUZ or XWM
	#  - loose XWM files take precedence over FUZ
	#  - loose LIP files take precedence over FUZ
	if has_fuz and (lip_size == 0 or not (has_wav or has_xwm)):
		with open(filename_fuz, "rb") as fuz_file:
			if lip_size == 0:
				fuz_file.seek(0x08)
				lip_size = int.from_bytes(fuz_file.read(0x04), byteorder = 'little', signed = False)
				lip_data = fuz_file.read(lip_size)
			else:
				fuz_file.seek(0x12)
			if not (has_wav or has_xwm):
				with open(filename_xwm, "wb") as xwm_file:
					xwm_file.write(fuz_file.read())
					has_xwm = True

	# try to reuse existing WAV whenever possible to avoid too many conversions
	if not has_wav:
		XWM2WAV(filename_xwm, filename_wav)

	# it returns -1 on a failed conversion
	channels = WAV2DSP(filename_wav, filename_dsp0, filename_dsp1)

	if lip_size > 0:
		lip_padding = lip_size % 4
		if lip_padding != 0: lip_padding = 4 - lip_padding
		voice_offset = 0x10 + lip_size + lip_padding

		with open(filename_fuz, "wb") as fuz_nx_file:
			header_fuz = b'\x46\x55\x5A\x45\x01\x00\x00\x00'
			fuz_nx_file.write(header_fuz)
			fuz_nx_file.write(lip_size.to_bytes(4, byteorder = 'little', signed = False))
			fuz_nx_file.write(voice_offset.to_bytes(4, byteorder = 'little', signed = False))
			fuz_nx_file.write(lip_data)
			fuz_nx_file.write(b'\x00' * lip_padding)
			DSP2MCADPCM(filename_dsp0, filename_dsp1, channels, fuz_nx_file)
	else:
		with open(filename_mcadpcm, "wb") as mcadpcm_file:
			DSP2MCADPCM(filename_dsp0, filename_dsp1, channels, mcadpcm_file)

	# clean up temporary files
	util.RemoveFile(filename_wav)
	if channels > 0: util.RemoveFile(filename_dsp0)
	if channels > 1: util.RemoveFile(filename_dsp1)
	if has_xwm: util.RemoveFile(filename_xwm)
	if has_lip: util.RemoveFile(filename_lip)
	if lip_size == 0: util.RemoveFile(filename_fuz)

	return (channels > 0)

def ConvertSound(target, filepath_without_extension):
	return ConvertSound_Internal(filepath_without_extension)

def ConvertSoundAsync(target, filename, ret):
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
