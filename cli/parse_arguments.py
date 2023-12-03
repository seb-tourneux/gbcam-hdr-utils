from argparse import ArgumentParser
from datetime import datetime
import processing.organizer as organizer

processing_actions=[
("average","Blend all images by averaging them"),
("gif_ascend", "Create a gif in the order of the input images [1..n]"),
("gif_descend", "Create a gif in the reverse order of the input images [n..1]"),
("gif_depth", "Create a gif by incrementaly blending more and more images [1, 1+2, ..., 1+...+n]"),
("gif_depth_reverse", "Create a gif by incrementaly blending more and more images [n, n+(n-1), n+...+1]")
]

def add_in_out_folder_args(parser):
	required = parser.add_argument_group('required arguments')
	required.add_argument("-i", "--input_folder", dest="input_folder", required=True,
                    help="Input folder of the pictures to be processed")

	required.add_argument("-o", "--output_folder", dest="output_folder", required=True,
	                    help="Folder to output the results")

def add_subparser_convert(subparsers):
	parser_convert = subparsers.add_parser('convert', help='Convert .sav files to image files')
	#add_in_out_folder_args(parser_convert)

def add_subparser_organize(subparsers):
	parser_organize = subparsers.add_parser('organize', help='Organize AEB sequences into separate folders')
	parser_organize.add_argument("-t", "--threshold", help="Threshold of luminosity between two consecutive image to be separated", dest="threshold", default=0.25, type=float)
	parser_organize.add_argument("-n", "--max_nb_per_set", help="Maximum number of images per set. Sets strictly bigger than this value will be handled according to mode", dest="max_nb_per_set", default=29, type=int)
	modes = [m.name.lower() for m in organizer.Mode]
	parser_organize.add_argument("-m", "--mode", help="Mode to manage sets bigger than max_nb_per_set", choices=modes, dest="mode", default=organizer.Mode(1))
	#add_in_out_folder_args(parser_organize)

def add_subparser_process(subparsers):
	parser_process = subparsers.add_parser('process', help='Process pictures sets : average, create gifs. Processing is done subfolder by subfolder')
	for (act, help_msg) in processing_actions:
		parser_process.add_argument("--{}".format(act), action="store_true", help=help_msg)
	parser_process.add_argument("--gif_frame_duration", help="Duration of 1 frame of the gif generated (ms)", dest="gif_frame_duration", default=100, type=int)
	parser_process.add_argument("--scale", help="Scaling factor", dest="scale_factor", default=1, type=int)
	parser_process.add_argument("--border_path", help="Path to a 160x144 border image", dest="border_path", default=None)
	parser_process.add_argument("--palette", help="String with 4 hexa string: ex \"#01162c #0460bf #7cbde8 #fff7e1\"", dest="palette", default=None)

	#add_in_out_folder_args(parser_process)
	return parser_process

def add_subparser_stitch(subparsers):
	parser_stitch = subparsers.add_parser('stitch', help='Stitch pictures together')
	#add_in_out_folder_args(parser_stitch)

def check_process_options(args, parser_process):
	if args.action == "process":
		args_dict = vars(args)
		standard_processing = any(args_dict[process_act] for (process_act, _) in processing_actions))
		palette_processing = args["palette"] != None
		if not(standard_processing or palette_processing):
			options_str = [ "--{}".format(process_act) for (process_act, _) in processing_actions]
			parser_process.error('At least one processing action is required amongst: {}'.format(options_str))

def parse_arguments():
	parser = ArgumentParser(prog='gbcam-hdr-utils',
	                    description='Utilities for processing HDR Gameboy Camera pictures.')


	subparsers = parser.add_subparsers(dest='action', help='Action to apply', required=True)
	
	add_subparser_convert(subparsers)
	add_subparser_organize(subparsers)
	parser_process = add_subparser_process(subparsers)
	add_subparser_stitch(subparsers)

	add_in_out_folder_args(parser)

	args = parser.parse_args()

	check_process_options(args, parser_process)

	return args

def print_cli(text, completion = None):
	
	completion_text = ""
	if completion:
		completion_text = "{:.2f}%".format(100*completion).rjust(7)
		completion_text = "[{}]".format(completion_text)

	time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
	
	print("[{}]{} {}".format(time, completion_text, text))

def parse_process_options(args):
	options = {'gif_ascend' : args.gif_ascend,
		    'gif_descend' : args.gif_descend,
			'gif_depth' : args.gif_depth,  # todo
			'gif_depth_reverse' : args.gif_depth_reverse,
			'blend_average' : args.average,
			'gif_frame_duration' : args.gif_frame_duration, #todo
			'scale_factor' : args.scale_factor,
			'border_path' : args.border_path,
			'color_palette' : args.palette
		 }
	return options