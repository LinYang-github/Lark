import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

import config
from core.subtitle_parser import SubtitleParser
from core.tts_provider import get_tts_provider
from core.audio_processor import AudioProcessor
from core.video_mixer import VideoMixer


class LarkDubbingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lark 离线视频配音引擎")
        self.root.geometry("500x350")
        self.root.resizable(False, False)
        
        # 定义存储变量
        self.video_path_var = tk.StringVar()
        self.srt_path_var = tk.StringVar()
        self.tts_mode_var = tk.StringVar(value=config.TTS_MODE)
        self.gender_var = tk.StringVar(value="male") 
        self.style_var = tk.StringVar(value="broadcaster") 
        
        self.create_widgets()

    def create_widgets(self):
        pad_options = {'padx': 10, 'pady': 5}
        
        # 1. 视频选择区
        frame_video = tk.Frame(self.root)
        frame_video.pack(fill=tk.X, **pad_options)
        tk.Label(frame_video, text="原视频文件:").pack(side=tk.LEFT)
        tk.Entry(frame_video, textvariable=self.video_path_var, width=35).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_video, text="浏览...", command=self.select_video).pack(side=tk.LEFT)

        # 2. 字幕选择区
        frame_srt = tk.Frame(self.root)
        frame_srt.pack(fill=tk.X, **pad_options)
        tk.Label(frame_srt, text="配套字幕(.srt):").pack(side=tk.LEFT)
        tk.Entry(frame_srt, textvariable=self.srt_path_var, width=35).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_srt, text="浏览...", command=self.select_srt).pack(side=tk.LEFT)

        # 3. 参数配置区
        frame_config = tk.Frame(self.root)
        frame_config.pack(fill=tk.X, **pad_options)
        
        tk.Label(frame_config, text="性别:").pack(side=tk.LEFT)
        gender_cb = ttk.Combobox(frame_config, textvariable=self.gender_var, values=config.GENDERS, state="readonly", width=8)
        gender_cb.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_config, text="风格:").pack(side=tk.LEFT, padx=(15, 0))
        style_cb = ttk.Combobox(frame_config, textvariable=self.style_var, values=config.STYLES, state="readonly", width=12)
        style_cb.pack(side=tk.LEFT, padx=5)

        # 4. 引擎选择区
        frame_engine = tk.Frame(self.root)
        frame_engine.pack(fill=tk.X, **pad_options)
        tk.Label(frame_engine, text="TTS 引擎:").pack(side=tk.LEFT)
        engine_cb = ttk.Combobox(frame_engine, textvariable=self.tts_mode_var, values=["native", "cosyvoice"], state="readonly", width=12)
        engine_cb.pack(side=tk.LEFT, padx=5)
        tk.Label(frame_engine, text="(AI 服务需本地启动 CosyVoice)", fg="gray", font=("", 10)).pack(side=tk.LEFT)


        # 4. 进度条与状态显示
        frame_progress = tk.Frame(self.root)
        frame_progress.pack(fill=tk.X, pady=20, padx=10)
        self.progress_bar = ttk.Progressbar(frame_progress, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        self.status_label = tk.Label(frame_progress, text="准备就绪", fg="gray")
        self.status_label.pack(anchor=tk.W, pady=5)

        # 5. 底部操作按钮
        frame_actions = tk.Frame(self.root)
        frame_actions.pack(pady=10)
        self.btn_run = tk.Button(frame_actions, text="🚀 启动自动混流渲染", bg="#4CAF50", fg="white", width=20, height=2, command=self.start_processing)
        self.btn_run.pack()

    def select_video(self):
        filepath = filedialog.askopenfilename(title="选择原视频", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
        if filepath:
            self.video_path_var.set(filepath)

    def select_srt(self):
        filepath = filedialog.askopenfilename(title="选择字幕文件", filetypes=[("SRT files", "*.srt"), ("All files", "*.*")])
        if filepath:
            self.srt_path_var.set(filepath)

    def update_status(self, message, progress=None):
        """安全地在主线程更新 UI 状态"""
        self.status_label.config(text=message)
        if progress is not None:
            self.progress_bar['value'] = progress
        self.root.update_idletasks()

    def progress_callback(self, current, total):
        """传递给 AudioProcessor 的回调，换算成 0 - 100 进度"""
        if total > 0:
            percentage = int((current / total) * 100)
            # 使用 after 保证 UI 线程安全更新
            self.root.after(0, self.update_status, f"音频时间轴对齐处理中... ({current}/{total} 句)", percentage)

    def start_processing(self):
        video_path = self.video_path_var.get()
        srt_path = self.srt_path_var.get()
        gender = self.gender_var.get()
        style = self.style_var.get()

        if not video_path or not os.path.exists(video_path):
            messagebox.showerror("错误", "请选择有效的视频文件！")
            return
        if not srt_path or not os.path.exists(srt_path):
            messagebox.showerror("错误", "请选择有效的字幕文件！")
            return

        # 禁用按钮防止重复点击
        self.btn_run.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        
        # 挂载后台工作线程
        mode = self.tts_mode_var.get()
        threading.Thread(target=self._worker_thread, args=(video_path, srt_path, gender, style, mode), daemon=True).start()

    def _worker_thread(self, video_path, srt_path, gender, style, mode):
        try:
            # Step 1
            self.root.after(0, self.update_status, "1. 正在解析物理时间轴...")
            parser = SubtitleParser(srt_path)
            subtitles = parser.parse()
            if not subtitles:
                raise ValueError("未提取到任何有效字幕！请检查文件格式。")

            # Step 2
            self.root.after(0, self.update_status, f"2. 正在初始化发音引擎({mode}/{gender}/{style})...")
            tts = get_tts_provider(mode, gender, style)
            
            if os.path.exists(config.TEMP_DIR):
                shutil.rmtree(config.TEMP_DIR)
            os.makedirs(config.TEMP_DIR, exist_ok=True)

            # Step 3 (耗时最长，接入回调)
            audio_processor = AudioProcessor(tts)
            merged_wav = audio_processor.process_subtitles(
                subtitles, 
                temp_dir=config.TEMP_DIR, 
                max_speed=config.MAX_SPEED_UP_RATIO,
                progress_callback=self.progress_callback
            )

            # Step 4
            self.root.after(0, self.update_status, "4. 正在执行底层音视频重混流装载...")
            video_mixer = VideoMixer()
            
            # 使用源文件名构造输出名
            base_dir = os.path.dirname(video_path)
            original_name = os.path.basename(video_path)
            name_part, ext_part = os.path.splitext(original_name)
            output_path = os.path.join(base_dir, f"{name_part}_dubbed_{gender}_{style}.mp4")
            
            video_mixer.mix(video_path, merged_wav, output_path)

            self.root.after(0, self.update_status, "🎉 全部任务完成！", 100)
            self.root.after(0, lambda: messagebox.showinfo("成功", f"混合视频导出成功！\n文件保存在:\n{output_path}"))

        except Exception as e:
            self.root.after(0, self.update_status, f"❌ 任务失败: {str(e)}", 0)
            self.root.after(0, lambda: messagebox.showerror("发生错误", str(e)))
            
        finally:
            self.root.after(0, self.update_status, "正在清理临时缓存区...")
            if os.path.exists(config.TEMP_DIR):
                shutil.rmtree(config.TEMP_DIR)
            # 恢复按钮
            self.root.after(0, lambda: self.btn_run.config(state=tk.NORMAL))
            self.root.after(0, self.update_status, "准备就绪")


if __name__ == "__main__":
    root = tk.Tk()
    app = LarkDubbingApp(root)
    root.mainloop()
