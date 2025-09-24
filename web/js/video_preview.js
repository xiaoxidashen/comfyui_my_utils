import {app} from "../../../scripts/app.js";

app.registerExtension({
    name: "VideoSplitCombine.VideoPreview",

    async nodeCreated(node) {
        if (node.comfyClass === "VideoSplitCombine") {
            // 创建视频预览小部件
            const videoPreviewWidget = {
                name: "video_preview",
                type: "video_preview_widget",
                draw: function (ctx, node, widget_width, y, widget_height) {
                    // 这里可以自定义绘制，但我们用DOM元素，所以留空
                },
                computeSize: function(width) {
                    // 返回小部件的高度 [width, height]
                    return [width, 200]; // 固定高度200px
                }
            };

            // 创建容器div
            const container = document.createElement("div");
            container.style.cssText = `
                width: 100%;
                height: 200px;
                overflow-x: auto;
                overflow-y: hidden;
                display: flex;
                gap: 10px;
                align-items: center;
                background: #2a2a2a;
                border-radius: 4px;
                padding: 10px;
                box-sizing: border-box;
            `;

            const placeholder = document.createElement("div");
            placeholder.style.cssText = `
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #888;
                font-size: 14px;
                border: 2px dashed #444;
                border-radius: 4px;
            `;
            placeholder.textContent = "视频预览将显示在这里";
            container.appendChild(placeholder);

            // 添加DOM小部件
            node.addDOMWidget(videoPreviewWidget.name, videoPreviewWidget.type, container);

            // 覆盖节点的 onExecuted 方法来处理预览
            const onExecuted = node.onExecuted;
            node.onExecuted = function (message) {
                // 调用原始的 onExecuted 方法
                onExecuted?.apply(this, arguments);

                // 处理视频预览
                if (message?.gifs && Array.isArray(message.gifs)) {
                    // 清空容器
                    container.innerHTML = "";

                    // 为每个视频创建预览元素
                    message.gifs.forEach((gifInfo, index) => {
                        const videoContainer = document.createElement("div");
                        videoContainer.style.cssText = `
                            flex-shrink: 0;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            gap: 5px;
                        `;

                        // 创建视频/GIF元素
                        let mediaElement;

                        if (gifInfo.format === "image/gif" || gifInfo.filename.endsWith('.gif')) {
                            // 创建img元素显示GIF
                            mediaElement = document.createElement("img");
                            mediaElement.style.cssText = `
                                max-width: 180px;
                                max-height: 140px;
                                border-radius: 4px;
                                border: 1px solid #444;
                                object-fit: contain;
                                background: #1a1a1a;
                            `;
                        } else {
                            // 创建video元素显示MP4/WEBM
                            mediaElement = document.createElement("video");
                            mediaElement.controls = true;
                            mediaElement.loop = true;
                            mediaElement.muted = true;
                            mediaElement.style.cssText = `
                                max-width: 180px;
                                max-height: 140px;
                                border-radius: 4px;
                                border: 1px solid #444;
                                background: #1a1a1a;
                            `;
                        }

                        // 构建媒体文件的URL
                        mediaElement.src = `/view?filename=${encodeURIComponent(gifInfo.filename)}&type=${gifInfo.type}&subfolder=${encodeURIComponent(gifInfo.subfolder || "")}`;

                        // 创建标签
                        const label = document.createElement("div");
                        label.style.cssText = `
                            font-size: 10px;
                            color: #ccc;
                            text-align: center;
                            max-width: 180px;
                            overflow: hidden;
                            text-overflow: ellipsis;
                            white-space: nowrap;
                        `;
                        label.textContent = `Part ${index + 1}`;
                        label.title = gifInfo.filename;

                        videoContainer.appendChild(mediaElement);
                        videoContainer.appendChild(label);
                        container.appendChild(videoContainer);
                    });
                }
            };
        }
    },
});