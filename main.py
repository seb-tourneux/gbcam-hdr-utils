import sys
import data
import files_utils
import process



# input_dir = "./input"
# output_dir = "./output"
input_dir = "E:/Data/Prods/2022/Photo/GameboyCamera/2023_09_03/HDR_no_dupl"
output_dir = "E:/Data/Prods/2022/Photo/GameboyCamera/2023_09_03/HDR_no_dupl_averages"

#border_path = "data/frame_original.png"
border_path = None

scale_factor_fusion = 1
gifFrameDurationMs = 150

scale_factor_gif = 5
make_gif = True

sub_dir = files_utils.get_sub_directories(input_dir)

for d in sub_dir:
	array_paths = data.get_arrays_and_path_from_folder(d, border_path)
	arrays = list(zip(*array_paths))[0]

	res = process.average(arrays)
	data.finalizeAndSave(res, scale_factor_fusion, output_dir, d, "average")

	if make_gif:
		data.make_gif(d, output_dir, scale_factor_gif, gifFrameDurationMs, border_path)