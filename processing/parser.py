import numpy as np
import sys
from bitstring import BitArray
import matplotlib.pyplot as plt
import os
import processing.files_utils as files_utils
import processing.data as data
from inspect import currentframe
from enum import Enum
from chrono import Timer

color_map = [3, 2, 1, 0]

class SavTypes():
	Type = Enum('Type', ['SINGLE', 'RAM_DUMP', 'FRAM_DUMP'])

	@staticmethod
	def get_type(file_size):
		typeFromSize = {	3_584 : SavTypes.Type.SINGLE, # 4 KiB,
							   131_072 : SavTypes.Type.RAM_DUMP, # 128 KiB
							   2_097_152 : SavTypes.Type.FRAM_DUMP # 2048 KiB, 16xRAM_DUMP
					   }
		return typeFromSize[file_size]

def get_linenumber():
	cf = currentframe()
	return cf.f_back.f_lineno

def file_pos(file):
	return "{}".format(file.tell())

def dbg_print_info(line_number, file):
	pos = file.tell()
	pos_hex = hex(pos)
	print("[{}] {} {}".format(line_number, pos, pos_hex))

def pairwise(iterable):
	"s -> (s0, s1), (s2, s3), (s4, s5), ..."
	a = iter(iterable)
	return zip(a, a)

def read_tile(bytes_16, x, y, arr):
	for row, (lo_str, hi_str) in enumerate(pairwise(bytes_16)):
		lo_value = BitArray(uint=lo_str, length=8)
		hi_value = BitArray(uint=hi_str, length=8)

		for col in range(8):
			lo_masked = lo_value[col]
			hi_masked = hi_value[col]
			res = BitArray([hi_masked, lo_masked])
			
			row_offset = y*8+row
			col_offset = x*8+col
			arr[row_offset][col_offset] = color_map[res.uint]

# return if image_data could be read
# (ie not end of file)
def read_image_data(file, arr):
	#dbg_print_info(get_linenumber(), file)
	x = 0
	y = 0

	bytes_16 = file.read(16)
	if not bytes_16:
		return False

	while bytes_16:
		read_tile(bytes_16, x, y, arr)

		x += 1
		if x*8 >=  arr.shape[1]:
			x = 0
			y += 1

		if y*8 >=  arr.shape[0]:
			break
		bytes_16 = file.read(16)
	return True

def read_metadata(file):
	# todo
	# for now, just consume the section
	metadata_size = 512
	file.seek(file.tell() + metadata_size)

def get_output_path(output_folder, input_file, i, bank, savType):
	if savType == SavTypes.Type.SINGLE:
		suffix = ""
	elif savType == SavTypes.Type.RAM_DUMP:
		suffix = "_{}".format(i)
	elif savType == SavTypes.Type.FRAM_DUMP:
		suffix = "_bank_{}_{}".format(bank, i)

	filename = files_utils.get_filename_no_ext(input_file)
	out_file = "{}/{}{}.png".format(output_folder, filename, suffix)
	return  os.path.normpath(out_file)

def write_image(arr, file_path, output_folder, i, bank, savType, file_processed_callback = None):
	out_path = get_output_path(output_folder, file_path, i, bank, savType)
	data.save_image_array(arr, out_path)
	file_processed_callback("=== Saved {}".format(out_path))

def end_of_bank(file):
	pos = file.tell()
	return pos % 131_072 == 0

def convert_file(file_path, output_folder, file_processed_callback = None):
	try:
		with Timer() as timerOpen:
			file = open(file_path, 'rb')
		print("timerOpen: {} seconds".format(timerOpen.elapsed))

		with Timer() as timerConv:
			arr  = np.zeros((112, 128), dtype=np.uint8)
			file_size = os.path.getsize(file_path)
			savType = SavTypes.get_type(file_size)

			i = 1
			bank = 1
			if savType == SavTypes.Type.SINGLE:
				read_image_data(file, arr)
				write_image(arr, file_path, output_folder, i, savType, file_processed_callback)
			elif savType == SavTypes.Type.RAM_DUMP or savType == SavTypes.Type.FRAM_DUMP:
				firstPictureAddress="02000"
				file.seek(int(firstPictureAddress, 16))

				while read_image_data(file, arr):
					write_image(arr, file_path, output_folder, i, bank, savType, file_processed_callback)
					read_metadata(file)

					if end_of_bank(file):
						i = 1
						bank += 1
						file.seek(file.tell() + int(firstPictureAddress, 16))
					else:
						i += 1
			else:
				file_processed_callback("Unsupported file size: {}".format(file_size))

			print("timerConv: {} seconds".format(timerConv.elapsed))

	except Exception as err:
		print("Cannot process file {} : {}".format(file_path, err))


def convert_folder(input_folder, output_folder, file_processed_callback = None):
	input_sav_files = files_utils.get_sav_files(input_folder)
	if not input_sav_files:
		if file_processed_callback:
			file_processed_callback("Not .sav files found in directory \"{}\"".format(input_folder))
	else:
		for f in input_sav_files:
			if file_processed_callback:
				file_processed_callback("= Converting {}...".format(f))

			convert_file(f, output_folder, file_processed_callback)


