import os
import natsort

image_extensions = (".png", ".bmp")
sav_extensions = (".sav")

def get_files(directory, extensions): 
	file_list = os.listdir(directory)
	res = []
	for file in file_list:
		full_path = os.path.join(directory, file)
		if os.path.isfile(os.path.join(directory, file)):
				res.append(full_path)
		else:
			result = get_image_files(os.path.join(directory, file))
			if result:
				res.extend(get_image_files(os.path.join(directory, file)))
				
	res = [ file for file in res if file.lower().endswith( extensions ) ]
	res = natsort.natsorted(res)

	return res

def get_image_files(directory):
	return get_files(directory, image_extensions)

def get_sav_files(directory):
	return get_files(directory, sav_extensions)


# process each folders
def get_sub_directories(input_dir):
	res = []
	for dirname, dirnames, filenames in os.walk(input_dir):
		# print path to all subdirectories first.
		for subdirname in dirnames:
			dirPath = os.path.join(dirname, subdirname)
			res.append(dirPath)

	res = natsort.natsorted(res)
	return res
