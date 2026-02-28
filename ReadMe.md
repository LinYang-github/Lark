# Lark 视频字幕自动配音工具

Lark 是一个专为**完全离线（内网）环境**设计的轻量级自动化视频配音与混轨工具。它通过读取本地的 `.mp4` 视频和配套的 `.srt` 字幕文件，调用本地 TTS 引擎自动生成对应语音，精准进行时间轴动态对齐压缩，最终合成融合音轨的新视频发布。

## 🌟 核心特性

- **🚀 绝对离线**：不需要任何外部网络请求，完美适应高度机密的内网和政企隔离环境。
- **🧩 模块化插拔 TTS**：内置了基于操作系统底层接口的脱机离线发音引擎（如 Windows: `sapi5`, Mac: `say` 的 Fallback），同时预留了 HTTP 抽象接口便于未来直连自建的本地语音大模型。
- **⏱️ 智能弹性对齐引擎**：能通过对字幕帧的物理运算绝对对齐时间周期。当生成语音比字幕展示时间长时，平滑调用 FFmpeg `atempo` 算法自适应轻微变速“挤压”进入时间轨；足够多出上限阈值部分可被精准斩断。短位音频则自动计算静默片进行填充（Pad）。
- **🎵 高级合流胶囊**：生成的配乐通过 `ffmpeg-python` 原生指令注入源视频，自动执行降扰合轨（默认将源带环境声的音量压降至 20% 作为微量背景声）。

## 📦 项目架构与文件功能说明

```text
Lark/
├── config.py                   # 全局策略中心 (容错倍速阈值、音轨混合比率)
├── main.py                     # 全自动化胶囊调度统一入口
├── requirements.txt            # 脱机部署环境声明 (兼容 Win/Mac)
└── core/
    ├── subtitle_parser.py      # 字幕提取渲染器 (绝对毫秒级别转换)
    ├── tts_provider.py         # 跨平台 TTS 服务驱动生成器
    ├── audio_processor.py      # 时间轴计算组装并执行变速垫黑引擎
    └── video_mixer.py          # 音轨最终并线投射器
```

## 🛠️ 安装指引 (离线环境准备)

工具链底层极度依赖著名的 [FFmpeg](https://ffmpeg.org/download.html)。请确保您的运行计算机上**配置了 FFmpeg 的系统环境变量**。

### Python 包离线封转

如果您要在物理隔离的 Windows 机器上安装：
1. **(有网机器)** 用外网终端执行下载所需 whl 包：
   ```bash
   mkdir offline_pkg
   pip download -r requirements.txt -d ./offline_pkg
   ```
2. **(无网机器)** 将文件夹通过介质拷贝进内网机后安装：
   ```bash
   pip install --no-index --find-links=./offline_pkg -r requirements.txt
   ```

*注意：Mac 的 Python 3.13 之后版本已不再预装 `audioop` 标准内联库，该程序内置了向后全向兼容补丁 (`audioop-lts`) 以保障 Mac 端的畅通运转。*

## 🚀 极速起跑

1. 准备您的输入素材并置于根目录（例如 `demo.mp4`, `demo.srt`）。
2. 在终端运行入口脚本：

```bash
# 最简执行（使用默认的基础本地 TTS 引擎）
python main.py -v demo.mp4 -s demo.srt -o final_output.mp4

# 高阶执行：如果您已经利用 ChatTTS 或 CosyVoice 在本地跑起了 http 的服务大模型：
python main.py -v demo.mp4 -s demo.srt -o final_output.mp4 --tts http
```

### 运行时控制流打印输出

在执行这行命令时，系统会自动清理先前的历史记录并显示每个周期的控制台渲染阶段：

*   `1. 正在解析字幕: demo.srt`
*   `2. 初始化 TTS 引擎...`
*   `3. 音频合成与时间轴对齐处理 (耗时操作)...` -> 这里会执行数百次碎块化创建与对齐计算。
*   `4. 视频音频混流封装...`
*   `🎉 任务全部完成！最终配音视频已保存至: final_output.mp4`

最后，程序将进行生命周期的安全清理，回收所有配音中途产生的零碎文件以节省内网储存空间。
