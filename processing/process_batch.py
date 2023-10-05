import processing.files_utils as files_utils
import processing.data as data
import processing.process as process
import os

def process_batch(input_dir, output_dir, options, update_callback):
	sub_dir = files_utils.get_sub_directories(input_dir)
	if not sub_dir:
		sub_dir = [input_dir]

	border_path = options["border_path"]
	n = len(sub_dir)
	for i, d in enumerate(sub_dir):
		array_paths = data.get_arrays_and_path_from_folder(d, border_path)
		arrays = list(zip(*array_paths))[0]
		update_callback( "Processing {} images in folder \"{}\"".format(len(arrays), os.path.basename(d)), i / n )

		if options["blend_average"]:
			res = process.average(arrays)
			data.finalizeAndSave(res, options["scale_factor"], output_dir, d, "average")

		if options["gif_ascend"]:
			data.make_gif(d, output_dir, options["scale_factor"], options["gif_frame_duration"], "gif_ascend", border_path)
		if options["gif_descend"]:
			data.make_gif(d, output_dir, options["scale_factor"], options["gif_frame_duration"], "gif_descend", border_path)
		if options["gif_depth"]:
			data.make_gif(d, output_dir, options["scale_factor"], options["gif_frame_duration"], "gif_depth", border_path)
		if options["gif_depth_reverse"]:
			data.make_gif(d, output_dir, options["scale_factor"], options["gif_frame_duration"], "gif_depth_reverse", border_path)
