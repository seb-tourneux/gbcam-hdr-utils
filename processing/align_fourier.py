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
from typing import Annotated
from typing_extensions import TypeAlias

Int2: TypeAlias = Annotated[npt.NDArray[np.int_], (2,)]


debug_level = 0
def debug_fine(f):
    global debug_level
    if debug_level >= 2:
        f()

def debug(f):
    global debug_level
    if debug_level >= 1:
        f()

@dataclass
class ImageData:
    img_idx : int
    img : npt.NDArray
    fft : npt.NDArray
    path : Path
    shift_from_parent : Int2 | None
    parent_idx : int | None
    global_shift : Int2 | None

@dataclass(frozen=True)
class CorrelationData:
    parent_idx : int
    child_idx : int
    correlation : float
    shift : Int2
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
    return ImageData(idx, img, fft, path, None, None, None)


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
    
def show_corr(data1, data2, correlation_magnitude, shift, correlation_value, title = None):
    
    fig, axes = plt.subplot_mosaic(
        [["img0", "img1", "res", "res"],
        ["corr", "corr", "res", "res"],
        ["corr", "corr", "res", "res"]]
    )
    
    if title is not None:
        fig.suptitle(title)
    
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

def blur_array(array, kernel_size):
    return cv2.GaussianBlur(array, kernel_size, 0)

def compute_overlapping_difference(array1, array2, offset):
    h1, w1 = array1.shape
    h2, w2 = array2.shape
    
    y_offset, x_offset= offset

    y1_start = max(0, -y_offset)
    y1_end = min(h1, h2 - y_offset)
    x1_start = max(0, -x_offset)
    x1_end = min(w1, w2 - x_offset)
    
    y2_start = max(0, y_offset)
    y2_end = min(h2, h1 + y_offset)
    x2_start = max(0, x_offset)
    x2_end = min(w2, w1 + x_offset)
    overlap1 = array2[y1_start:y1_end, x1_start:x1_end]
    overlap2 = array1[y2_start:y2_end, x2_start:x2_end]
    if overlap1.size == 0 or overlap1.shape != overlap2.shape:
        return None, 0
    #overlap1 = overlap1.astype(np.int32)
    #overlap2 = overlap2.astype(np.int32)

    cps = compute_cps(np.fft.fft2(pad_to_square(overlap1)), np.fft.fft2(pad_to_square(overlap2)))
    correlation = np.fft.ifft2(np.fft.ifftshift(cps))
    correlation = np.fft.fftshift(correlation)
    correlation_magnitude = np.abs(correlation)
    correlation_magnitude = blur_array(correlation_magnitude, (3,3))
    center_correl = correlation_magnitude[correlation_magnitude.shape[0]//2, correlation_magnitude.shape[1]//2]
    return 1.0/(1.0 + center_correl), overlap1.size


def compute_shift_cps(data1 : ImageData, data2 : ImageData):
    cps = compute_cps(data1.fft, data2.fft)
    #display_cps(cps)
    
    (peak_coords, peak_val, correlation_magnitude) = find_peak_location(cps)
    shift = compute_shift(peak_coords, data1.fft.shape)

    candidates = []
    min_size_to_keep = min(data1.img.shape[0], data1.img.shape[1]) * 3 # at least 3 row/col of overlap
    # shift might be offset by a whole period as FFT phase correlation wraps around
    for x in range(-1, 2):
        for y in range(-1, 2):
            offset = (shift[0] + x*data1.fft.shape[1], shift[1] + y*data1.fft.shape[0])
            diff, size = compute_overlapping_difference(data1.img[:,:,0], data2.img[:,:,0], offset)
            if diff is None:
                continue
            if size > min_size_to_keep: # keep 
                candidates.append((offset, diff, size))
        
            # biggest size first, keep only top 5 (might be close if offset is size/2)
            candidates.sort(key=lambda x: x[2], reverse=True)
            candidates = candidates[:5]

    if debug_level >= 2:
        for i, c in enumerate(candidates):
            show_corr(data1, data2, correlation_magnitude, c[0], peak_val, f"Candidate {i+1}/{len(candidates)} offset{c[0]} diff {c[1]}")
    min_element = min(candidates, key=lambda x: abs(x[1]))
    shift = min_element[0]
    diff = min_element[1]

    debug_fine(lambda: show_corr(data1, data2, correlation_magnitude, shift, 0, f"Best shift: {shift=} {diff=}"))

    shift = np.array(shift, dtype=np.int_)
    return shift, peak_val, correlation_magnitude

def compute_correlation(data1 : ImageData, data2: ImageData):
    (shift, correlation, correlation_magnitude) = compute_shift_cps(data1, data2)
    return CorrelationData(data1.img_idx, data2.img_idx, correlation, shift, correlation_magnitude)

def find_matches(images, update_callback):
    datas = [create_image_data(idx, img, path) for (idx, (img, path)) in enumerate(images)]

    datas[0].parent_idx = -1
    datas[0].shift_from_parent = np.zeros(2, dtype=np.int_)
    
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

        debug(lambda: show_corr(datas[best_corr.parent_idx], datas[best_corr.child_idx], best_corr.correlation_magnitude, best_corr.shift, best_corr.correlation, "Accepted") )

        found = datas[best_corr.child_idx]
        found.parent_idx = best_corr.parent_idx
        found.shift_from_parent = best_corr.shift
        update_callback(f"Found match {found.path.stem} with parent {datas[best_corr.parent_idx].path.stem}: ({best_corr.shift[1]}, {-best_corr.shift[0]}) corr: {best_corr.correlation:.4f}.")
    return datas

def compute_global_shift(datas : list[ImageData], index : int):
    if datas[index].parent_idx == -1 or datas[index].shift_from_parent is None:
        datas[index].global_shift = np.zeros(2, dtype=np.int_)
        return
    parent_idx = datas[index].parent_idx
    compute_global_shift(datas, parent_idx)
    datas[index].global_shift = datas[index].shift_from_parent + datas[parent_idx].global_shift

def compute_global_shifts(datas : list[ImageData]):
    for i, _ in enumerate(datas):
        compute_global_shift(datas, i)

def compute_global_shifts_bounding_box(datas : list[ImageData]):
    min_x = min(i.global_shift[1] for i in datas)
    min_y = min(i.global_shift[0] for i in datas)
    max_x = max(i.global_shift[1] for i in datas)
    max_y = max(i.global_shift[0] for i in datas)
    return np.array((min_x, min_y), dtype=np.int_), np.array((max_x, max_y), dtype=np.int_)

def save_images(datas : list[ImageData], out_folder : str):
    compute_global_shifts(datas)
    minBox, maxBox = compute_global_shifts_bounding_box(datas)
    span = maxBox - minBox
    border = np.array((50, 50), dtype=np.int_)
    single_size = np.array([datas[0].img.shape[1], datas[0].img.shape[0]], dtype=np.int_)
    total_size = single_size + span + border
    pos_unmatched = (20,20)
    ref_pos = -minBox + border//2

    background = Image.new("RGBA", total_size.tolist())
    blended_all = background.copy()
    
    # reverse order to put first image on top of the blend
    for data in reversed(datas):
        if data.global_shift is None:
            pos = pos_unmatched
        else:
            pos = ref_pos + np.flip(data.global_shift)
        pilImg = Image.fromarray(data.img)
        single_img = background.copy()
        single_img.paste(pilImg, pos.tolist())
        single_img.save(os.path.join(out_folder, f"{data.path.stem}.png"))
        
        blended_all.paste(pilImg, pos.tolist())

    blended_all.save(os.path.join(out_folder, "stitch.png"))

def auto_align(in_folder, out_folder, threshold, update_callback):

    images = align.load_img_and_paths_cv2(in_folder)

    datas = find_matches(images, update_callback)

    placeds = [i for i in datas if i.shift_from_parent is not None]
    update_callback(f"Managed to stitch {len(placeds)}/{len(datas)} images")
    
    save_images(datas, out_folder)


