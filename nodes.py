import torch

vhs_videocombine = None

try:
    import importlib
    nodes_module = importlib.import_module("custom_nodes.comfyui-videohelpersuite.videohelpersuite.nodes")
    utils_module = importlib.import_module("custom_nodes.comfyui-videohelpersuite.videohelpersuite.utils")
    get_video_formats = getattr(nodes_module, 'get_video_formats')
    imageOrLatent = getattr(utils_module, 'imageOrLatent')
    floatOrInt = getattr(utils_module, 'floatOrInt')
    ContainsAll = getattr(utils_module, 'ContainsAll')
except:
    def get_video_formats():
        return ["'video/h264-mp4'", "'video/webm'"], {}
    imageOrLatent = "IMAGE"
    floatOrInt = "FLOAT"
    def ContainsAll(x):
        return x

class VideoSplitCombine:
    @classmethod
    def INPUT_TYPES(s):
        ffmpeg_formats, format_widgets = get_video_formats()
        format_widgets["image/webp"] = [['lossless', "BOOLEAN", {'default': True}]]
        return {
            "required": {
                "images": (imageOrLatent,),
                "split_num": ("INT", {"default": 1, "min": 1, "max": 100, "step": 1}),
                "frame_rate": (
                    floatOrInt,
                    {"default": 8, "min": 1, "step": 1},
                ),
                "loop_count": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
                "filename_prefix": ("STRING", {"default": "SplitVideo"}),
                "format": (["image/gif", "image/webp"] + ffmpeg_formats, {'formats': format_widgets}),
                "pingpong": ("BOOLEAN", {"default": False}),
                "save_output": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "audio": ("AUDIO",),
                "meta_batch": ("VHS_BatchManager",),
                "vae": ("VAE",),
            },
            "hidden": ContainsAll({
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID"
            }),
        }

    RETURN_TYPES = ("VHS_FILENAMES",)
    RETURN_NAMES = ("Filenames",)
    OUTPUT_NODE = True
    CATEGORY = "MyUtils"
    FUNCTION = "split_and_combine"

    def split_and_combine(
        self,
        frame_rate: int,
        loop_count: int,
        images=None,
        latents=None,
        split_num=1,
        filename_prefix="SplitVideo",
        format="image/gif",
        pingpong=False,
        save_output=True,
        prompt=None,
        extra_pnginfo=None,
        audio=None,
        unique_id=None,
        manual_format_widgets=None,
        meta_batch=None,
        vae=None,
        **kwargs
    ):
        global vhs_videocombine
        if vhs_videocombine is None:
            from nodes import NODE_CLASS_MAPPINGS as NODE_CLASS_MAPPINGS_all
            vhs_videocombine = NODE_CLASS_MAPPINGS_all["VHS_VideoCombine"]()

        # 处理 images 和 latents 的逻辑，与 VideoCombine 保持一致
        if latents is not None:
            images = latents
        if images is None:
            return ((save_output, []),)

        if not isinstance(images, torch.Tensor):
            raise ValueError("输入必须是 torch.Tensor")

        batch_size = images.shape[0]
        if batch_size < split_num:
            raise ValueError(f"输入帧数 ({batch_size}) 不能小于分割数 ({split_num})")

        frames_per_split = batch_size // split_num
        remainder = batch_size % split_num

        all_filenames = []
        all_gifs = []

        start_idx = 0
        for i in range(split_num):
            # 计算当前分割的帧数（处理余数）
            current_frames = frames_per_split + (1 if i < remainder else 0)
            end_idx = start_idx + current_frames

            # 分割 tensor
            split_images = images[start_idx:end_idx]

            # 为每个分割的视频创建唯一的文件名前缀
            split_filename_prefix = f"{filename_prefix}_part{i+1:02d}"

            # 调用原始的 VHS_VideoCombine，传递所有参数
            result = vhs_videocombine.combine_video(
                frame_rate=frame_rate,
                loop_count=loop_count,
                images=split_images,
                latents=None,
                filename_prefix=split_filename_prefix,
                format=format,
                pingpong=pingpong,
                save_output=save_output,
                prompt=prompt,
                extra_pnginfo=extra_pnginfo,
                audio=audio,
                unique_id=unique_id,
                manual_format_widgets=manual_format_widgets,
                meta_batch=meta_batch,
                vae=vae,
                **kwargs
            )

            # 收集文件名和UI信息
            if result and "result" in result:
                result_tuple = result["result"]
                if result_tuple and len(result_tuple[0]) >= 2:
                    filenames = result_tuple[0][1]
                    all_filenames.extend(filenames)

                # 收集 UI 中的 gifs 预览信息
                if "ui" in result and "gifs" in result["ui"]:
                    gifs_info = result["ui"]["gifs"]
                    all_gifs.extend(gifs_info)

            start_idx = end_idx

        # 返回包含 result 和 ui 的字典格式
        return {
            "result": ((save_output, all_filenames),),
            "ui": {"gifs": all_gifs}
        }

# 注册节点
NODE_CLASS_MAPPINGS = {
    "VideoSplitCombine": VideoSplitCombine,
}
