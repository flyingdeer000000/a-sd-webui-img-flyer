import os
import argparse


import scripts.service.video_process

from scripts.service import image_process, video_process


def parse_arguments():
    parser = argparse.ArgumentParser(description='Image processing script')

    parser.add_argument('--cmd', dest='cmd', required=True, help='command to perform')

    parser.add_argument('--src-file', dest='src_file', help='Source file')
    parser.add_argument('--des-file', dest='des_file', help='Target file')

    parser.add_argument('--src-dir', dest='src_dir', help='Source directory')
    parser.add_argument('--des-dir', dest='des_dir', help='Target directory (default: output)')
    parser.add_argument('--resize', dest='resize', default='512x512', help='Resize size (default: 512x512)')
    parser.add_argument('--rembg-model', dest='rembg_model', default='isnet-anime',
                        help='Remove background model (default: isnet-anime)')
    parser.add_argument('--depth', dest='dir_depth', type=int, default=0,
                        help='Recursive depth (default: 0)')

    args = parser.parse_args()
    return args


def img_process():
    resize_width, resize_height = map(int, args.resize.split('x'))
    if args.rembg_model.lower() == 'resize':
        rembg_model = ''
    else:
        rembg_model = args.rembg_model
    print("[directory] source : {}".format(args.src_dir))
    print("[directory] target : {}".format(args.des_dir))
    print("[resize] parameter size: {} x {}".format(resize_width, resize_height))
    print("[remove background] model: {}".format(rembg_model))
    print("[recursive] depth: {}".format(args.dir_depth))
    if not os.path.exists(args.src_dir):
        print("[directory] not found: {}".format(args.src_dir))
        exit(404)
    if args.des_dir is None:
        des_dir = os.path.join(args.src_dir, 'output')
    else:
        des_dir = args.des_dir
    image_process.process(
        src_dir=args.src_dir,
        des_dir=des_dir,
        r_width=resize_width,
        r_height=resize_height,
        rembg_model=rembg_model,
        recursive_depth=args.dir_depth,
    )


def to_wav():

    if args.src_file is None:
        raise Exception("missing argument --src-file")

    if args.des_file is None:
        args.des_file = args.src_file.replace(".mp4", ".wav")

    print("[src_file] source : {}".format(args.src_file))
    print("[des_file] target : {}".format(args.des_file))
    video_process.convert_mp4_to_wav(args.src_file, args.des_file)


if __name__ == '__main__':
    args = parse_arguments()

    args.cmd = "2wav"
    args.src_file = "D:/work/ai/set/psplive/dousha/audio/20240214_words.mp4"

    cmd = args.cmd.lower()

    print("[cmd] " + cmd)

    if cmd == 'img':
        img_process()

    if cmd == '2wav' or cmd == 'to_wav':
        to_wav()

    print("[fin]")