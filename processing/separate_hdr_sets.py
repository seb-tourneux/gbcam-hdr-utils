import data
import files_utils
import os
import shutil
from copy import deepcopy

input_dir = "F:/MySofts/GBCam_PicNRec_v1.7/2023-09-04_21-03-46"
output_dir = "E:/Data/Prods/2022/Photo/GameboyCamera/2023_09_03/HDR_no_dupl"

threshold = 0.5

def copy_set_paths(sets_paths, output_dir):
	print("Nb sets {}".format(len(sets_paths)))
	
	i = 0
	for set_paths in sets_paths:
		if len(set_paths) == 0:
			continue
		
		print("Nb files of the set#{} : {}".format(i, len(set_paths)))
		new_dir = output_dir + "/" + "set_{}".format(i)
		os.makedirs(new_dir)
		i+=1
		for path in set_paths:
			basename = os.path.basename(path)
			new_path = os.path.join(new_dir, basename)
			shutil.copy(path, new_path)




# Separate images into several sets.
# As HDR images gradually increases (or decreases) exposure
# we can detect big differences of luminosity in sequences of images.
# Most of the time it should detect (almost full black -> almost full white) or (almost full white -> almost full black)
def separate_hdr_sets(input_dir, output_dir):
	print("Processing {}".format(input_dir))

	files = files_utils.get_image_files(input_dir)
	
	arrays_paths = data.get_arrays_and_path_from_file_list(files)
	
	sets_paths = [[]]
	current_set = []
	ref_mean = arrays_paths[0][0].mean()
	for arr, path in arrays_paths:
		cur_mean = arr.mean()
		
		if abs(cur_mean - ref_mean) > threshold :
			with_dup = len(current_set)
			unique = {array[0].tostring(): array for array in current_set}
			unique = unique.values()
			without_dup = len(unique)
			if (with_dup != without_dup):
				print("Remove {} duplicates".format(with_dup-without_dup))
				
			paths_only = list(zip(*unique))[1]
			sets_paths.append(deepcopy(paths_only))
			current_set.clear()
		
		print("mean {} file {} ".format(cur_mean, path))
		
		current_set.append((arr, path))
		ref_mean = cur_mean
	
		paths_only = list(zip(*current_set))[1]

	paths_only = list(zip(*current_set))[1]
	sets_paths.append(deepcopy(paths_only))
	copy_set_paths(sets_paths, output_dir)



separate_hdr_sets(input_dir, output_dir)