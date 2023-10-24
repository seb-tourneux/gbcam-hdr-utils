from cli.parse_arguments import *

import processing.parser as parser
import processing.organizer as organizer
import processing.process_batch as process_batch


args = parse_arguments()

if args.action == "convert":
	parser.convert_folder(args.input_folder, args.output_folder, print_cli)
elif args.action == "organize":
	mode = next(m for m in organizer.Mode if m.name.lower() == args.mode)
	organizer.separate_hdr_sets(args.input_folder, args.output_folder, args.threshold, args.max_nb_per_set, mode, print_cli)
elif args.action == "process":
	options = parse_process_options(args)
	process_batch.process_batch(args.input_folder, args.output_folder, options, print_cli)
#elif args.action == "stitch":
else:
	print("\"{}\" not implemented yet".format(args.action))
