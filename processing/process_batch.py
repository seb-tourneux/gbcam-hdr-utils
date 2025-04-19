import processing.files_utils as files_utils
import processing.data as data
import processing.process as process
import os

def default_options():
    return {
        "blend_average": True,
        "scale_factor": 1,
        "border_path": None,
        "palette": None,
        "gif_frame_duration": 100,
        "gif_ascend": False,
        "gif_descend": False,
        "gif_depth": False,
        "gif_depth_reverse": False
    }


def process_batch(input_dir, output_dir, options, update_callback = None):
	sub_dirs = files_utils.get_all_subdirectories(input_dir)

	for sub_dir in sub_dirs:
		relative_path = sub_dir.replace(input_dir, "")

		relative_path = relative_path.replace("/", "_")
		new_prefix = relative_path.replace("\\", "_")
		if new_prefix[0] == "_":
			new_prefix = new_prefix[1:]

		process_batch_dir(sub_dir, output_dir, options, new_prefix, update_callback)


def make_gif_from_type(gif_type, input_dir, output_dir, options, prefix, border_path, update_callback):
    if options[gif_type]:
        output_dir_type = os.path.join(output_dir, gif_type)
        os.makedirs(output_dir_type, exist_ok=True)
        data.make_gif(input_dir, output_dir_type, options["scale_factor"], options["gif_frame_duration"], type, border_path)

def process_batch_dir(input_dir, output_dir, options, prefix, update_callback):
	#sub_dir = files_utils.get_sub_directories(input_dir)
	#if not sub_dir:
	sub_dir = [input_dir]

	border_path = options["border_path"]
	n = len(sub_dir)
	for i, d in enumerate(sub_dir):
		array_paths = data.get_arrays_and_path_from_folder(d, border_path)
		if len(array_paths) == 0:
			continue
			
		arrays = list(zip(*array_paths))[0]
		update_callback( "Processing {} images in folder \"{}\"".format(len(arrays), os.path.basename(d)), i / n )

		if options["blend_average"]:
			res = process.average(arrays)
			data.finalizeAndSave(res, options["scale_factor"], None, output_dir, prefix, "average")
		else:
			# save single pictures (maybe make an option)
			n_single = len(array_paths)
			for i_single, (arr, path) in enumerate(array_paths):
				suffix = os.path.basename(path)
				data.finalizeAndSave(arr, options["scale_factor"], options["color_palette"], output_dir, prefix, suffix)
				update_callback( "=== Saving single image {}".format(suffix), i_single / n_single )

		make_gif_from_type("gif_ascend", d, output_dir, options, prefix, border_path, update_callback)
		make_gif_from_type("gif_descend", d, output_dir, options, prefix, border_path, update_callback)
		make_gif_from_type("gif_depth", d, output_dir, options, prefix, border_path, update_callback)
		make_gif_from_type("gif_depth_reverse", d, output_dir, options, prefix, border_path, update_callback)
		
