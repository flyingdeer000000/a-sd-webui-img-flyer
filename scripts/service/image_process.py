import time
from pathlib import Path

from PIL import Image
import rembg
import os

from scripts.service import util


def color_to_transparent(image, target_str: str):
    # Split the image into individual color channels

    if target_str == 'auto' or target_str == 'def':
        target = color_4_corners(image)
    else:
        target = util.color_string_to_tuple(target_str)

    red, green, blue, alpha = image.split()

    # Create a mask of the color to make transparent
    mask = red.point(lambda x: 0 if x == target[0] else 255)
    mask = mask.point(lambda x: 0 if x == green.getpixel((0, 0)) else 255)
    mask = mask.point(lambda x: 0 if x == blue.getpixel((0, 0)) else 255)

    # Apply the mask to the alpha channel
    alpha = alpha.point(lambda x: x if x != 0 else 0)
    alpha.paste(0, mask)

    # Combine the color channels with the modified alpha channel
    image = Image.merge('RGBA', (red, green, blue, alpha))

    return image


def color_get_most_used(image):
    # Get the colors and their counts
    colors = image.getcolors(image.size[0] * image.size[1])

    # Sort the colors by count in descending order
    sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)

    # Return the most used color
    most_used_color = sorted_colors[0][1]
    return most_used_color


def color_4_corners(image):
    # Get the color values of the four corners
    width, height = image.size
    top_left_color = image.getpixel((0, 0))
    top_right_color = image.getpixel((width - 1, 0))
    bottom_left_color = image.getpixel((0, height - 1))
    bottom_right_color = image.getpixel((width - 1, height - 1))

    # Determine the most frequent color among the corners
    colors = [top_left_color, top_right_color, bottom_left_color, bottom_right_color]
    background_color = max(set(colors), key=colors.count)

    return background_color


def background_remove(
        rem_src_dir: str,
        rem_des_dir: str,
        bg_color_str: str,
        session
):
    if session is None:
        return

    print("[rembg] {} ---> {}".format(rem_src_dir, rem_des_dir))

    os.makedirs(rem_des_dir, mode=777, exist_ok=True)

    files = Path(rem_src_dir).glob('*.[pP][nN][gG]')

    rgba_color = util.color_string_to_tuple(bg_color_str)

    index = 0
    total = util.file_count(rem_src_dir)
    for file in files:
        input_path = str(file)
        output_path = str(rem_des_dir + os.path.sep + (file.stem + file.suffix))

        with open(input_path, 'rb') as i:
            with open(output_path, 'wb') as o:
                data_in = i.read()
                data_out = rembg.remove(data_in, session=session)
                o.write(data_out)
                index = index + 1
                print("[rembg] [{}/{}] {}".format(index, total, output_path))

                # Fill with RGBA color
                background_fill(output_path, rgba_color)

    if total > 0:
        print("")


def background_fill(image_path, bg_color):
    image = Image.open(image_path)
    width, height = image.size
    background = Image.new('RGBA', (width, height), bg_color)
    background.paste(image, (0, 0), mask=image.convert('RGBA'))
    background.save(image_path)


def resize_image(
        input_path, output_path,
        to_width=512, to_height=512,
        fill_color="0,0,0,0",
        remove_color="",
):
    image = Image.open(input_path)
    image = image.convert('RGBA')

    if util.str_exist(remove_color):
        image = color_to_transparent(image, remove_color)

    ratio = image.width / image.height
    to_ratio = to_width / to_height

    color_tuple = util.color_string_to_tuple(fill_color)

    if ratio > to_ratio:
        new_width = to_width
        new_height = round(new_width / ratio)
    else:
        new_height = to_height
        new_width = round(new_height * ratio)

    # Resize the image while maintaining the aspect ratio
    resized_image = image.resize((new_width, new_height))

    # Create a new image with the desired dimensions and transparent background
    padded_image = Image.new("RGBA", (to_width, to_height), color_tuple)

    # fill color
    """
    if color_tuple[3] > 0:
        draw = ImageDraw.Draw(padded_image)
        draw.rectangle([(0, 0), (to_width, to_height)], fill=color_tuple)
    """

    # Calculate the padding offsets
    x_offset = (to_width - new_width) // 2
    y_offset = (to_height - new_height)

    # Paste the resized image onto the padded image with transparent pixels
    padded_image.paste(resized_image, (x_offset, y_offset))

    # Save the padded image with transparent pixels
    padded_image.save(output_path)


def resize_directory(
        resize_src_dir,
        resize_des_dir,
        width=512,
        height=512,
        fill_color="0,0,0,0",
        remove_color="",
):
    print("[resize] {} ---> {} ".format(resize_src_dir, resize_des_dir))

    if width <= 0:
        width = 512

    os.makedirs(resize_des_dir, mode=777, exist_ok=True)

    index = 0
    total = util.file_count(resize_src_dir)
    for filename in os.listdir(resize_src_dir):
        if filename.lower().endswith('.png'):
            image_path = os.path.join(resize_src_dir, filename)
            output_path = os.path.join(resize_des_dir, filename)
            resize_image(image_path, output_path, width, height, fill_color, remove_color)
            index = index + 1
            print("[resize] [{}/{}] {} ".format(index, total, output_path))

    if total > 0:
        print("")


def process(
        src_dir,
        des_dir,
        resize_width=512, resize_height=512,
        resize_fill_color="",
        resize_remove_color="",
        resize_exec=True,
        rembg_model="",
        rembg_color="",
        recursive_depth=None,
):
    start_time = time.time()

    try:
        src_dir = str(src_dir)
        des_dir = str(des_dir)
        resize_width = int(resize_width)
        resize_height = int(resize_height)
        resize_fill_color = str(resize_fill_color).strip()
        resize_exec = bool(resize_exec)
        rembg_model = str(rembg_model)
        recursive_depth = int(recursive_depth)

        if resize_width <= 0:
            resize_width = 512
        if resize_height <= 0:
            resize_height = 512

        os.makedirs(des_dir, mode=0o777, exist_ok=True)

        sep_count = src_dir.count(os.path.sep)

        if rembg_model == "def" or rembg_model == "default":
            rembg_model = "isnet-anime"

        if rembg_model == "" or rembg_model == "none" or rembg_model == "null":
            rembg_session = None
        else:
            rembg_session = rembg.new_session(model_name=rembg_model)

        for root, dirs, files in os.walk(src_dir):
            # Calculate the current depth
            depth = root.count(os.path.sep) - sep_count

            # Skip if max_depth is specified and the current depth exceeds it
            if recursive_depth is not None and depth > recursive_depth:
                print("[process] max recursive depth reached {} > {}".format(depth, recursive_depth))
                continue

            dir_name = os.path.basename(root)
            if depth <= 0:
                des_path = des_dir
            else:
                des_path = str(os.path.join(des_dir, dir_name))

            print("[process] root: {}, depth: {}, max depth: {}".format(root, depth, recursive_depth))
            print("[process] name: {}, to: {}".format(dir_name, des_path))

            if rembg_session is None:
                if resize_exec:
                    resize_directory(
                        root, des_path,
                        resize_width, resize_height,
                        resize_fill_color, resize_remove_color
                    )
            else:
                background_remove(root, des_path, rembg_color, rembg_session)
                if resize_exec:
                    resize_directory(
                        des_path, des_path,
                        resize_width, resize_height,
                        resize_fill_color, resize_remove_color
                    )
    finally:
        elapsed_time = time.time() - start_time
        print(f"[process] elapsed time: {elapsed_time} seconds")
