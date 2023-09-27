import os
import natsort

image_extensions = [".png",".PNG", ".bmp", ".BMP"]

def get_image_files(dir): 
	file_list = os.listdir(dir)
	res = []
	for file in file_list:
		full_path = os.path.join(dir, file)
		if os.path.isfile(os.path.join(dir, file)):
				res.append(full_path)
		else:
			result = get_image_files(os.path.join(dir, file))
			if result:
				res.extend(get_image_files(os.path.join(dir, file)))
				
	res=[filename for filename in res if filename[-4:] in image_extensions]

	res = natsort.natsorted(res)

	return res


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

