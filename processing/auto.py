import processing.organizer as organizer
import processing.process_batch as process_batch
import processing.align_fourier as align_fourier
import processing.making_of as making_of
import json
import os
from pathlib import Path

def auto_process_from_json(in_folder, out_folder, json_path:Path, update_callback = None):
    options_org = None
    options_proc = None
    options_stitch = None
    options_making_of = None
    options = None
    with open(json_path, "r") as f:
        options = json.load(f)
    options_org = options["organize"] if options is not None and "organize" in options else organizer.default_options()
    options_proc = options["process"] if options is not None and "process" in options else process_batch.default_options()
    options_stitch = options["stitch"] if options is not None and "stitch" in options else align_fourier.default_options()
    options_making_of = options["making_of"] if options is not None and "making_of" in options else making_of.default_options() 

    auto_process(in_folder, out_folder, options_org, options_proc, options_stitch, options_making_of, update_callback)

def making_of_from_gif_type(in_folder_png, in_folder_gif, out_folder, gif_type, options_proc: dict, options_making_of: dict, update_callback):
    if gif_type in options_proc and options_proc[gif_type]:
        making_of_folder = os.path.join(out_folder, f"04_making_of_{gif_type}")
        os.makedirs(making_of_folder, exist_ok=True)
        in_folder_gif = os.path.join(in_folder_gif, gif_type)
        making_of.make_gifs(in_folder_png, in_folder_gif, making_of_folder, update_callback)
        making_of.make_gif_all(in_folder_png, in_folder_gif, making_of_folder, options_making_of, update_callback)
        update_callback(f"Making-of {gif_type} done.")

def auto_process(in_folder, out_folder, options_org: dict, options_proc: dict, options_stitch: dict, options_making_of: dict, update_callback = None):
    org_folder = os.path.join(out_folder, "01_organize")
    proc_folder = os.path.join(out_folder, "02_process")
    stitch_folder = os.path.join(out_folder, "03_stitch")

    if options_org is not None:
        os.makedirs(org_folder, exist_ok=True)
        organizer.separate_hdr_sets(in_folder, org_folder, options_org, update_callback)
        update_callback("Organize done.")
    if options_proc is not None:
        os.makedirs(proc_folder, exist_ok=True)
        process_batch.process_batch(org_folder, proc_folder, options_proc, update_callback)
        update_callback("Process done.")
    if options_stitch is not None:
        os.makedirs(stitch_folder, exist_ok=True)
        align_fourier.auto_align(proc_folder, stitch_folder, options_stitch, update_callback)
        update_callback("Stitch done.")
    if options_making_of is not None and options_proc is not None:
        making_of_from_gif_type(stitch_folder, proc_folder, out_folder, "gif_ascend", options_proc, options_making_of, update_callback)
        making_of_from_gif_type(stitch_folder, proc_folder, out_folder, "gif_descend", options_proc, options_making_of, update_callback)
        making_of_from_gif_type(stitch_folder, proc_folder, out_folder, "gif_depth", options_proc, options_making_of, update_callback)
        making_of_from_gif_type(stitch_folder, proc_folder, out_folder, "gif_depth_reverse", options_proc, options_making_of, update_callback)





