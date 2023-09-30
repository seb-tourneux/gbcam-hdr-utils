import cProfile
import processing.parser as parser

#cProfile.run('parser.convert_folder("input/sav/single", "output/test/", print)', 'restats')
#cProfile.run('parser.convert_folder("input/sav/dump_ram_128", "output/test/", print)', 'restats')
cProfile.run('parser.convert_folder("input/sav/dump_fram_2048", "output/test/", print)', 'restats')

# use perf_restats.py to display

