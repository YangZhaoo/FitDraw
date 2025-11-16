from abc import ABC, abstractmethod
import cv2 as cv
from util import extract_audio_to_video
import subprocess
from parser import Record
from typing import List
import os
from pathlib import Path


class StreamProcessTemplate(ABC):

    def __init__(self, input_video_path, record_file_path, output_video_path, preview: bool = False):
        self._input_video_path = input_video_path
        parent_path = Path(input_video_path).parent
        file_name, file_format = Path(input_video_path).name.split('.')
        self._record_file_path = record_file_path
        if output_video_path is not None:
            self._output_video_path = os.path.join(Path(output_video_path, f"{file_name}_speed.{file_format}"))
            self._temp_video_path = os.path.join(Path(self._output_video_path).parent, f"{file_name}_speed_temp.{file_format}")
        else:
            self._output_video_path = os.path.join(parent_path, f"{file_name}_speed.{file_format}")
            self._temp_video_path = os.path.join(parent_path, f"{file_name}_speed_temp.{file_format}")
        if os.path.exists(self._temp_video_path):
            os.remove(self._temp_video_path)
        self._preview = preview

    def do_process(self):

        # 打开视频文件
        self._cap = cv.VideoCapture(self._input_video_path)

        # 获取视频属性
        self._fps = self._cap.get(cv.CAP_PROP_FPS)
        width = int(self._cap.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(self._cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        self._total_frames = int(self._cap.get(cv.CAP_PROP_FRAME_COUNT))

        print(f"视频信息: {width}x{height}, {self._fps} FPS, 总帧数: {self._total_frames}")

        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # 覆盖输出文件
            '-f', 'rawvideo',  # 输入格式：原始视频
            '-vcodec', 'rawvideo',
            '-s', f'{width}x{height}',  # 视频尺寸
            '-pix_fmt', 'bgr24',  # OpenCV 使用 BGR24 格式
            '-r', str(self._fps),  # 帧率
            '-i', '-',  # 从标准输入读取
            '-an',  # 不处理音频
            '-vcodec', 'libx264',  # 使用 H.264 编码
            '-preset', 'ultrafast',
            # 编码速度：faster 平衡速度和质量 取值：faster（41s）、veryfast（32s）、ultrafast（24s）
            '-crf', '23',  # 质量：23 是默认值，与原视频质量接近
            '-pix_fmt', 'yuv420p',  # 像素格式
            self._temp_video_path
        ]

        if not self._preview:
            print("启动 ffmpeg 编码器...")
            try:
                self._ffmpeg_process = subprocess.Popen(
                    ffmpeg_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=10 ** 8
                )
            except FileNotFoundError:
                print("❌ 未找到 ffmpeg，将使用 OpenCV 编码器（文件会较大）")
                print("   建议安装 ffmpeg: brew install ffmpeg")
                fourcc = cv.VideoWriter_fourcc(*'mp4v')
                self._ffmpeg_process = None

        records = self._get_records(self._record_file_path)
        self._stream_process(records)

        # 释放资源
        self._cap.release()
        if not self._preview:
            # 关闭 ffmpeg 管道
            self._ffmpeg_process.stdin.close()
            self._ffmpeg_process.wait()

            # 检查 ffmpeg 是否成功
            if self._ffmpeg_process.returncode != 0:
                stderr_output = self._ffmpeg_process.stderr.read().decode('utf-8')
                print(f"❌ ffmpeg 编码失败: {stderr_output}")
                exit(1)

        cv.destroyAllWindows()
        print("视频帧处理完成，正在合并音频...")

        if not self._preview:
            extract_audio_to_video(self._output_video_path, self._temp_video_path,
                                   self._input_video_path)

    @abstractmethod
    def _stream_process(self, records: List[Record]):
        pass

    @abstractmethod
    def _get_records(self, file_path) -> List[Record]:
        pass
