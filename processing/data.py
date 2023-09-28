from processing.files_utils import *
from PIL import Image as PILImage
import numpy
from PIL.ImageQt import ImageQt
import os

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
		img = img.convert('L')
		img = crop(img)
		
		img = paste_in_frame(img, border_img)
		
		arr = numpy.array(img,dtype=float) / 255
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


def finalizeAndSave(arr, scale_factor, output_dir, aFolder, aSuffix):
	arr=numpy.array(numpy.round(255.0*arr),dtype=numpy.uint8)
	out=PILImage.fromarray(arr,mode="L")
	out = resize_PIL(out, scale_factor)

	lastDir = os.path.basename(os.path.normpath(aFolder))
	imgOutput = output_dir + "/" + lastDir + "_" + aSuffix + ".png"
	out.save(imgOutput)
	print("Saved {}".format(imgOutput))
	
def make_gif(images_folder, output_folder, scale_factor, gifFrameDurationMs, border_path = None, reverse = False):
	lastDir = os.path.basename(os.path.normpath(images_folder))
	imgGifOutput = output_folder + "/" + lastDir + "_anim"

	allfiles=os.listdir(images_folder)
	im_files=[images_folder+"/"+filename for filename in allfiles if  filename[-4:] in [".png",".PNG", ".bmp"]]
	im_files.sort()
	if reverse:
		im_files.reverse()
	
	border_img = None
	if border_path is not None:
		border_img = PILImage.open(border_path).convert('L')
		

	frames = [PILImage.open(image) for image in im_files]
	frames = list(map(lambda f: crop(f), frames))
	frames = list(map(lambda f: paste_in_frame(f, border_img), frames))
	frames = list(map(lambda f: resize_PIL(f, scale_factor), frames))

	frame_one = frames[0]
	
	gif_filename = "{}_{}ms{}.gif".format(imgGifOutput, gifFrameDurationMs, "_reverse" if reverse else "")

	frame_one.save(gif_filename, format="GIF", append_images=frames[1:],
									save_all=True, duration=gifFrameDurationMs, loop=0)
	
	print("Saved {}".format(gif_filename))
