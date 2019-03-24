#! python3

import os
import util

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
	VGAudioCli = GetVGAudioCli()
	commandLine = [VGAudioCli, "-i:0", filename_wav, filename_dsp0]
	util.RunCommandLine(commandLine)

	with open(filename_wav, "rb") as wav_file:
		wav_file.seek(0x16)
		channel_count = int.from_bytes(wav_file.read(1), byteorder = 'little', signed = False)
		if channel_count > 1:
			commandLine = [VGAudioCli, "-i:1", filename_wav, filename_dsp1]
			util.RunCommandLine(commandLine)

def ConvertDSP(dsp_data):
	dsp_data[0x00:0x19:4], dsp_data[0x01:0x1A:4], dsp_data[0x02:0x1B:4], dsp_data[0x03:0x1C:4] = dsp_data[0x03:0x1C:4], dsp_data[0x02:0x1B:4], dsp_data[0x01:0x1A:4], dsp_data[0x00:0x19:4]
	dsp_data[0x1C:0x5F:2], dsp_data[0x1D:0x60:2] = dsp_data[0x1D:0x60:2], dsp_data[0x1C:0x5F:2]

def DSP2MCADPCM(filename_dsp0, filename_dsp1, sound_file):
	header_single = b'\x01\x00\x00\x00\x0C\x00\x00\x00'
	header_stereo = b'\x02\x00\x00\x00\x14\x00\x00\x00'
	
	with open(filename_dsp0, "rb") as dsp0_file:
		dsp0_data = bytearray(dsp0_file.read())
		dsp0_size = len(dsp0_data)
		ConvertDSP(dsp0_data)
		
	if os.path.exists(filename_dsp1):
		with open(filename_dsp1, "rb") as dsp1_file:
			dsp1_data = bytearray(dsp1_file.read())
			dsp1_size = len(dsp1_data)
			ConvertDSP(dsp1_data)
		
		dsp1_offset = 0x14 + dsp0_size
		sound_file.write(header_stereo)
		sound_file.write(dsp0_size.to_bytes(4, byteorder = 'little', signed = False))
		sound_file.write(dsp1_offset.to_bytes(4, byteorder = 'little', signed = False))
		sound_file.write(dsp1_size.to_bytes(4, byteorder = 'little', signed = False))
		sound_file.write(dsp0_data)
		sound_file.write(dsp1_data)
		
	else:
		sound_file.write(header_single)
		sound_file.write(dsp0_size.to_bytes(4, byteorder = 'little', signed = False))
		sound_file.write(dsp0_data)

def ConvertSound_Internal(filepath_without_extension):
	filename_mcadpcm = filepath_without_extension + ".mcadpcm"
	filename_dsp0 = filepath_without_extension + "__CH0__.dsp"
	filename_dsp1 = filepath_without_extension + "__CH1__.dsp"

	filename_wav = filepath_without_extension + ".wav"
	filename_xwm = filepath_without_extension + ".xwm"
	filename_lip = filepath_without_extension + ".lip"
	filename_fuz = filepath_without_extension + ".fuz"

	has_wav = os.path.exists(filename_wav)
	has_xwm = os.path.exists(filename_xwm)
	has_lip = os.path.exists(filename_lip)
	has_fuz = os.path.exists(filename_fuz)

	util.LogDebug("Convert Sound <{}> WAV:{} XWM:{} LIP:{} FUZ:{}".format(filepath_without_extension, has_wav, has_xwm, has_lip, has_fuz))

	# get LIP and convert sound to DSP
	#  - loose WAV files take precedence over FUZ or XWM
	#  - loose XWM files take precedence over FUZ
	#  - loose LIP files take precedence over FUZ
	if has_lip:
		with open(filename_lip, "rb") as lip_file:
			lip_data = lip_file.read()
			lip_size = len(lip_data)
	else:
		lip_size = 0

	if has_fuz and (lip_size == 0 or not (has_wav or has_xwm)):
		with open(filename_fuz, "rb") as fuz_file:
			if lip_size == 0:
				fuz_file.seek(0x08)
				lip_size = int.from_bytes(fuz_file.read(0x04), byteorder = 'little', signed = False)
				lip_data = fuz_file.read(lip_size) # if lip_size > 0
			else:
				fuz_file.seek(0x12)				
			if not (has_wav or has_xwm):
				with open(filename_xwm, "wb") as xwm_file:
					xwm_file.write(fuz_file.read())
			
	if not has_wav:
		XWM2WAV(filename_xwm, filename_wav)

	WAV2DSP(filename_wav, filename_dsp0, filename_dsp1)

	# convert DSP to MCADPCM and save as MCADPCM or as FUZ if LIP exists
	if lip_size > 0:
		header_fuz = b'\x46\x55\x5A\x45\x01\x00\x00\x00'
		
		lip_padding = lip_size % 4
		if lip_padding != 0: lip_padding = 4 - lip_padding
		voice_offset = 0x10 + lip_size + lip_padding
		
		with open(filename_fuz, "wb") as fuz_nx_file:
			fuz_nx_file.write(header_fuz)
			fuz_nx_file.write(lip_size.to_bytes(4, byteorder = 'little', signed = False))
			fuz_nx_file.write(voice_offset.to_bytes(4, byteorder = 'little', signed = False))
			fuz_nx_file.write(lip_data)
			fuz_nx_file.write(b'\x00' * lip_padding)
			DSP2MCADPCM(filename_dsp0, filename_dsp1, fuz_nx_file)			
	else:
		with open(filename_mcadpcm, "wb") as mcadpcm_file:
			DSP2MCADPCM(filename_dsp0, filename_dsp1, mcadpcm_file)

	# clean up temporary files	
	util.RemoveFile(filename_dsp0)
	util.RemoveFile(filename_dsp1)
	util.RemoveFile(filename_wav) 
	util.RemoveFile(filename_xwm)
	util.RemoveFile(filename_lip)
	if lip_size == 0: util.RemoveFile(filename_fuz)
	
	return True
	
def ConvertSound(target, filepath_without_extension):
	return ConvertSound_Internal(filepath_without_extension)
	
if __name__ == '__main__':
	import sys
	filepath = sys.argv[1]
	util.InitialiseLog(filepath + ".log")
	util.StartTimer()
	util.LogInfo("Skyrim-NX-Toolkit {} - convert_txt".format(util.GetToolkitVersion()))
	ConvertSound_Internal(filepath)
	util.EndTimer()
