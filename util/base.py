import os
import subprocess
import re
from datetime import datetime


def extract_audio_to_video(output_video_path, temp_video_path, input_video_path):
    """
        使用 ffmpeg 将原视频的音频和其他流复制到新视频中
        -i temp_video_path: 输入处理后的视频（无音频）
        -i input_video_path: 输入原始视频（有音频）
        -map 0:v:0: 使用第一个输入的视频流（处理后的视频）
        -map 1:a?: 使用第二个输入的所有音频流（原视频的音频）
        -c:v copy: 复制视频流，不重新编码
        -c:a copy: 复制音频流，不重新编码
        -shortest: 以最短的流为准
    :param output_video_path:
    :param temp_video_path:
    :param input_video_path:
    :return:
    """
    try:
        # 删除已存在的输出文件
        if os.path.exists(output_video_path):
            os.remove(output_video_path)

        ffmpeg_cmd = [
            'ffmpeg',
            '-i', temp_video_path,  # 处理后的视频（无音频）
            '-i', input_video_path,  # 原视频（有音频）
            '-map', '0:v:0',  # 使用第一个输入的视频流
            '-map', '1:a?',   # 使用第二个输入的音频流（如果存在）
            '-c:v', 'copy',   # 复制视频流
            '-c:a', 'copy',   # 复制音频流
            '-shortest',      # 以最短流为准
            '-y',             # 覆盖输出文件
            output_video_path
        ]

        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✓ 视频处理完成，输出文件: {output_video_path}")
            # 删除临时文件
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
                print("✓ 临时文件已清理")
        else:
            print(f"❌ FFmpeg 合并失败: {result.stderr}")
            print(f"临时视频文件保存在: {temp_video_path}")

    except FileNotFoundError:
        print("❌ 未找到 ffmpeg，请确保已安装 ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("   Ubuntu: sudo apt install ffmpeg")
        print(f"临时视频文件（无音频）保存在: {temp_video_path}")
    except Exception as e:
        print(f"❌ 合并音频时出错: {e}")
        print(f"临时视频文件保存在: {temp_video_path}")


def get_video_file_start_timestamp(video_filename):
    """
    从视频文件名中解析开始时间
    例如: DJI_20251001132807_0130_D.MP4 -> 2025-10-01 13:28:07
    """
    # 提取文件名中的时间戳部分 (格式: YYYYMMDDHHmmss)
    match = re.search(r'(\d{14})', video_filename)
    if match:
        time_str = match.group(1)
        # 解析为 datetime 对象
        dt = datetime.strptime(time_str, '%Y%m%d%H%M%S')
        # 返回时间戳（秒）
        return dt.timestamp()
    else:
        raise ValueError(f"无法从文件名中解析时间: {video_filename}")