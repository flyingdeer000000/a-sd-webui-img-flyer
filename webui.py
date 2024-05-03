import io
import os
import sys
import traceback
import threading

from scripts.service import image_process, video_process, util
import gradio as gr

stdout_stream = io.StringIO()
stderr_stream = io.StringIO()


class DualStream:
    def __init__(self, stream1, stream2):
        self.stream1 = stream1
        self.stream2 = stream2

    def write(self, text):
        self.stream1.write(text)
        self.stream2.write(text)

    def flush(self):
        self.stream1.flush()
        self.stream2.flush()


def capture_output():
    # Create the dual stream object
    dual_stream = DualStream(sys.stdout, stdout_stream)

    # Redirect stdout and stderr to the dual stream
    sys.stdout = dual_stream
    sys.stderr = dual_stream


def get_output():
    # Get the captured stdout and stderr
    stdout_value = stdout_stream.getvalue()
    stderr_value = stderr_stream.getvalue()

    return stdout_value, stderr_value


def capture_console_output(func):
    def wrapper(*args, **kwargs):
        try:
            # Create a thread to capture the stdout and stderr
            output_thread = threading.Thread(target=capture_output)
            output_thread.start()

            result = func(*args, **kwargs)  # Execute the decorated function

            # Wait for the thread to finish capturing output
            output_thread.join()

            stdout_value, stderr_value = get_output()

            return f"{result}\n{stdout_value}{stderr_value}"
        except Exception as e:
            traceback_str = traceback.format_exc()
            return f"Error occurred:\n{traceback_str}"

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


def tab_image_process():
    with gr.Row():
        src_dir = gr.Textbox(label="Source Directory")
    with gr.Row():
        des_dir = gr.Textbox(label="Destination Directory")
    with gr.Row():
        resize = gr.Textbox(value="512x512", label="Resize (e.g., 512x512)")
        resize_fill_color = gr.Textbox(label="Resize Fill Color")
        resize_remove_color = gr.Textbox(label="Resize Remove Color")
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
        rembg_color = gr.Textbox(label="Remove Background Color")
    with gr.Row():
        dir_depth = gr.Number(label="Directory Depth", value=0)
        run_img = gr.Button("Run Image Processing")

    img_output = gr.Textbox(label="Output")
    run_img.click(
        img_process_interface,
        inputs=[src_dir, des_dir, resize, resize_fill_color, resize_remove_color, rembg_model, rembg_color,
                dir_depth],
        outputs=img_output,
    )

    return img_output


def tab_video_to_wav():
    src_file = gr.Textbox(label="Source Video File")
    des_file = gr.Textbox(label="Destination WAV File")
    run_wav = gr.Button("Convert to WAV")
    wav_output = gr.Textbox(label="Output")
    run_wav.click(to_wav_interface, inputs=[src_file, des_file], outputs=wav_output)

    return wav_output


def tab_media_split():
    split_src_dir = gr.Textbox(label="Source Directory")
    split_des_dir = gr.Textbox(label="Destination Directory")
    divider = gr.Number(label="Divider", value=2)
    file_ext = gr.Textbox(label="File Extension", value="wav")
    run_split = gr.Button("Split Video")
    split_output = gr.Textbox(label="Output")
    run_split.click(split_interface, inputs=[split_src_dir, split_des_dir, divider, file_ext],
                    outputs=split_output)

    return split_output


def tab_media_sum_duration():
    sum_dir = gr.Textbox(label="Directory")
    run_sum = gr.Button("Sum Media Duration")
    sum_output = gr.Textbox(label="Output")
    run_sum.click(sum_duration_interface, inputs=[sum_dir], outputs=sum_output)

    return sum_output


def webui(port):
    with gr.Blocks() as demo:
        with gr.Tab("Image"):
            img_output = tab_image_process()

        with gr.Tab("Extract Video Sound"):
            wav_output = tab_video_to_wav()

        with gr.Tab("Media Split"):
            split_output = tab_media_split()

        with gr.Tab("Media Duration"):
            sum_output = tab_media_sum_duration()

        def clear_output():
            stdout_stream.truncate(0)
            stderr_stream.truncate(0)
            img_output.value = ''
            wav_output.value = ''
            split_output.value = ''
            sum_output.value = ''

        clear_button = gr.Button("Clear Output")
        clear_button.click(clear_output)

    def update_output():

        while True:
            stdout_value, stderr_value = get_output()

            img_output.value = stdout_value + stderr_value
            wav_output.value = stdout_value + stderr_value
            split_output.value = stdout_value + stderr_value
            sum_output.value = stdout_value + stderr_value

    output_thread = threading.Thread(target=update_output)
    output_thread.start()

    demo.launch(
        server_port=port,
        debug=True
    )


if __name__ == '__main__':
    webui(10005)
