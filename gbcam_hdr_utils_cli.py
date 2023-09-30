from cli.parse_arguments import *
import processing.parser as parser

args = parse_arguments()

if args.action == "convert":
	parser.convert_folder(args.input_folder, args.output_folder, print_cli)

# todo actuel process