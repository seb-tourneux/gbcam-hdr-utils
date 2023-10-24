import cv2
import numpy as np
import processing.data as data
import processing.files_utils as files_utils
import matplotlib.pyplot as plt
from PIL import Image


input_dir = "E:/Data/Prods/2022/Photo/GameboyCamera/2023_09_03/align_poteau1"
output_dir = "E:/Data/Prods/2022/Photo/GameboyCamera/2023_09_03/test_align1_res"






def match_ratio_fun(x):
	return x[0].distance/x[1].distance

def compute_delta(m, kp1, kp2):
	# Get the matching keypoints for each of the images
	img1_idx = m.queryIdx
	img2_idx = m.trainIdx

	# x - columns
	# y - rows
	# Get the coordinates
	p1 = kp1[img1_idx].pt
	p2 = kp2[img2_idx].pt
	
	delta = np.subtract(p1, p2)
	#print("1 : {} | 2 : {}, delta {}".format( p1, p2, delta ))
	return delta

def bounding_box(A):
	return (np.min(A, axis=0), np.max(A, axis=0))
	

def find_delta(img1, img2):
	# Initiate SIFT detector
	sift = cv2.SIFT_create(sigma = 1) #sigma = 1 => do not blur
	# find the keypoints and descriptors with SIFT
	kp1, des1 = sift.detectAndCompute(img1,None)
	kp2, des2 = sift.detectAndCompute(img2,None)
	# BFMatcher with default params
	bf = cv2.BFMatcher()
	matches = bf.knnMatch(des1,des2,k=2)
	
	match_threshold = 0.7
	max_nb_matches = 5
	
	img3 = None
	
	matches = sorted(matches, key=match_ratio_fun) # sort best matches first
	matches= matches[:max_nb_matches]
	
	# filter not good matches
	matches = list(filter(lambda m : match_ratio_fun(m) < match_threshold, matches))
	#for m in matches:
	#	print(match_ratio_fun(m))
	
	average_delta = None
	if len(matches) != 0:
		# cv2.drawMatchesKnn expects list of lists as matches.
		to_print = list(map(lambda x : [x[0]], matches))
		img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,to_print,None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
		
		matches = list(map(lambda x : x[0], matches))
		deltas = list(map(lambda x :compute_delta(x, kp1, kp2), matches))
		array_deltas = np.array([*deltas])
	
		average_delta = array_deltas.mean(axis=0)
		average_delta = average_delta.astype(int)
		
	return (img3, img2, average_delta)

#	diff = array_deltas-average_delta
#	print (array_deltas)
#	print (average_delta)
#	print (diff)
#	variance = np.linalg.norm(diff, ord=2) 
#	print("variance {}".format(variance))


def align_images(img1, img2, delta, accepted_images_delta):
	image1 = img1
	image2 = img2
	# Create a blank canvas for the new image
	new_shape = (image1.shape[0]+2*image2.shape[0], image1.shape[1]+2*image2.shape[1], 3)
	
	
	background_color = (255, 255, 255)  # Background color in BGR format (white in this case)
	new_image = np.zeros(new_shape, dtype=np.uint8)
	new_image[:, :] = background_color
	
	# Calculate positions where you want to place the images
	start_image1 = np.array([image2.shape[0], image2.shape[1]])
	start_image2 = np.add(start_image1, delta)
	
	end_image1 = np.array([start_image1[1] + image1.shape[0], start_image1[0] + image1.shape[1]])
	end_image2 = np.array([start_image2[1] + image2.shape[0], start_image2[0] + image2.shape[1]])
	
	# Paste the images onto the new image
	new_image[start_image1[1]:end_image1[0], start_image1[0]:end_image1[1]] = image1
	new_image[start_image2[1]:end_image2[0], start_image2[0]:end_image2[1]] = image2
	minBox, maxBox = bounding_box([start_image1, start_image2, end_image1, end_image2])
	new_image = new_image[minBox[1]:maxBox[0], minBox[0]:maxBox[1]]
	
	accepted_images_delta.append((img2, delta))
	
	def global_delta(d):
		return np.subtract(np.add(delta, start_image1), minBox)
	
	accepted_images_delta = [(i,global_delta(d)) for (i, d) in accepted_images_delta ]

	return new_image



def process_one_match(unmatched_images, res, accepted_images_delta, nb_fails):
	img = unmatched_images.pop(0)
	if res is None : 
		res = img.copy()
		accepted_images_delta.append((img, np.array([0,0]) ))
		img = unmatched_images.pop(0)

	d = find_delta(res, img)
	return (d, res)
		
		
		


def process_match_accept_decline(unmatched_images, res, accepted_images_delta, nb_fails, img_matched, delta, accepted):
	#manual_reject = manual_check and input("Accept ? y/n: ") == 'n'
	if (delta is None) or (not accepted) :
		unmatched_images.append(img_matched) # process later, maybe we'll find better matches
		nb_fails[0] += 1
		#print("FAIL : nb images {}, nb fail {}".format(len(unmatched_images), nb_fails))
	else:

		nb_fails[0] = 0
		res = align_images(res, img_matched, delta, accepted_images_delta)
	return res


# accepted_images_delta = []

# manual_check = True

# res = None
# nb_fails = [0]
# while len(unmatched_images) != 0 and nb_fails[0] < len(unmatched_images):
# 	process_one_match(unmatched_images, res, accepted_images_delta, nb_fails)

			

def save_layers(accepted_images_delta, unmatched_images, out_folder, set_name):

	if len(unmatched_images) > 0:
		ref_img = unmatched_images[0]
	elif len(accepted_images_delta) > 0:
		ref_img = accepted_images_delta[0][0]
	else:
		return
		
	img_size = (ref_img.shape[0], ref_img.shape[1])

	# manage some unmatched pictures
	extra =(0,0)
	offset = (20,20)
	if len(unmatched_images) != 0:
		extra = img_size + offset
	
	deltas_global = list(list(zip(*accepted_images_delta))[1])
	minBox, maxBox = bounding_box(deltas_global)
	
	# todo correct
	size_accepted = (maxBox[0]+img_size[1], maxBox[1]+img_size[0])
	total_size = (size_accepted[0] + extra[1], size_accepted[1] + extra[0])
	pos_unmatched = (size_accepted[0]+offset[1], size_accepted[1]+offset[0])
	
	# add match/umatched flag
	res_images_delta = [(i,d,True) for (i,d) in accepted_images_delta]
	res_images_delta.extend([(img, pos_unmatched, False) for img in unmatched_images])

	background = Image.new("RGBA",total_size)
	
	blended_all = background.copy()
	for (i, (img, delta, matched)) in enumerate(res_images_delta):
		cur_bg = background.copy()
		pilImg = Image.fromarray(img)
		cur_bg.paste(pilImg, (delta[0], delta[1]))
		blended_all.paste(pilImg, (delta[0], delta[1]))
		cur_bg.save(out_folder + "/{}{}_{}.png".format(set_name, "" if matched else "_unmatched", i))
	
	suffix = "partial_stitch" if len(unmatched_images) > 0 else "stitch"
	total_file_path = out_folder + "/all_{}_{}.png".format(set_name, suffix)
	blended_all.save(total_file_path)

def load_folder_cv2(folder):
	array_paths = data.get_arrays_and_path_from_folder(folder)
	if not array_paths:
		return None
	unmatched_images = [ cv2.imread(p) for (_, p) in array_paths ]
	return unmatched_images