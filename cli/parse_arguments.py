from argparse import ArgumentParser
from datetime import datetime

def add_in_out_folder_args(parser):
	required = parser.add_argument_group('required arguments')
	required.add_argument("-i", "--input_folder", dest="input_folder", required=True,
                    help="Input folder of the pictures to be processed", metavar="input_folder")

	required.add_argument("-o", "--output_folder", dest="output_folder", required=True,
	                    help="Folder to output the results", metavar="output_folder")

def add_subparser_convert(subparsers):
	parser_convert = subparsers.add_parser('convert', help='Convert .sav files to image files')
	add_in_out_folder_args(parser_convert)

def add_subparser_organize(subparsers):
	parser_organize = subparsers.add_parser('organize', help='Organize AEB sequences into separate folders')
	add_in_out_folder_args(parser_organize)

def add_subparser_process(subparsers):
	parser_process = subparsers.add_parser('process', help='Process pictures sets : average, create gifs. Processing is done subfolder by subfolder')
	processing_actions=["average", "gif_ascend", "gif_descend", "gif_depth"]
	for act in processing_actions:
		parser_process.add_argument("--{}".format(act), action="store_true")
	add_in_out_folder_args(parser_process)
	return parser_process

def add_subparser_stitch(subparsers):
	parser_stitch = subparsers.add_parser('stitch', help='Stitch pictures together')
	add_in_out_folder_args(parser_stitch)

def check_process_options(args, parser_process):
	if args.action == "process":
		args_dict = vars(args)
		if not any(args_dict[process_act] for process_act in processing_actions):
			parser_process.error('At least one processing action is required amongst {}'.format(processing_actions))

def parse_arguments():
	parser = ArgumentParser(prog='gbcam-hdr-utils',
	                    description='Utilities for processing HDR Gameboy Camera pictures.')
	subparsers = parser.add_subparsers(dest='action', help='Action to apply', required=True)
	
	add_subparser_convert(subparsers)
	add_subparser_organize(subparsers)
	parser_process = add_subparser_process(subparsers)
	add_subparser_stitch(subparsers)

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