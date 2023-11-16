from cli.parse_arguments import *

import processing.parser as parser
import processing.organizer as organizer
import processing.process_batch as process_batch
import processing.align as align
import os

args = parse_arguments()

input_folder = os.path.normpath(args.input_folder)
output_folder = os.path.normpath(args.output_folder)

if args.action == "convert":
	parser.convert_folder(input_folder, output_folder, print_cli)
elif args.action == "organize":
	mode = next(m for m in organizer.Mode if m.name.lower() == args.mode)
	organizer.separate_hdr_sets(input_folder, output_folder, args.threshold, args.max_nb_per_set, mode, print_cli)
elif args.action == "process":
	options = parse_process_options(args)
	process_batch.process_batch(input_folder, output_folder, options, print_cli)
elif args.action == "stitch":
	align.auto_align(input_folder, output_folder, args.match_ratio_threshold, print_cli)
else:
	print("\"{}\" not implemented yet".format(args.action))
