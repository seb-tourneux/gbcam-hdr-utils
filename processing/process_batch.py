import processing.files_utils as files_utils
import processing.data as data
import processing.process as process
import os

def process_batch(input_dir, output_dir, options, callback):
	sub_dir = files_utils.get_sub_directories(input_dir)
	if not sub_dir:
		sub_dir = [input_dir]

	border_path = options["border_path"]
	for d in sub_dir:
		array_paths = data.get_arrays_and_path_from_folder(d, border_path)
		arrays = list(zip(*array_paths))[0]
		callback( "Processing {} images in folder \"{}\"".format(len(arrays), os.path.basename(d)) )

		if options["blend_average"]:
			res = process.average(arrays)
			data.finalizeAndSave(res, options["scale_factor"], output_dir, d, "average")

		if options["gif_first_to_last"]:
			data.make_gif(d, output_dir, options["scale_factor"], options["gif_frame_duration"], border_path)

		if options["gif_last_to_first"]:
			data.make_gif(d, output_dir, options["scale_factor"], options["gif_frame_duration"], border_path, True)
