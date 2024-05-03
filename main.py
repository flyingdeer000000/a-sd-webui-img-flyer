import io
import os
import sys

from scripts.service import image_process, video_process, util
import gradio as gr


def capture_console_output(func):
    def wrapper(*args, **kwargs):
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = io.StringIO()  # Redirect stdout
        sys.stderr = io.StringIO()  # Redirect stderr
        try:
            result = func(*args, **kwargs)
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            return result + "\n" + output + error
        finally:
            sys.stdout = original_stdout  # Reset stdout to original
            sys.stderr = original_stderr  # Reset stderr to original

    return wrapper


@capture_console_output
def img_process_interface(src_dir, des_dir, resize, resize_fill_color, resize_remove_color, rembg_model, rembg_color,
                          dir_depth):
    # Convert string resize '512x512' into two integers
    resize_width, resize_height = map(int, resize.split('x'))
    # Check if directories exist, if not create
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)

    image_process.process(
        src_dir=src_dir,
        des_dir=des_dir,
        resize_width=resize_width,
        resize_height=resize_height,
        resize_fill_color=resize_fill_color,
        resize_remove_color=resize_remove_color,
        rembg_model=rembg_model,
        rembg_color=rembg_color,
        recursive_depth=dir_depth,
    )
    return f"Processed images are saved in {des_dir}"


@capture_console_output
def to_wav_interface(src_file, des_file):
    video_process.convert_mp4_to_wav(src_file, des_file)
    return f"Converted WAV file is saved as {des_file}"


@capture_console_output
def split_interface(src_dir, des_dir, divider, file_ext):
    video_process.duration_split(src_dir, des_dir, divider, file_ext)
    return f"Videos split successfully into {des_dir}"


@capture_console_output
def sum_duration_interface(directory):
    total_sec = video_process.duration_sum(directory)
    time = util.format_time(total_sec)
    return f"Total Duration: {time}"


def webui(port):
    with gr.Blocks() as demo:
        with gr.Tab("Image Processing"):
            with gr.Row():
                src_dir = gr.Textbox(label="Source Directory")
            with gr.Row():
                des_dir = gr.Textbox(label="Destination Directory")
            with gr.Row():
                resize = gr.Textbox(value="512x512", label="Resize (e.g., 512x512)")
                resize_fill_color = gr.Textbox(label="Resize Fill Color")
                resize_remove_color = gr.Textbox(label="Resize Remove Color")
                rembg_model = gr.Textbox(label="Remove Background Model")
                rembg_color = gr.Textbox(label="Remove Background Color")
                dir_depth = gr.Number(label="Directory Depth", value=0)
            with gr.Row():
                run_img = gr.Button("Run Image Processing")

            img_output = gr.Textbox(label="Output")
            run_img.click(img_process_interface,
                          inputs=[src_dir, des_dir, resize, resize_fill_color, resize_remove_color, rembg_model,
                                  rembg_color, dir_depth], outputs=img_output)

        with gr.Tab("Video to WAV"):
            src_file = gr.Textbox(label="Source Video File")
            des_file = gr.Textbox(label="Destination WAV File")
            run_wav = gr.Button("Convert to WAV")
            wav_output = gr.Textbox(label="Output")
            run_wav.click(to_wav_interface, inputs=[src_file, des_file], outputs=wav_output)

        with gr.Tab("Split Video"):
            split_src_dir = gr.Textbox(label="Source Directory")
            split_des_dir = gr.Textbox(label="Destination Directory")
            divider = gr.Number(label="Divider", value=2)
            file_ext = gr.Textbox(label="File Extension", value="wav")
            run_split = gr.Button("Split Video")
            split_output = gr.Textbox(label="Output")
            run_split.click(split_interface, inputs=[split_src_dir, split_des_dir, divider, file_ext],
                            outputs=split_output)

        with gr.Tab("Sum Duration"):
            sum_dir = gr.Textbox(label="Directory")
            run_sum = gr.Button("Calculate Duration")
            sum_output = gr.Textbox(label="Output")
            run_sum.click(sum_duration_interface, inputs=[sum_dir], outputs=sum_output)

    demo.launch(
        server_port=port,
        debug=True
    )


if __name__ == '__main__':
    webui(10005)
