import cProfile
import processing.parser as parser
from cli.parse_arguments import print_cli

#cProfile.run('parser.convert_folder("input/sav/single", "output/test/", print_cli)', 'restats')
#cProfile.run('parser.convert_folder("input/sav/dump_ram_128", "output/test/", print_cli)', 'restats')
cProfile.run('parser.convert_folder("input/sav/dump_fram_2048", "output/test/", print_cli)', 'restats')

# use perf_restats.py to display

