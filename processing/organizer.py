import processing.data as data
import processing.files_utils as files_utils
import os
import shutil
from copy import deepcopy

threshold = 0.1

def set_infos(set_paths):
	basenames = [os.path.basename(p) for p in set_paths]
	N = len(basenames)

	if N == 1:
		return "1 picture : [{}]".format(basenames[0])
	else:
		info = "{} pictures: ".format(N)
		if N == 2:
			info += "[{}, {}]".format(basenames[0], basenames[-1])
		else:
			info += "[{}, ..., {}]".format(basenames[0], basenames[-1])
	return info

def copy_set_paths(sets_paths, output_dir):
	i = 0
	for set_paths in sets_paths:
		if len(set_paths) == 0:
			continue
		
		new_dir = output_dir + "/" + "set_{}".format(i)
		os.makedirs(new_dir)
		i+=1
		for path in set_paths:
			basename = os.path.basename(path)
			new_path = os.path.join(new_dir, basename)
			shutil.copy(path, new_path)


def stop_size(current_set, max_nb_per_set):
	return (max_nb_per_set != None) and (len(current_set) >= max_nb_per_set)

def append_current_set(sets_paths, current_set, max_nb_per_set, completion, file_processed_callback):
	

	
	paths_only = list(zip(*current_set))[1]
	
	
	ignored_by_size = stop_size(current_set, max_nb_per_set)
	if ignored_by_size:
		if file_processed_callback:
			file_processed_callback("Ignoring set because bigger than maximum of {} pictures : {}"\
						   .format(max_nb_per_set, set_infos(paths_only)),\
								    completion)
			return
	
	if file_processed_callback:
		file_processed_callback("Set #{} : {}".format(len(sets_paths), set_infos(paths_only)), completion)
	sets_paths.append(deepcopy(paths_only))


def stop_distance(cur_mean, ref_mean, threshold):
	return abs(cur_mean - ref_mean) > threshold

# Separate images into several sets.
# As HDR images gradually increases (or decreases) exposure
# we can detect big differences of luminosity in sequences of images.
# Most of the time it should detect (almost full black -> almost full white) or (almost full white -> almost full black)
def separate_hdr_sets(input_dir, output_dir, threshold, max_nb_per_set, update_callback = None):
	print("Processing {}".format(input_dir))


	files = files_utils.get_image_files(input_dir)
	n = len(files)
	update_callback("Found {} files".format(n))
	
	arrays_paths = data.get_arrays_and_path_from_file_list(files)
	
	sets_paths = []
	current_set = []
	ref_mean = arrays_paths[0][0].mean()
	for i, (arr, path) in enumerate(arrays_paths):
		cur_mean = arr.mean()
		
		stopped_by_dist =  stop_distance(cur_mean, ref_mean, threshold)
		
		if stopped_by_dist:
			ignored_by_size = stop_size(current_set, max_nb_per_set)

			#todo option
			remove_dup = False # todo setting
			if remove_dup:
				with_dup = len(current_set)
				unique = {array[0].tostring(): array for array in current_set}
				current_set = unique.values()
				without_dup = len(current_set)
				if (with_dup != without_dup):
					print("Remove {} duplicates".format(with_dup-without_dup))
		
			append_current_set(sets_paths, current_set, max_nb_per_set, i / n, update_callback)

			
			current_set = []
		
		#print("mean {} file {} ".format(cur_mean, path))
		
		current_set.append((arr, path))
		ref_mean = cur_mean
	
	append_current_set(sets_paths, current_set, max_nb_per_set, 1.0, update_callback)
	copy_set_paths(sets_paths, output_dir)

