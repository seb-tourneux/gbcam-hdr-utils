from argparse import ArgumentParser
from datetime import datetime
import processing.organizer as organizer
import processing.process_batch as process_batch
import processing.align_fourier as align_fourier
import processing.making_of as making_of
import argparse

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
    default_options = organizer.default_options()
    parser_organize = subparsers.add_parser('organize', help='Organize AEB sequences into separate folders')
    parser_organize.add_argument("-t", "--threshold", help="Threshold of luminosity between two consecutive image to be separated", dest="threshold", default=default_options["threshold"], type=float)
    parser_organize.add_argument("-n", "--max_nb_per_set", help="Maximum number of images per set. Sets strictly bigger than this value will be handled according to mode", dest="max_nb_per_set", default=default_options["max_nb_per_set"], type=int)
    modes = [m.name.lower() for m in organizer.Mode]
    parser_organize.add_argument("-m", "--mode", help="Mode to manage sets bigger than max_nb_per_set", choices=modes, dest="mode", default=default_options["mode"])
    #add_in_out_folder_args(parser_organize)

def add_subparser_process(subparsers):
    default_options = process_batch.default_options()
    parser_process = subparsers.add_parser('process', help='Process pictures sets : average, create gifs. Processing is done subfolder by subfolder')
    for (act, help_msg) in processing_actions:
        parser_process.add_argument("--{}".format(act), action="store_true", help=help_msg) 
    parser_process.add_argument("--gif_frame_duration", help="Duration of 1 frame of the gif generated (ms)", dest="gif_frame_duration", default=default_options["gif_frame_duration"], type=int)
    parser_process.add_argument("--scale", help="Scaling factor", dest="scale_factor", default=default_options["scale_factor"], type=int)
    parser_process.add_argument("--border_path", help="Path to a 160x144 border image", dest="border_path", default=default_options["border_path"])
    parser_process.add_argument("--palette", help="String with 4 hexa string: ex \"#01162c #0460bf #7cbde8 #fff7e1\"", dest="palette", default=default_options["palette"])

    #add_in_out_folder_args(parser_process)
    return parser_process

def add_subparser_stitch(subparsers):
    parser_stitch = subparsers.add_parser('stitch', help='Stitch pictures together')
    parser_stitch.add_argument("--method", help="Stitching method", dest="method", choices=["feature", "fourier"], default="feature", type=str)
    parser_stitch.add_argument("--match_ratio_threshold", help="Threshold of match quality", dest="match_ratio_threshold", default=0.5, type=float)

def parse_rgb(value):
    try:
        r, g, b = map(int, value.split(","))
        if not all(0 <= x <= 255 for x in (r, g, b)):
            raise ValueError
        return (r, g, b)
    except ValueError:
        raise argparse.ArgumentTypeError("RGB must be three integers (0-255) separated by commas, e.g., '255,255,255'.")

def add_subparser_making_of(subparsers):
    default_options = making_of.default_options()
    parser_making_of = subparsers.add_parser('making_of', help='Create making-of gifs')
    parser_making_of.add_argument('--frame_duration', dest="frame_duration", help="in ms", default=default_options["frame_duration"], type=int)
    parser_making_of.add_argument('--freeze_duration', dest="freeze_duration", help="in ms", default=default_options["freeze_duration"], type=int)
    parser_making_of.add_argument("--bg_color", dest="bg_color", type=parse_rgb, default=default_options["bg_color"], help="Background color as R,G,B (e.g., 255,255,255)")

def add_subparser_auto(subparsers):
    parser_auto = subparsers.add_parser('auto', help='Auto process (organize, process, stitch, making-of)')
    parser_auto.add_argument("--json_config", dest="json_config", help="Path to a json config file", type=str)

def check_process_options(args, parser_process):
    if args.action == "process":
        args_dict = vars(args)
        standard_processing = any(args_dict[process_act] for (process_act, _) in processing_actions)
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
    add_subparser_making_of(subparsers)
    add_subparser_auto(subparsers)

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

def parse_organize_options(args):
    options = {'threshold' : args.threshold,
            'max_nb_per_set' : args.max_nb_per_set,
            'mode' : next(m for m in organizer.Mode if m.name.lower() == args.mode)
            }
    return options

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

def parse_making_of_options(args):
    options = {'frame_duration' : args.frame_duration,
            'freeze_duration' : args.freeze_duration,
            'bg_color' : args.bg_color
         }
    return options