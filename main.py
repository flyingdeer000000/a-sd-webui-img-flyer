import os
import argparse
from scripts.service import image_process, video_process, util


def parse_arguments():
    parser = argparse.ArgumentParser(description='Image processing script')

    # parser.add_argument('--cmd', dest='cmd', required=True, help='command to perform')

    subparsers = parser.add_subparsers(dest='subcmd')

    # img
    img_parser = subparsers.add_parser('img', help='perform image processing')
    img_parser.add_argument('--src-dir', dest='src_dir', help='source directory')
    img_parser.add_argument('--des-dir',
                            dest='des_dir',
                            help='target directory (default: output)')
    img_parser.add_argument('--resize',
                            dest='resize',
                            default='512x512',
                            help='resize size (default: 512x512)')
    img_parser.add_argument('--resize-color',
                            dest='resize_color',
                            type=str, default='',
                            help='resize color')
    img_parser.add_argument('--rembg-model',
                            dest='rembg_model',
                            type=str, default='isnet-anime',
                            help='remove background model (default: isnet-anime)')
    img_parser.add_argument('--rembg-color',
                            dest='rembg_color',
                            type=str, default='',
                            help='padding color after remove background (default=transparent)')
    img_parser.add_argument('--depth',
                            dest='dir_depth',
                            type=int, default=0,
                            help='recursive depth (default: 0)')

    # to_wav
    wav_parser = subparsers.add_parser('2wav', aliases=['to_wav'], help='convert video to WAV')
    wav_parser.add_argument('--src-file', dest='src_file', help='source file')
    wav_parser.add_argument('--des-file', dest='des_file', help='target file')

    # split
    split_parser = subparsers.add_parser('split',
                                         help='split videos based on duration')
    split_parser.add_argument('--src-dir',
                              dest='src_dir',
                              help='source directory')
    split_parser.add_argument('--des-dir',
                              dest='des_dir',
                              type=str, default="",
                              help='target directory (default: output)')
    split_parser.add_argument('--divider',
                              dest='divider',
                              type=int, default=2,
                              help='divider (default: 2)')
    split_parser.add_argument('--file-ext',
                              dest='file_ext',
                              type=str, default='wav',
                              help='file extension (default: wav')

    # sum_duration
    sum_parser = subparsers.add_parser('sum_duration', help='sum directory media file duration')
    sum_parser.add_argument('--dir', required=True, dest='directory', help='directory path')

    return parser.parse_args()


def img_process(args):
    resize_width, resize_height = map(int, args.resize.split('x'))

    if args.rembg_model.lower() == 'resize':
        rembg_model = ''
    else:
        rembg_model = args.rembg_model

    args.resize_color = getattr(args, 'resize_color', '0,0,0,0')
    args.rembg_color = getattr(args, 'rembg_color', '0,0,0,0')
    args.dir_depth = getattr(args, 'dir_depth', 0)

    print("[directory] source: {}".format(args.src_dir))
    print("[directory] target: {}".format(args.des_dir))
    print("[resize] size: {} x {} | color: {}".format(resize_width, resize_height, args.resize_color))
    print("[remove background] model: {} | color: {}".format(rembg_model, args.rembg_color))
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
        r_color=args.resize_color,
        rembg_model=rembg_model,
        rembg_color=args.rembg_color,
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


def sum_duration(args):
    if args.directory is None:
        raise Exception("missing argument --dir")

    total_sec = video_process.duration_sum(args.directory)
    time = util.format_time(total_sec)
    print("Total Duration: {}".format(time))


def testing(a):

    a.subcmd = 'img'
    a.src_dir = 'D:/work/ai/models/psplive/dousha/school/512x768_white/1'
    a.des_dir = 'D:/work/ai/models/psplive/dousha/school/512x768_white/2'
    a.resize = '512x768'
    a.resize_color = '255,13,85,1'
    a.rembg_model = 'none'

    return a


if __name__ == '__main__':

    args = parse_arguments()

    args = testing(args)

    print("[cmd] {}".format(args.subcmd))

    if args.subcmd == 'img':
        img_process(args)
    elif args.subcmd == '2wav' or args.subcmd == 'to_wav':
        to_wav(args)
    elif args.subcmd == 'split':
        split(args)
    elif args.subcmd == 'sum_duration':  # Handle the sum subcommand
        sum_duration(args)

    print("[fin]")
