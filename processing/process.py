#from typing import TYPE_CHECKING, Any
import numpy as np
import cv2 as cv
from enum import Enum
from scipy import signal


class Method(Enum):
	AVERAGE = 1
	CONTRAST = 2


def average(arrays):
	arr=np.zeros(arrays[0].shape,float)
	N = len(arrays)
	for imarr in arrays:
		arr= arr + imarr/N
	return arr


def gammaCorrection(arr, gamma):
	invGamma = 1 / max(0.01, gamma)

	return arr ** invGamma


def merge_mertens(arrays, exposure):
	
	#return average(arrays)

	constrast = 0.5
	#TODO
	print("Mertens : Wcontrast{} Wexposure {}".format(constrast, exposure))
	merge_mertens = cv.createMergeMertens(constrast, 0.0, exposure)
	res_mertens = merge_mertens.process(arrays)
	
	res_mertens = np.interp(res_mertens, (res_mertens.min(), res_mertens.max()), (0, 1))
	return res_mertens


def mask_contrast(image, constrast_weight):
	kernel = np.array([	[0, -1, 0], 
						[-1, 4, -1.],
						[0, -1, 0]], float)
	kernel /= 4.0
	conv = np.absolute(signal.convolve2d(image, kernel, boundary='symm', mode='same'))
	res = conv + constrast_weight * np.ones(image.shape,float)
	return res

def compute_masks(images, method, constrast_weight):
	masks = []
	contrast_method = Method.CONTRAST
	for image in images:
		if method == Method.CONTRAST:
			mask = mask_contrast(image, constrast_weight)
			#mask += np.ones(image.shape,float)
		else:
			mask = np.ones(image.shape,float)
		masks.append(mask)
		
	mask_sum=np.zeros(images[0].shape,float)
	for (image, mask) in zip(images, masks):
		mask_sum += mask
	
	n = len(masks)
	#masks = [ mask * n / (mask_sum) for mask in masks]
	
	for n in range(len(masks)):
		m = masks[n]
		m [ mask_sum == 0 ] = 1
		masks[n] = m

	return masks

def fusion(images, masks):
	n = len(images)
	coef = 1.0 / float(n)
	res=np.zeros(images[0].shape,float)
	mask_sum=np.zeros(images[0].shape,float)
	for (image, mask) in zip(images, masks):
		res += image * mask * coef
	
	return res