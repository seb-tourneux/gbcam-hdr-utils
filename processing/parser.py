import numpy as np
import sys
import matplotlib.pyplot as plt
import os
import processing.files_utils as files_utils
import processing.data as data
from inspect import currentframe
from enum import Enum
from chrono import Timer


class SavTypes():
	Type = Enum('Type', ['SINGLE', 'ORIGINAL_RAM_DUMP', 'FRAM_DUMP'])

	single_size = 3_584
	original_RAM_dump_size = 131_072
	
	@staticmethod
	def get_type(file_size):

		if file_size == SavTypes.single_size: # 4 KiB
			return SavTypes.Type.SINGLE
		elif file_size == SavTypes.original_RAM_dump_size: # 128 KiB
			return SavTypes.Type.ORIGINAL_RAM_DUMP
		elif file_size % SavTypes.original_RAM_dump_size == 0:
			# n banks
			#1024 KiB (8 banks), 2048 KiB (16 banks), etc
			return SavTypes.Type.FRAM_DUMP
		else:
			return None

	@staticmethod
	def get_nb_images(file_size):
		if file_size == SavTypes.single_size:
			return 1
		elif file_size == SavTypes.original_RAM_dump_size:
			return 30
		else:
			return (file_size / SavTypes.original_RAM_dump_size) * 30

print_chrono = False
nb_tiles = 224 # 128*112/64 : 128*112 total pixels, 8*8 pixels per tile
tile_size = 16


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

masks = [0b10000000,
0b01000000,
0b00100000,
0b00010000,
0b00001000,
0b00000100,
0b00000010,
0b00000001]

color_map = {(True, True) :0,
			 (True, False) : 128,
			 (False, True) : 192,
			 (False, False) : 255}

def read_tile(cur_tile_bytes, tile_idx, arr):
	x = tile_idx % 16
	y = tile_idx // 16

	for row, (lo, hi) in enumerate(pairwise(cur_tile_bytes)):
		for col in range(8):
			lo_masked = lo& masks[col] != 0
			hi_masked = hi & masks[col] != 0

			row_offset = y*8+row
			col_offset = x*8+col
			arr[row_offset][col_offset] = color_map[(hi_masked, lo_masked)]




# return if image_data could be read
# (ie not end of file)
def read_image_data(file, arr):
	#dbg_print_info(get_linenumber(), file)

	tiles_bytes = file.read(nb_tiles*tile_size)
	if not tiles_bytes:
		return False

	for tile_idx in range(0, nb_tiles):
		read_tile(tiles_bytes[tile_idx*tile_size : (tile_idx+1)*tile_size], tile_idx, arr)

	read_metadata(file)

	return True

def read_metadata(file):
	# todo
	# for now, just consume the section
	metadata_size = 512
	#file.seek(file.tell() + metadata_size)
	file.read(metadata_size)

def get_output_path(output_folder, input_file, i, bank, savType):
	if savType == SavTypes.Type.SINGLE:
		suffix = ""
	elif savType == SavTypes.Type.ORIGINAL_RAM_DUMP:
		suffix = "_{:02d}".format(i)
	elif savType == SavTypes.Type.FRAM_DUMP:
		suffix = "_bank_{:02d}_{:02d}".format(bank, i)

	filename = files_utils.get_filename_no_ext(input_file)
	out_file = "{}/{}{}.png".format(output_folder, filename, suffix)
	return  os.path.normpath(out_file)

def write_image(arr, file_path, output_folder, i, bank, savType, nb_images_processed, total_nb_images, update_callback = None):
	out_path = get_output_path(output_folder, file_path, i, bank, savType)
	data.save_image_array(arr, False, out_path)
	
	nb_images_processed[0] += 1 # workaround because int are immutable
	if update_callback:
		update_callback("=== Saved {}".format(out_path), nb_images_processed[0] / total_nb_images)

def end_of_bank(file):
	pos = file.tell()
	return pos % 131_072 == 0

def skip_header(file):
	firstPictureAddress="02000"
	file.seek(file.tell() + int(firstPictureAddress, 16))

def convert_file(file_path, output_folder, nb_images_processed, total_nb_images, update_callback = None):
	try:
		file = open(file_path, 'rb')

		with Timer() as timerConv:
			arr  = np.zeros((112, 128), dtype=np.uint8)
			file_size = os.path.getsize(file_path)
			savType = SavTypes.get_type(file_size)

			i = 1
			bank = 1
			if savType == SavTypes.Type.SINGLE:
				read_image_data(file, arr)
				write_image(arr, file_path, output_folder, i, bank, savType, nb_images_processed, total_nb_images, update_callback)
			elif savType == SavTypes.Type.ORIGINAL_RAM_DUMP or savType == SavTypes.Type.FRAM_DUMP:
				skip_header(file)
				while read_image_data(file, arr):
					write_image(arr, file_path, output_folder, i, bank, savType, nb_images_processed, total_nb_images, update_callback)

					if end_of_bank(file):
						i = 1
						bank += 1
						skip_header(file)
					else:
						i += 1
			else:
				update_callback("Unsupported file size: {}".format(file_size))

		if print_chrono:
			print("= timerConv: {} seconds".format(timerConv.elapsed))

	except Exception as err:
		print("Cannot process file {} : {}".format(file_path, err))
		raise err

def folder_nb_images(input_sav_files):
	count_nb_images = 0
	for f in input_sav_files:
		file_size = os.path.getsize(f)
		count_nb_images += SavTypes.get_nb_images(file_size)
	return count_nb_images

def convert_folder(input_folder, output_folder, update_callback = None):
	input_sav_files = files_utils.get_sav_files(input_folder)
	if not input_sav_files:
		if update_callback:
			update_callback("Not .sav files found in directory \"{}\"".format(input_folder))
	else:
		total_nb_images = folder_nb_images(input_sav_files)
		i = [0]
		for f in input_sav_files:
			if update_callback:
				update_callback("= Converting {}...".format(f))

			convert_file(f, output_folder, i, total_nb_images, update_callback)


