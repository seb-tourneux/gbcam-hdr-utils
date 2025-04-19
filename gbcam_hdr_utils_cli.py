from cli.parse_arguments import *

import processing.parser as parser
import processing.organizer as organizer
import processing.process_batch as process_batch
import processing.making_of as making_of
import processing.align as align
import processing.align_fourier as align_fourier
import processing.auto as auto
import os

args = parse_arguments()

input_folder = os.path.normpath(args.input_folder)
output_folder = os.path.normpath(args.output_folder)

if args.action == "convert":
    parser.convert_folder(input_folder, output_folder, print_cli)
elif args.action == "organize":
    options = parse_organize_options(args)
    organizer.separate_hdr_sets(input_folder, output_folder, options, print_cli)
elif args.action == "process":
    options = parse_process_options(args)
    process_batch.process_batch(args.input_folder, args.output_folder, options, print_cli)
elif args.action == "making_of":
    options = parse_making_of_options(args)
    # TODO add option to specify different folders for png and gif
    making_of.make_gif_all(args.input_folder, args.input_folder, args.output_folder, options, print_cli)
elif args.action == "stitch":
    if args.method == "fourier":
        align_fourier.auto_align(input_folder, output_folder, args.match_ratio_threshold, print_cli)
    else:
        align.auto_align(input_folder, output_folder, args.match_ratio_threshold, print_cli)
elif args.action == "auto":
    auto.auto_process_from_json(args.input_folder, args.output_folder, args.json_config, print_cli)
else:
    print(f'Unsupported action: "{args.action}')
