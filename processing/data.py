from processing.files_utils import *
from PIL import Image as PILImage
from PIL import ImageColor as PILImageColor
import numpy
from PIL.ImageQt import ImageQt
import os
import processing.infos as infos
import processing.process as process

def crop(img_pil):
	s = img_pil.size
	if s == (160, 144):
		#remove frame
		img_pil = img_pil.crop( (16, 16, 16+128, 16+112) )
	return img_pil

def paste_in_frame(picture_img, border_img):
	img = picture_img
	if border_img is not None:
		res = border_img.copy()
		res.paste(picture_img, (16, 16))
		return res
	return img

	

def PIL_to_array(img, border_img = None):
	img = img.convert('L')
	img = crop(img)
	
	img = paste_in_frame(img, border_img)
	
	arr = numpy.array(img,dtype=float) / 255
	return arr

def get_arrays_and_path_from_file_list(imlist, border_path=None):
	if not imlist:
		return

	# Assuming all images are the same size, get dimensions of first image
	w,h=PILImage.open(imlist[0]).convert('L').size
	N=len(imlist)

	border_img = None
	if border_path is not None:
		border_img = PILImage.open(border_path).convert('L')
	

	array_path_list = []
	for img_path in imlist:
		img = PILImage.open(img_path)
		arr = PIL_to_array(img, border_img)
		array_path_list.append( (arr, img_path) )
		
	return array_path_list


def get_arrays_and_path_from_folder(folder_path, border_path = None):
	all_files = get_image_files(folder_path)

	print("== Processing {} image(s) in folder {}".format(len(all_files), folder_path))

	return get_arrays_and_path_from_file_list(all_files, border_path)

def array_to_ImageQt(arr):
	formatted = (255*arr).astype('uint8')
	imgPIL = PILImage.fromarray(formatted)
	return ImageQt(imgPIL)

def resize_PIL(img_pil, scale_factor):
	if scale_factor != 1.0:
		w, h = img_pil.size
		return img_pil.resize((int(w*scale_factor), int(h*scale_factor)), PILImage.NEAREST)
	else :
		return img_pil


def apply_palette(pixel, palette):
	try:
		avg = (sum(pixel) / len(pixel)) / 255.0
	except TypeError:
		avg = pixel / 255.0

	if avg < 0.2:
		return palette[0]
	elif avg < 0.6:
		return palette[1]
	elif avg < 0.8:
		return palette[2]
	else:
		return palette[3]
	

def PIL_apply_palette(img, str_palette):
	pixels = img.load() # create the pixel map
	col_palette = [PILImageColor.getrgb(s) for s in str_palette.split()]
	for i in range(img.size[0]): # for every pixel:
		for j in range(img.size[1]):
			new_pixel = apply_palette(pixels[i,j], col_palette)
			img.putpixel((i, j), new_pixel)
	return img

def finalizeAndSave(arr, scale_factor, color_palette, output_dir, aFolder, aSuffix):
	arr=numpy.array(numpy.round(255.0*arr),dtype=numpy.uint8)

	out=PILImage.fromarray(arr,mode="L")

	if color_palette:
		# not sure if mode is input or output
		out=out.convert("RGB")
		out=PIL_apply_palette(out, color_palette)

		
	out = resize_PIL(out, scale_factor)
	lastDir = os.path.basename(os.path.normpath(aFolder))
	imgOutput = output_dir + "/" + lastDir + "_" + aSuffix + ".png"
	out.save(imgOutput)
	print("Saved {}".format(imgOutput))

def images_anim_depth(frames):
	arrays = [PIL_to_array(img) for img in frames]
	pil_avg = []
	for i, _ in enumerate(arrays):
		arr = process.average(arrays[:i+1]) # average from 0 to i
		arr=numpy.array(numpy.round(255.0*arr),dtype=numpy.uint8)
		pil_avg.append(PILImage.fromarray(arr,mode="L"))
	
	return pil_avg

def make_gif(images_folder, output_folder, scale_factor, gifFrameDurationMs, method, border_path = None):
	lastDir = os.path.basename(os.path.normpath(images_folder))
	imgGifOutput = output_folder + "/" + lastDir + "_anim"

	allfiles=os.listdir(images_folder)
	im_files=[images_folder+"/"+filename for filename in allfiles if  filename[-4:] in [".png",".PNG", ".bmp"]]
	im_files.sort()
	

	
	border_img = None
	if border_path is not None:
		border_img = PILImage.open(border_path).convert('L')
		

	frames = [PILImage.open(image) for image in im_files]
	file_suffix = ""
	if method == "gif_descend":
		frames.reverse()
		file_suffix = "_reverse"
	if method == "gif_depth_reverse":
		frames.reverse()
		frames = images_anim_depth(frames)
		file_suffix = "_depth_reverse"
	if method == "gif_depth":
		frames = images_anim_depth(frames)
		file_suffix = "_depth"
		
	frames = list(map(lambda f: crop(f), frames))
	frames = list(map(lambda f: paste_in_frame(f, border_img), frames))
	frames = list(map(lambda f: resize_PIL(f, scale_factor), frames))

	frame_one = frames[0]
	
	gif_filename = "{}_{}ms{}.gif".format(imgGifOutput, gifFrameDurationMs, file_suffix)

	frame_one.save(gif_filename, format="GIF", append_images=frames[1:],
									save_all=True, duration=gifFrameDurationMs, loop=0)
	
	print("Saved {}".format(gif_filename))

def save_image_array(arr, conv_to_255, path):
	if conv_to_255:
		arr = numpy.round(255.0*arr)
	arr= numpy.array(arr,dtype=numpy.uint8)
	pilImg = PILImage.fromarray(arr)
# 	exif_data = {
# 		271: "Gameboy Camera",
# 		305: infos.get_software_name()}
	#pilImg.info["exif"] = exif_data
	pilImg.save(path)