
import os

import gradio as gr

import ui.common.console as uicon
from scripts import util
from scripts.service import image_process, video_process, net_process


@uicon.capture_wrap
def img_process_interface(
        src_dir, des_dir,
        resize,
        resize_fill_color, resize_fill_alpha,
        resize_remove_color, resize_remove_alpha, resize_remove_threshold,
        rembg_model,
        rembg_color, rembg_alpha,
        dir_depth
):
    # Convert string resize '512x512' into two integers
    resize_width, resize_height = map(int, resize.split('x'))
    # Check if directories exist, if not create
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)

    if resize_fill_alpha < 0:
        resize_fill_color = ''
    else:
        resize_fill_color = resize_fill_color + hex(resize_fill_alpha)[2:].zfill(2)

    if resize_remove_alpha < 0:
        resize_remove_color = ''
    elif resize_remove_alpha == 0:
        resize_remove_color = 'auto'
    else:
        resize_remove_color = resize_remove_color + hex(resize_remove_alpha)[2:].zfill(2)

    if rembg_alpha <= 0:
        rembg_color = ''
    else:
        rembg_color = rembg_color + hex(rembg_alpha)[2:].zfill(2)

    image_process.process(
        src_dir=src_dir,
        des_dir=des_dir,
        resize_width=resize_width,
        resize_height=resize_height,
        resize_fill_color=resize_fill_color,
        resize_remove_color=resize_remove_color,
        resize_remove_threshold=resize_remove_threshold,
        rembg_model=rembg_model,
        rembg_color=rembg_color,
        recursive_depth=dir_depth,
    )
    return f"Processed images are saved in {des_dir}"


@uicon.capture_wrap
def media_to_wav_interface(src_file, des_file):
    video_process.convert_mp4_to_wav(src_file, des_file)
    return f"Converted WAV file is saved as {des_file}"


@uicon.capture_wrap
def media_split_interface(src_dir, des_dir, divider, file_ext):
    video_process.duration_split(src_dir, des_dir, divider, file_ext)
    return f"Videos split successfully into {des_dir}"


@uicon.capture_wrap
def media_duration_sum_interface(directory):
    total_sec = video_process.duration_sum(directory)
    t = util.format_time(total_sec)
    return f"Total Duration: {t}"


@uicon.capture_wrap
def media_fetch_interface(
        src, des, t_start, t_end,
):
    output_path, ret = net_process.fetch_by_yt_dlp(
        src, des,
        t_start, t_end,
    )
    return ret, output_path


def tab_image_process():
    with gr.Row():
        src_dir = gr.Textbox(label="Source Directory")
    with gr.Row():
        des_dir = gr.Textbox(label="Destination Directory")
    with gr.Row():
        resize = gr.Textbox(value="512x512", label="Resize (e.g., 512x512)")
        resize_fill_color = gr.ColorPicker(label="Resize Fill Color", value='#000000')
        resize_fill_alpha = gr.Slider(label="Resize Fill Alpha", value=-1, minimum=-1, maximum=255)
    with gr.Row():
        resize_remove_color = gr.ColorPicker(label="Resize Remove Color", value='#000000')
        resize_remove_alpha = gr.Slider(label="Resize Remove Alpha", value=-1, minimum=-1, maximum=255)
        resize_remove_threshold = gr.Number(label="Resize Remove Threshold", value=100)
    with gr.Row():
        rembg_model = gr.Dropdown(
            label="Remove Background Model  "
                  "| 'none' for no removing  "
                  "| first time executing takes a while  ",
            value="isnet-anime",
            choices=[
                "none",
                "u2net",
                "u2netp",
                "u2net_human_seg",
                "u2net_cloth_seg",
                "silueta",
                "isnet-general-use",
                "isnet-anime",
                "sam"
            ]
        )
        rembg_color = gr.ColorPicker(label="Remove Background Color")
        rembg_alpha = gr.Slider(label="Remove Background Alpha", value=-1, minimum=-1, maximum=255)
    with gr.Row():
        dir_depth = gr.Number(label="Directory Depth", value=0)
        run_img = gr.Button("Run Image Processing")
    with gr.Row():
        result = gr.TextArea(label="Result")
    run_img.click(
        img_process_interface,
        inputs=[src_dir, des_dir,
                resize,
                resize_fill_color, resize_fill_alpha,
                resize_remove_color, resize_remove_alpha, resize_remove_threshold,
                rembg_model,
                rembg_color, rembg_alpha,
                dir_depth],
        outputs=[result]
    )


def tab_video_to_wav():
    src_file = gr.Textbox(label="Source Video File")
    des_file = gr.Textbox(label="Destination WAV File")
    run_wav = gr.Button("Convert to WAV")
    result = gr.TextArea(label="Result")
    run_wav.click(media_to_wav_interface, inputs=[src_file, des_file], outputs=[result])


def tab_media_split():
    split_src_dir = gr.Textbox(label="Source Directory")
    split_des_dir = gr.Textbox(label="Destination Directory")
    divider = gr.Number(label="Divider", value=2)
    file_ext = gr.Textbox(label="File Extension", value="wav")
    run_split = gr.Button("Split Video")
    result = gr.TextArea(label="Result")
    run_split.click(
        media_split_interface,
        inputs=[split_src_dir, split_des_dir, divider, file_ext],
        outputs=[result]
    )


def tab_media_sum_duration():
    sum_dir = gr.Textbox(label="Directory")
    run_sum = gr.Button("Sum Media Duration")
    result = gr.TextArea(label="Result")
    run_sum.click(media_duration_sum_interface, inputs=[sum_dir], outputs=[result])


def tab_media_fetch():
    with gr.Row():
        with gr.Column():
            text_src_path = gr.Textbox(label="Source Path", value="")
            text_des_path = gr.Textbox(label="Destination", value="")
            with gr.Group():
                with gr.Row():
                    num_src_start = gr.Number(value=0, label="Start (sec)")
                    num_src_end = gr.Number(value=0, label="End (sec)")
                    button_src_url = gr.Button("Fetch Source", variant="primary")
                with gr.Row():
                    text_result = gr.TextArea(label="Result")
        with gr.Column():
            audio_src = gr.Audio(
                label="Source",
                interactive=True,
                show_download_button=True,
            )

    button_src_url.click(
        fn=media_fetch_interface,
        inputs=[
            text_src_path, text_des_path,
            num_src_start, num_src_end,
        ],
        outputs=[
            text_result, audio_src,
        ]
    )


def webui():
    with gr.Blocks() as demo:
        with gr.Tab("Image"):
            tab_image_process()

        with gr.Tab("Extract Video Sound"):
            tab_video_to_wav()

        with gr.Tab("Media Fetch"):
            tab_media_fetch()

        with gr.Tab("Media Split"):
            tab_media_split()

        with gr.Tab("Media Duration"):
            tab_media_sum_duration()

        text_output = gr.Textbox(label="Console")

        def clear_output():
            uicon.capture_clear()
            text_output.value = '[clear]'

        clear_button = gr.Button("Clear Output")
        clear_button.click(clear_output)

    return demo


if __name__ == '__main__':
    app = webui()
    app.queue().launch(
        server_port=10005,
        show_error=True,
        debug=True
    )
