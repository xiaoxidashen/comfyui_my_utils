# ComfyUI 自定义节点简明指南

## 基本结构
- 在 `custom_nodes/<包名>/` 下创建 `nodes.py`，`__init__.py` 可留空。
- 导入必要模块：`torch`、`folder_paths`、`from nodes import PreviewImage`，按需补充 `numpy`、`PIL`。

```python
class MyNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",)}}

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = "My Utils"

    def execute(self, image):
        return {"ui": {}, "result": (image,)}
```

- 注册节点：
  ```python
  NODE_CLASS_MAPPINGS = {"MyNode": MyNode}
  NODE_DISPLAY_NAME_MAPPINGS = {"MyNode": "我的节点"}
  ```

## 添加图像预览
- 复用核心 `PreviewImage`：
  ```python
  preview = PreviewImage()
  preview_data = preview.save_images(image_tensor, filename_prefix="MyNodePreview")
  return {"ui": preview_data.get("ui", {}), "result": (image_tensor,)}
  ```
- 返回值中的 `ui.images` 会让前端显示缩略图。

## 视频/动画预览
- 将帧序列写成 WebP/GIF，并设置 `ui["animated"] = (True,)`：
  ```python
  pil_frames[0].save(path,
                     save_all=True,
                     append_images=pil_frames[1:],
                     duration=duration,
                     loop=0)
  ui = {
      "images": [{"filename": file, "subfolder": subfolder, "type": "temp"}],
      "animated": (len(pil_frames) > 1,),
      "text": [f"{len(pil_frames)}f {w}x{h} @{fps:.1f}fps"]
  }
  return {"ui": ui, "result": (images,)}
  ```
- 帧批次需大于 1 才会播放。

## 调试建议
- `python -m py_compile nodes.py` 检查语法。
- 重启 ComfyUI 载入新节点，在 UI 搜索注册名测试。
