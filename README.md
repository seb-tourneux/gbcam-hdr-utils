# gbcam-hdr-utils

Utilities and GUI for processing HDR Gameboy Camera pictures.

## Features
For HDR image processing, each of the steps is meant to be done successively. For single image processing, the "Process" step can also be interesting.
Note that no file is modified nor deleted, each step only creates new files in the output folder.

### Convert
Convert a `.sav` dump to `.png` files. Supports single picture dump (4 KiB), original ram dump (128 KiB) and multiple ram dump concatenated in the same file (n times 128 KiB, such as [PHOTO!](https://github.com/untoxa/gb-photo) dump).

### Organize
Used with AEB sequences : sequence of pictures of the same subject with increasing or decreasing exposure time. From a folder containing several AEB sequences, separate each sequence into a specific folder. This is done by comparing two successive pictures (ordered by names), so input pictures order is important.

### Process
Different processing utilities:
* blend AEB sequences (subfolder by subfolder)
* make gifs from folder of pictures
* add a border
* scale the picture

### Stitch
Stitch several pictures together using corresponding features. To keep up with the pixel art style of Gameboy Camera pictures, the stitch is done only by translating the picture, and not by rotating or inversing the homography.
When using the graphical interface, one can approve or disprove each found match. Depending on the input pictures, and the overlap percentage, not all pictures can be matched, and sometimes have to be aligned manually.
The output is several png images, with transparency that can be opened as layers in an image processing software, for further processing.

## Interface

A graphical interface and command line interface are available.

### Command line

```console
python gbcam_hdr_utils_cli.py -i path/to/input_folder -o path/to/output_folder <action> [OPTIONS]
```
`<action>` being one of {`convert`,`organize`,`process`,`stitch`}

Use `python gbcam_hdr_utils_cli.py <action> --help`  for further help about a specific action.

## References/Acknowledgements
* [Structure of the Gameboy Camera Save Data](https://funtography.online/wiki/Structure_of_the_Game_Boy_Camera_Save_Data)
* [Gameboy 2BPP Graphics Format](https://www.huderlem.com/demos/gameboy2bpp.html)
* [Gameboy Camera Gallery](https://github.com/HerrZatacke/gb-printer-web)
* [Game Boy Gamera Club Discord](https://discord.gg/C7WFJHG)

## TODO

### Convert
- [x] Support Photo rolls dump (2048Ko)
- [x] CLI
- [x] GUI
- [ ] read/write metadata
- [ ] ignore deleted pictures/chech checksum ?

### Organize
- [x] GUI
- [x] link to core
- [x] CLI

### Process
- [x] GUI
- [x] link to core
- [x] implement increasing depth
- [x] CLI

### Stitch
- [ ] GUI
- [ ] link to core
- [ ] CLI

#### Nice to have
- [ ] pictures previews
- [ ] input filenames and nb of files
- [ ] save config (last opened tab, paths for each step, settings)

### Code

- [ ] code structure (`src`) relative imports
- [ ]  `__main__.py`,  `__init__.py`

