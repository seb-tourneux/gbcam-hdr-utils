import numpy as np
import sys
from bitstring import BitArray
import matplotlib.pyplot as plt
import os
import processing.files_utils as files_utils

filePnR="input/pnr_001212.sav"
fileSavDump="input/PHOTO.sav"

color_map = [3, 2, 1, 0]

def pairwise(iterable):
	"s -> (s0, s1), (s2, s3), (s4, s5), ..."
	a = iter(iterable)
	return zip(a, a)

image_arr  = np.zeros((112, 128), dtype=np.uint8)


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

def read_image_data(file, arr):
	x = 0
	y = 0
		
	bytes_16 = file.read(16)
	while bytes_16:
		read_tile(bytes_16, x, y, arr)
		x += 1
		if x*8 >=  arr.shape[1]:
			x = 0
			y += 1
		
		if y*8 >=  arr.shape[0]:
			break
		bytes_16 = file.read(16)

def read_file(file_path):
	try:
		file = open(file_path, 'rb')
		fullRamSize = 131072
		onePictureDataSize = 3584
		
		# todo handle Photo 8 rolls : 2048Ko 
		
		file_size = os.path.getsize(file_path)
		if file_size == fullRamSize:
			firstPictureAddress="02000"
			file.seek(int(firstPictureAddress, 16))
			# todo iterate
		read_image_data(file, image_arr)
		
	except Exception as err:
		print("Cannot process file {} : {}".format(file_path, err))

def test():
	read_file(filePnR)
	
	
	plt.imshow(image_arr, cmap='gray', interpolation='nearest')
	plt.axis('off')
	
	#read_file(fileSavDump)
		
	plt.show()

def convert_folder(input_folder, output_folder, file_processed_callback = None):
	input_sav_files = files_utils.get_sav_files(input_folder)
	if not input_sav_files:
		if file_processed_callback:
			file_processed_callback("Not .sav files found in directory \"{}\"".format(input_folder))
	else:
		for f in input_sav_files:
			# todo actually convert
			if file_processed_callback:
				file_processed_callback("Converted {}".format(f))

