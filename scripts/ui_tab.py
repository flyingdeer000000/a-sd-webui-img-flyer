import traceback

import gradio as gr

import modules.scripts as scripts
from modules import script_callbacks
from modules.shared import opts

from scripts.service import image_process

FN_GO_RUNNING = False


class Script(scripts.Script):
    def __init__(self) -> None:
        super().__init__()

    def title(self):
        return "Flyer"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        return ()


def fn_go(
        dir_src,
        dir_des,
        num_depth,
        rembg_model,
        is_resize,
        resize_width,
        resize_height,
        resize_color,
):
    global FN_GO_RUNNING

    print("[img process] here {}".format(FN_GO_RUNNING))

    if FN_GO_RUNNING:
        print("[img process] running")
        return

    FN_GO_RUNNING = True
    try:
        if dir_src == "" or dir_des == "":
            print("[img process] miss params: input directory & output directory")
            return

        print("[img process] image directory {} -> {}".format(dir_src, dir_des))
        print("[img process] remove image background model {}".format(rembg_model))
        if is_resize:
            print("[img process] image resize {} x {}".format(resize_width, resize_height))
        else:
            print("[img process] image keep original size")

        resize_color = resize_color.strip()
        if resize_color == "" or resize_color is None:
            resize_color = "0,0,0,0"

        image_process.process(
            src_dir=str(dir_src),
            des_dir=str(dir_des),
            r_width=int(resize_width),
            r_height=int(resize_height),

            resize_exec=bool(is_resize),
            rembg_model=str(rembg_model),
            recursive_depth=int(num_depth),
        )
    except:
        traceback.print_exc()
    finally:
        FN_GO_RUNNING = False
        print("[img process] done")
    return []


def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as flyer_editor:
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    textbox_dir_src = gr.Textbox(
                        label='Input Directory',
                        placeholder='/path/input/images or /path/input/images/**/*'
                    )
                with gr.Row():
                    textbox_dir_des = gr.Textbox(
                        label='Output Directory',
                        placeholder='/path/output/images or /path/output/images/**/*'
                    )
                with gr.Row():
                    number_recursive_depth = gr.Number(
                        value=0,
                        label='Directory Recursive Depth'
                    )
                with gr.Row():
                    dropdown_rembg_model = gr.Dropdown(
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
                with gr.Row():
                    checkbox_resize = gr.Checkbox(
                        value=True,
                        label="Image Resize"
                    )
                    textbox_resize_color = gr.Textbox(
                        label='Resize Color (RGBA)',
                        value="0,0,0,0",
                        placeholder='0,0,0,0'
                    )
                    slider_w = gr.Slider(label="resize width", minimum=64, maximum=2048, value=512, step=64,
                                         interactive=True)
                    slider_h = gr.Slider(label="resize height", minimum=64, maximum=2048, value=512, step=64,
                                         interactive=True)
                with gr.Row():
                    button_go = gr.Button(value="GO!", variant="primary")

        button_go.click(fn_go, [
            textbox_dir_src,
            textbox_dir_des,
            number_recursive_depth,
            dropdown_rembg_model,
            checkbox_resize,
            slider_w,
            slider_h,
            textbox_resize_color,
        ], [])

    return [(flyer_editor, "Flyer", "flyer_editor")]


script_callbacks.on_ui_tabs(on_ui_tabs)
