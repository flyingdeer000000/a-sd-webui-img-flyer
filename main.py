import os
import argparse
from scripts.service import image_process, video_process


def parse_arguments():
    parser = argparse.ArgumentParser(description='Image processing script')

    parser.add_argument('--cmd', dest='cmd', required=True, help='command to perform')

    subparsers = parser.add_subparsers(dest='subcmd')

    # img
    img_parser = subparsers.add_parser('img', help='perform image processing')
    img_parser.add_argument('--src-dir', dest='src_dir', help='source directory')
    img_parser.add_argument('--des-dir', dest='des_dir', help='target directory (default: output)')
    img_parser.add_argument('--resize', dest='resize', default='512x512', help='resize size (default: 512x512)')
    img_parser.add_argument('--resize-color', dest='resize_color', default='0,0,0,0', help='resize color')
    img_parser.add_argument('--rembg-model', dest='rembg_model', default='isnet-anime',
                            help='remove background model (default: isnet-anime)')
    img_parser.add_argument('--depth', dest='dir_depth', type=int, default=0, help='recursive depth (default: 0)')

    # to_wav
    wav_parser = subparsers.add_parser('2wav', aliases=['to_wav'], help='convert video to WAV')
    wav_parser.add_argument('--src-file', dest='src_file', help='source file')
    wav_parser.add_argument('--des-file', dest='des_file', help='target file')

    # split
    split_parser = subparsers.add_parser('split', help='split videos based on duration')
    split_parser.add_argument('--src-dir', dest='src_dir', help='source directory')
    split_parser.add_argument('--des-dir', dest='des_dir', help='target directory (default: output)')
    split_parser.add_argument('--divider', dest='divider', help='divider (default: 2)')
    split_parser.add_argument('--file-ext', dest='file_ext', help='file extension (default: wav')

    return parser.parse_args()


def img_process(args):
    resize_width, resize_height = map(int, args.resize.split('x'))
    resize_color = args.resize_color.strip()

    if args.rembg_model.lower() == 'resize':
        rembg_model = ''
    else:
        rembg_model = args.rembg_model

    print("[directory] source: {}".format(args.src_dir))
    print("[directory] target: {}".format(args.des_dir))
    print("[resize] size: {} x {}, color: {}".format(resize_width, resize_height, resize_color))
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
        r_color=resize_color,
        rembg_model=rembg_model,
        recursive_depth=args.dir_depth,
    )


def to_wav(args):
    if args.src_file is None:
        raise Exception("missing argument --src-file")

    if args.des_file is None:
        args.des_file = args.src_file.replace(".mp4", ".wav")

    print("[src_file] source: {}".format(args.src_file))
    print("[des_file] target: {}".format(args.des_file))
    video_process.convert_mp4_to_wav(args.src_file, args.des_file)


def split(args):
    if args.src_dir is None:
        raise Exception("missing argument --src-dir")

    if args.des_dir is None:
        args.des_dir = os.path.join(args.src_dir, 'output')

    args.divider = int(args.divider)
    args.file_ext = str(args.file_ext).lower()

    video_process.duration_split(args.src_dir, args.des_dir, args.divider, args.file_ext)


if __name__ == '__main__':
    args = parse_arguments()

    print("[cmd] {}".format(args.cmd))

    if args.cmd == 'img':
        img_process(args)
    elif args.cmd == '2wav' or args.cmd == 'to_wav':
        to_wav(args)
    elif args.cmd == 'split':
        split(args)

    print("[fin]")
