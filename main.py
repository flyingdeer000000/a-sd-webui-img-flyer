
import os
import sys

from scripts.service import service_img


def help_print():
    print("<remove image background & resize image & squaring image>")
    print("")
    print("usage: ")
    print("   arg 1 = source directory")
    print("   arg 2 = (optional) target directory, default = output ")
    print("   arg 3 = (optional) resize size, default = 512x512")
    print("   arg 4 = (optional) remove background model, default = isnet-anime")
    print("         none = resize only, no-square = keep ratio")
    print("         none,no-square = resize only & keep ratio")
    print("   arg 5 = (optional) recursive depth, default = 0")
    print("")
    print("example:")
    print("   python main.py D:/input D:/output")
    print("   python main.py D:/input D:/output 512x512")
    print("   python main.py D:/input D:/output 512x768 isnet-anime 3")
    print("")
    print("example (resize only):")
    print("   python main.py D:/input D:/output 512x768 resize")
    print("")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    if len(sys.argv) < 2:
        help_print()
        exit(0)

    resize_width = 512
    resize_height = 512
    rembg_model = "isnet-anime"
    src_dir = '?'
    des_dir = '?'
    dir_depth = 0

    if len(sys.argv) >= 2:
        src_dir = sys.argv[1]

    if len(sys.argv) >= 3:
        des_dir = sys.argv[2]
    else:
        des_dir = os.path.join(src_dir, 'output')

    if len(sys.argv) >= 4:
        dimensions = sys.argv[3].split("x")
        resize_width = int(dimensions[0])
        if len(dimensions) == 1:
            resize_height = resize_width
        else:
            resize_height = int(dimensions[1])

    if len(sys.argv) >= 5:
        rembg_model = sys.argv[4]
        if rembg_model == "def" or rembg_model == "default":
            rembg_model = ""

    if len(sys.argv) >= 6:
        dir_depth = int(sys.argv[5])

    print("[directory] source : {}".format(src_dir))
    print("[directory] target : {}".format(des_dir))
    print("[resize] parameter size: {} x {}".format(resize_width, resize_height))
    print("[remove background] model: {}".format(rembg_model))
    print("[recursive] depth: {}".format(dir_depth))

    if not os.path.exists(src_dir):
        print("[directory] not found: {}".format(src_dir))
        exit(404)

    service_img.process(
        src_dir=src_dir,
        des_dir=des_dir,
        r_width=resize_width,
        r_height=resize_height,
        rembg_model=rembg_model,
        recursive_depth=dir_depth,
    )

    print("[success]")
