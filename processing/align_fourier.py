import cv2
import numpy as np
import processing.align as align
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image
import os
from pathlib import Path

from dataclasses import dataclass
import numpy.typing as npt

@dataclass
class ImageData:
    img_idx : int
    img : npt.NDArray
    fft : npt.NDArray
    path : Path
    shift_from_parent : tuple[int, int] | None
    parent_idx : int | None

@dataclass(frozen=True)
class CorrelationData:
    parent_idx : int
    child_idx : int
    correlation : float
    shift : tuple
    correlation_magnitude : npt.NDArray

def pad_to_square(arr):
    h, w = arr.shape
    if h == w:
        return arr

    if h > w:
        pad_total = h - w
        pad_left = pad_total // 2
        pad_right = pad_total - pad_left
        padding = ((0, 0), (pad_left, pad_right))
    else:
        pad_total = w - h
        pad_top = pad_total // 2
        pad_bottom = pad_total - pad_top
        padding = ((pad_top, pad_bottom), (0, 0))

    padded = np.pad(arr, padding, mode='constant', constant_values=0)
    return padded

def show_image(img, title):
    plt.imshow(img, cmap='gray')
    plt.title(title)
    plt.show(block=True)

def compute_fft(img):
    image_gray = img[:,:,0]/255
    return np.fft.fft2(pad_to_square(image_gray))

def fft_test(img, path : Path):
    fft_result = compute_fft(img)
    fft_shifted = np.fft.fftshift(fft_result)

    magnitude = np.abs(fft_shifted)
    magnitude_log = np.log1p(magnitude)
    magnitude_log /= magnitude_log.max()
    #show_image(magnitude_log, f"magnitude log {path.stem}")
    return fft_result


def create_image_data(idx, img, path : Path):
    fft = compute_fft(img)
    return ImageData(idx, img, fft, path, None, None)


def compute_cps(fft1, fft2):
    product = fft1 * np.conj(fft2)
    magnitude = np.abs(product)
    magnitude[magnitude == 0] = 1e-8
    cps = product / magnitude
    cps_shifted = np.fft.fftshift(cps)
    return cps_shifted


def find_peak_location(cps):
    correlation = np.fft.ifft2(np.fft.ifftshift(cps))
    correlation_magnitude = np.abs(correlation)

    flat_index = correlation_magnitude.argmax()
    peak_val = correlation_magnitude.flat[flat_index]
    peak_coords = np.unravel_index(flat_index, correlation.shape)

    return peak_coords, peak_val, correlation_magnitude

def compute_shift(peak_coords, shape):
    shifts = []
    for p, s in zip(peak_coords, shape):
        shift = p if p < s // 2 else p - s
        shifts.append(shift)
    return tuple(shifts)

def display_cps(cps):
    phase = np.angle(cps)

    plt.imshow(phase, cmap='gray', extent=(-0.5, 0.5, -0.5, 0.5))
    plt.colorbar(label="Phase (radians)")
    plt.title("Normalized Cross Power Spectrum (Phase)")
    plt.axis("off")
    plt.show()

def array_border(array, spacing):
    spacing = 15
    dot_length = 3
    val = 0.3
    rows, cols = array.shape
    for i in range(cols):
        if i % spacing < dot_length:
            array[0, i] *= val
            array[rows-1, i] *= val

    for j in range(rows):
        if j % spacing < dot_length:
            array[j, 0] *= val
            array[j, cols-1] *= val
    return array

def preview_shift(data1, data2, shift):
    
    array1 = data1.img[:,:,0]
    array2 = data2.img[:,:,0]
    height = 3*array1.shape[0]
    width = 3*array1.shape[1]
    
    result = np.zeros((height, width))
    start_y = (height - array1.shape[0]) // 2
    start_x = (width - array1.shape[1]) // 2
    
    result[start_y:start_y + array1.shape[0], start_x:start_x + array1.shape[1]] = array1
    
    result_only_first = result.copy()

    offset_x = shift[1] + start_x
    offset_y = shift[0] + start_y
    result[offset_y:offset_y + array2.shape[0], offset_x:offset_x + array2.shape[1]] = array2

    non_zero_rows = np.any(result != 0, axis=1)
    non_zero_cols = np.any(result != 0, axis=0)
    result = result[non_zero_rows, :][:, non_zero_cols]
    result_only_first = result_only_first[non_zero_rows, :][:, non_zero_cols]

    return result, result_only_first
    
def show_corr(data1, data2, correlation_magnitude, shift, correlation_value):
    
    fig, axes = plt.subplot_mosaic(
        [["img0", "img1", "res", "res"],
        ["corr", "corr", "res", "res"],
        ["corr", "corr", "res", "res"]]
    )
    for i, data in enumerate([data1, data2]):
        axes[f"img{i}"].imshow(data.img, cmap='gray')
        axes[f"img{i}"].set_axis_off()

    axes["img0"].set_title("Reference")
    axes["img1"].set_title("Match")
    
    axes["corr"].imshow(correlation_magnitude, cmap='gray')
    axes["corr"].set_title(f"Max phase correlation: {correlation_value}")

    preview, preview_only_first = preview_shift(data1, data2, shift)
    im = axes["res"].imshow(preview, cmap='gray')
    axes["res"].set_title(f"Found offset: ({shift[1]}, {-shift[0]})")
    axes["res"].set_axis_off()
    
    def update(frame):
        if frame % 2 == 0:
            im.set_array(preview)
        else:
            im.set_array(preview_only_first)
        return [im]
    ani = FuncAnimation(fig, update, frames=10, interval=500, blit=True)
    
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()

    plt.show(block=True)

def compute_shift_cps(data1 : ImageData, data2 : ImageData):
    cps = compute_cps(data1.fft, data2.fft)
    #display_cps(cps)
    
    (peak_coords, peak_val, correlation_magnitude) = find_peak_location(cps)
    shift = compute_shift(peak_coords, data1.fft.shape)
    #show_corr(data1, data2, correlation_magnitude, shift, peak_val, f"Correlation_magnitude {data1.path.stem} <> {data2.path.stem}")
    return shift, peak_val, correlation_magnitude

def compute_correlation(data1 : ImageData, data2: ImageData):
    (shift, correlation, correlation_magnitude) = compute_shift_cps(data1, data2)
    return CorrelationData(data1.img_idx, data2.img_idx, correlation, shift, correlation_magnitude)

def auto_align(in_folder, out_folder, threshold, update_callback):

    images = align.load_img_and_paths_cv2(in_folder)
    datas = [create_image_data(idx, img, path) for (idx, (img, path)) in enumerate(images)]

    target_resolution = len(images) * max(np.max([img.shape for (img, _) in images], axis=0))
    
    datas[0].parent_idx = -1
    datas[0].shift_from_parent = (0,0)
    
    while True:
        candidates = [i for i in datas if i.shift_from_parent is None]
        if not candidates:
            break
        placeds = [i for i in datas if i.shift_from_parent is not None]
        
        correlation_datas = []
        for placed in placeds:
            for candidate in candidates:
                correlation_datas.append(compute_correlation(placed, candidate))

        best_corr = max(correlation_datas, key=lambda data: data.correlation)

        show_corr(datas[best_corr.parent_idx], datas[best_corr.child_idx], best_corr.correlation_magnitude, best_corr.shift, best_corr.correlation)

        # TODO threshold, limited number of tries
        
        found = datas[best_corr.child_idx]
        found.parent_idx = best_corr.parent_idx
        found.shift_from_parent = best_corr.shift

    placeds = [i for i in datas if i.shift_from_parent is not None]
    update_callback(f"Managed to stitch {len(placeds)}/{len(datas)} images")
    
    # TODO output results
