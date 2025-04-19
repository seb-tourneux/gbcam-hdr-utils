from PIL import Image, ImageSequence
import os
import re

def default_options():
    return {
        "frame_duration": 100,
        "freeze_duration": 3000,
        "fade_duration": 1000,
        "bg_color": [255, 255, 255]
    }

def find_clean_image(folder):
    for file in os.listdir(folder):
        if "_clean." in file:
            return os.path.join(folder, file)
    return None

def overlay_gif_on_png_animated(gif_path, png_path, output_path):
    png = Image.open(png_path).convert("RGBA")
    width, height = png.size

    def find_top_left_non_transparent_pixel(image):
        pixels = image.load()
        for y in range(height):
            for x in range(width):
                _, _, _, alpha = pixels[x, y]
                if alpha > 0:
                    return x, y
        return None

    top_left = find_top_left_non_transparent_pixel(png)
    if not top_left:
        raise ValueError("No non-transparent pixels found in the PNG.")

    gif = Image.open(gif_path)
    frames = []
    duration = gif.info.get("duration", 100)  # Get frame duration

    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert("RGBA")  # Ensure transparency is maintained
        new_frame = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        new_frame.paste(frame, top_left, frame)  # Overlay GIF frame

        frames.append(new_frame)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        transparency=0
    )


def overlay_all(image, frames, frame_duration, gif_path, png_path, bg_color):
    png = Image.open(png_path).convert("RGBA")
    width, height = png.size

    def find_top_left_non_transparent_pixel(image):
        pixels = image.load()
        for y in range(height):
            for x in range(width):
                _, _, _, alpha = pixels[x, y]
                if alpha > 0:
                    return x, y
        return None

    top_left = find_top_left_non_transparent_pixel(png)
    if not top_left:
        raise ValueError("No non-transparent pixels found in the PNG.")

    gif = Image.open(gif_path)
    duration = gif.info.get("duration", 100)

    if not image:
        bg_color = tuple(bg_color)
        image = Image.new("RGB", (width, height), bg_color)

    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert("RGBA")
        frame.info['duration'] = frame_duration

        image.paste(frame, top_left, frame)

        final_frame = image.convert("RGB")
        final_frame.info['duration'] = frame_duration
        frames.append(final_frame)

    return image


def find_gif_png_pairs(in_folder_png, in_folder_gif):
    pattern = re.compile(r"set_\d{4}_")

    files_png = os.listdir(in_folder_png)
    files_gif = os.listdir(in_folder_gif)

    gifs = {f: pattern.search(f) for f in files_gif if f.lower().endswith(".gif")}
    pngs = {f: pattern.search(f) for f in files_png if f.lower().endswith(".png")}

    pairs = {}
    for png, png_match in pngs.items():
        if png_match:
            key = png_match.group()
            for gif, gif_match in gifs.items():
                    if gif and gif_match.group() == key:
                        pairs[png] = gif # important : png as key (as they're ordered by Photoshop export, when exporting layer by layer)

    return pairs


def make_gif(gif_base, png_base, in_folder_gif, in_folder_png, out_folder):
    output_path = os.path.join(out_folder, os.path.basename(gif_base))
    gif_file = os.path.join(in_folder_gif, gif_base)
    png_file = os.path.join(in_folder_png, png_base)
    overlay_gif_on_png_animated(gif_file, png_file, output_path)
    

def make_gifs(in_folder_png, in_folder_gif, out_folder, update_callback):
    pairs = find_gif_png_pairs(in_folder_png, in_folder_gif)
    update_callback("Found {} GIF/PNG pairs".format(len(pairs)))

    for png, gif in pairs.items():
        make_gif(gif, png, in_folder_gif, in_folder_png, out_folder)
        update_callback("Pair {}<->{}".format(os.path.basename(gif), os.path.basename(png)))

def compose_gifs(image, frames, frame_duration, gif_base, png_base, bg_color, in_folder_gif, in_folder_png):
    gif_file = os.path.join(in_folder_gif, gif_base)
    png_file = os.path.join(in_folder_png, png_base)
    return overlay_all(image, frames, frame_duration, gif_file, png_file, bg_color)
    
def make_gif_all(in_folder_png, in_folder_gif, out_folder, options, update_callback):
    frame_duration = options['frame_duration']
    freeze_duration = options['freeze_duration']
    fade_duration = options['fade_duration']
    bg_color = options['bg_color']

    pairs = find_gif_png_pairs(in_folder_png, in_folder_gif)
    update_callback("Found {} GIF/PNG pairs".format(len(pairs)))

    image = None
    frames = []

    for png, gif in reversed(pairs.items()):
        image = compose_gifs(image, frames, frame_duration, gif, png, bg_color, in_folder_gif, in_folder_png)
        update_callback("Pair {}<->{}".format(os.path.basename(gif), os.path.basename(png)))

    if len(frames) == 0:
        update_callback("No frames found")
        return

    last_frame = frames[-1]

    clean_path = options["clean_path"] if "clean_path" in options else None
    if clean_path and fade_duration > 0:
        fade_frames = int(fade_duration / frame_duration)
        clean_img = Image.open(clean_path).convert("RGB")

        for i in range(1, fade_frames + 1):
            alpha = i / fade_frames
            blended = Image.blend(last_frame, clean_img, alpha)
            frames.append(blended)

    if freeze_duration > 0:
        last_frame = frames[-1]
        freeze_frames = int(freeze_duration / frame_duration)
        frames.extend([last_frame] * freeze_frames)
    
    update_callback(f"Saving gif of {len(frames)} frames...")

    out_path = os.path.join(out_folder, f"making_of_{frame_duration}ms.gif")
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration,
        loop=0
        )
    update_callback(f"Saved \"{out_path}\"")
