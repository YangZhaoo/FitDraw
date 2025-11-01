import cv2 as cv
from draw.speed_view_v2 import LoopSpeedV2
from parser import FitParser
import os
import bisect
import subprocess
from datetime import datetime
import re
import time


def find_closest_record(records, target_timestamp):
    """根据时间戳找到最接近的记录"""
    # 使用二分查找找到最接近的记录
    timestamps = [r.timestamp for r in records]
    idx = bisect.bisect_left(timestamps, target_timestamp)
    
    if idx == 0:
        return records[0]
    if idx == len(records):
        return records[-1]
    
    # 比较前后两个记录，返回最接近的
    before = records[idx - 1]
    after = records[idx]
    
    if abs(before.timestamp - target_timestamp) < abs(after.timestamp - target_timestamp):
        return before
    else:
        return after


def convert_speed_to_kmh(speed_mps):
    """将速度从 m/s 转换为 km/h"""
    if speed_mps is None:
        return 0
    return round(speed_mps * 3.6, 1)


def parse_video_start_time(video_filename):
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



def image_show(image):
    cv.imshow('demo', image)
    if cv.waitKey(0) & 0xFF == ord('q'):
        return

def preview_video(input_video_path, records, fit_start_timestamp, time_offset=0):
    """
    预览模式：实时显示处理后的视频，无需等待导出
    
    参数:
        input_video_path: 输入视频路径
        records: FIT 记录列表
        fit_start_timestamp: FIT 文件起始时间戳
        time_offset: 时间偏移量（秒），用于调整视频和 FIT 数据的对齐
    
    键盘控制:
        空格: 暂停/继续
        q/ESC: 退出预览
        d 或 右箭头: 快进10秒
        a 或 左箭头: 后退10秒
        s: 快进1秒
        w: 后退1秒
        ] 或 +: 时间偏移 +10 秒
        [ 或 -: 时间偏移 -10 秒
    """
    print("\n=== 预览模式 ===")
    print("控制键:")
    print("  空格: 暂停/继续")
    print("  q/ESC: 退出预览")
    print("  d 或 右箭头: 快进10秒")
    print("  a 或 左箭头: 后退10秒")
    print("  s: 快进1秒")
    print("  w: 后退1秒")
    print("  ] 或 +: 时间偏移 +10 秒（调整数据对齐）")
    print("  [ 或 -: 时间偏移 -10 秒（调整数据对齐）\n")
    
    # 创建速度绘制器
    loopView = LoopSpeedV2(max_speed=60)
    
    # 从视频文件名解析视频开始时间
    video_filename = os.path.basename(input_video_path)
    video_start_timestamp = parse_video_start_time(video_filename)
    
    # 打开视频
    cap = cv.VideoCapture(input_video_path)
    fps = cap.get(cv.CAP_PROP_FPS)
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    
    # 创建窗口
    window_name = "预览 (按 q 退出)"
    cv.namedWindow(window_name, cv.WINDOW_NORMAL)
    
    paused = False
    frame_idx = 0

    records_map = {record.timestamp: record for record in records}
    
    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                print("视频播放完毕")
                break
            
            frame = cv.rotate(frame, cv.ROTATE_180)
            
            # 计算当前时间戳
            current_time_in_video = frame_idx / fps
            current_timestamp = video_start_timestamp + current_time_in_video
            
            # 查找对应的记录
            # record_index = int(current_timestamp - fit_start_timestamp + time_offset)
            # closest_record = records[record_index]
            closest_record = records_map[int(current_timestamp - 275)]

            # 绘制速度信息
            frame_with_speed = loopView.draw(closest_record, frame)
            
            # 添加信息文本
            info_text = f"Frame: {frame_idx}/{total_frames} | Speed: {closest_record.speed:.1f} km/h  | Time: {closest_record.date_time.astimezone()} | Offset: {time_offset}s"
            cv.putText(frame_with_speed, info_text, (10, 30),
                      cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 显示
            cv.imshow(window_name, frame_with_speed)
            frame_idx += 1
        else:
            # 暂停时只显示当前帧
            cv.imshow(window_name, frame_with_speed)
        
        # 控制键盘输入（等待时间与帧率匹配）
        wait_time = int(1000 / fps) if not paused else 100
        key = cv.waitKey(wait_time)
        
        # 处理按键
        if key == -1:  # 没有按键
            continue
        
        # 对于ASCII字符，使用 & 0xFF
        key_char = key & 0xFF
        
        if key_char == ord('q') or key_char == 27:  # q 或 ESC
            print("退出预览")
            break
        elif key_char == ord(' '):  # 空格
            paused = not paused
            print("暂停" if paused else "继续")
        elif key_char == ord('d') or key == 2555904 or key == 83 or key == 65363:  # d 或 右箭头
            # 快进10秒
            frame_idx = min(frame_idx + int(10 * fps), total_frames - 1)
            cap.set(cv.CAP_PROP_POS_FRAMES, frame_idx)
            print(f"快进到 {frame_idx / fps:.1f}s")
        elif key_char == ord('a') or key == 2424832 or key == 81 or key == 65361:  # a 或 左箭头
            # 后退10秒
            frame_idx = max(frame_idx - int(10 * fps), 0)
            cap.set(cv.CAP_PROP_POS_FRAMES, frame_idx)
            print(f"后退到 {frame_idx / fps:.1f}s")
        elif key_char == ord('s'):  # s 快进1秒
            frame_idx = min(frame_idx + int(fps), total_frames - 1)
            cap.set(cv.CAP_PROP_POS_FRAMES, frame_idx)
            print(f"快进到 {frame_idx / fps:.1f}s")
        elif key_char == ord('w'):  # w 后退1秒
            frame_idx = max(frame_idx - int(fps), 0)
            cap.set(cv.CAP_PROP_POS_FRAMES, frame_idx)
            print(f"后退到 {frame_idx / fps:.1f}s")
        elif key_char == ord(']'):  # ] 时间偏移 +1
            time_offset += 10
            print(f"时间偏移: {time_offset}s")
        elif key_char == ord('['):  # [ 时间偏移 -1
            time_offset -= 10
            print(f"时间偏移: {time_offset}s")
        elif key_char == ord('+') or key_char == ord('='):  # + 或 =
            time_offset += 10
            print(f"时间偏移: {time_offset}s")
        elif key_char == ord('-') or key_char == ord('_'):  # - 或 _
            time_offset -= 10
            print(f"时间偏移: {time_offset}s")
        else:
            # 调试：打印未处理的按键码
            if key_char != 255:  # 忽略无效键
                print(f"未识别的按键 - 完整键码: {key}, 字符码: {key_char}")
    
    cap.release()
    cv.destroyAllWindows()
    
    return time_offset


if __name__ == '__main__':
    # 解析 FIT 文件
    fitParser = FitParser('./resource/20251001.fit')
    records = fitParser.parser()
    
    if not records:
        print("No records found in FIT file")
        exit(1)
    
    fit_start_timestamp = records[0].timestamp
    fit_end_timestamp = records[-1].timestamp
    print(f"FIT 文件时间范围: {datetime.fromtimestamp(fit_start_timestamp)} ~ {datetime.fromtimestamp(fit_end_timestamp)}")
    print(f"总共 {len(records)} 条记录")

    file_name = 'DJI_20251001132807_0130_D'
    # 视频文件路径
    input_video_path = f'./resource/{file_name}.MP4'
    temp_video_path = f'./resource/{file_name}_speed_temp.mp4'
    output_video_path = f'./resource/{file_name}_speed.mp4'
    
    # 选择模式
    print("\n请选择模式:")
    print("1. 预览模式 (快速查看效果，可调整参数)")
    print("2. 导出模式 (生成最终视频文件)")
    
    mode = input("请输入 1 或 2 (默认为预览): ").strip()
    
    if mode == '2':
        # 导出模式
        time_offset_input = input("请输入时间偏移量(秒，默认 -372): ").strip()
        time_offset = int(time_offset_input) if time_offset_input else -372
    else:
        # 预览模式
        print("\n启动预览...")
        time_offset = preview_video(input_video_path, records, fit_start_timestamp, time_offset=-698)
        
        # 预览后询问是否导出
        export = input("\n预览完成，是否导出视频? (y/n): ").strip().lower()
        if export != 'y':
            print("取消导出")
            exit(0)
    
    print(f"\n使用时间偏移: {time_offset}s")

    # 创建速度绘制器
    loopView = LoopSpeedV2(max_speed=60)  # 最大速度 60 km/h
    
    # 从视频文件名解析视频开始时间
    video_filename = os.path.basename(input_video_path)
    video_start_timestamp = parse_video_start_time(video_filename)
    print(f"视频开始时间: {datetime.fromtimestamp(video_start_timestamp)}")
    
    # 检查输入视频是否存在
    if not os.path.exists(input_video_path):
        print(f"视频文件不存在: {input_video_path}")
        exit(1)
    
    # 打开视频文件
    cap = cv.VideoCapture(input_video_path)
    
    # 获取视频属性
    fps = cap.get(cv.CAP_PROP_FPS)
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    
    print(f"视频信息: {width}x{height}, {fps} FPS, 总帧数: {total_frames}")
    
    # 使用 ffmpeg 管道直接写入，避免生成巨大的临时文件
    # 删除已存在的临时文件
    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)
    
    # 构建 ffmpeg 命令：从 stdin 读取原始视频帧，使用高质量 H.264 编码
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',  # 覆盖输出文件
        '-f', 'rawvideo',  # 输入格式：原始视频
        '-vcodec', 'rawvideo',
        '-s', f'{width}x{height}',  # 视频尺寸
        '-pix_fmt', 'bgr24',  # OpenCV 使用 BGR24 格式
        '-r', str(fps),  # 帧率
        '-i', '-',  # 从标准输入读取
        '-an',  # 不处理音频
        '-vcodec', 'libx264',  # 使用 H.264 编码
        '-preset', 'ultrafast',  # 编码速度：faster 平衡速度和质量 取值：faster（41s）、veryfast（32s）、ultrafast（24s）
        '-crf', '23',  # 质量：23 是默认值，与原视频质量接近
        '-pix_fmt', 'yuv420p',  # 像素格式
        temp_video_path
    ]
    
    print("启动 ffmpeg 编码器...")
    try:
        ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=10**8
        )
    except FileNotFoundError:
        print("❌ 未找到 ffmpeg，将使用 OpenCV 编码器（文件会较大）")
        print("   建议安装 ffmpeg: brew install ffmpeg")
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        out = cv.VideoWriter(temp_video_path, fourcc, fps, (width, height))
        ffmpeg_process = None
    
    use_ffmpeg = ffmpeg_process is not None
    
    # 逐帧处理
    frame_count = 0
    start_time = time.time()
    last_print_time = start_time

    records_map = {record.timestamp: record for record in records}


    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv.rotate(frame, cv.ROTATE_180)
        # image_show(frame)
        # 计算当前帧的时间戳（秒）
        current_time_in_video = frame_count / fps
        
        # 计算当前帧对应的实际时间戳
        current_timestamp = video_start_timestamp + current_time_in_video
        
        # 找到最接近的记录（使用时间偏移）
        # record_index = int(current_timestamp + time_offset - fit_start_timestamp)
        # record_index = max(0, min(record_index, len(records) - 1))
        # closest_record = records[record_index]
        closest_record = records_map[int(current_timestamp - 275)]

        # 绘制速度信息
        frame_with_speed = loopView.draw(closest_record, frame)
        
        # 写入输出视频
        if use_ffmpeg:
            # 使用 ffmpeg 管道写入
            try:
                ffmpeg_process.stdin.write(frame_with_speed.tobytes())
            except BrokenPipeError:
                print("❌ ffmpeg 管道断开")
                break
        else:
            # 使用 OpenCV 写入
            out.write(frame_with_speed)
        
        # 显示进度
        frame_count += 1
        current_time = time.time()
        
        # 每秒或每100帧更新一次进度
        if frame_count % 100 == 0 or (current_time - last_print_time) >= 1.0:
            elapsed = current_time - start_time
            progress = (frame_count / total_frames) * 100
            fps_processing = frame_count / elapsed if elapsed > 0 else 0
            remaining_frames = total_frames - frame_count
            eta_seconds = remaining_frames / fps_processing if fps_processing > 0 else 0
            eta_minutes = int(eta_seconds / 60)
            eta_seconds_rem = int(eta_seconds % 60)
            
            print(f"处理进度: {progress:.1f}% ({frame_count}/{total_frames}) | "
                  f"速度: {fps_processing:.1f} fps | "
                  f"预计剩余: {eta_minutes}:{eta_seconds_rem:02d}")
            last_print_time = current_time
    
    # 释放资源
    cap.release()
    
    # 计算总耗时
    total_elapsed = time.time() - start_time
    total_minutes = int(total_elapsed / 60)
    total_seconds = int(total_elapsed % 60)
    
    if use_ffmpeg:
        # 关闭 ffmpeg 管道
        ffmpeg_process.stdin.close()
        ffmpeg_process.wait()
        
        # 检查 ffmpeg 是否成功
        if ffmpeg_process.returncode != 0:
            stderr_output = ffmpeg_process.stderr.read().decode('utf-8')
            print(f"❌ ffmpeg 编码失败: {stderr_output}")
            exit(1)
        
        print(f"✓ 已处理 {frame_count} 帧，耗时 {total_minutes}:{total_seconds:02d}")
    else:
        out.release()
        print(f"✓ 已处理 {frame_count} 帧（使用 OpenCV 编码器），耗时 {total_minutes}:{total_seconds:02d}")
    
    cv.destroyAllWindows()
    
    print("视频帧处理完成，正在合并音频...")
    
    # 使用 ffmpeg 将原视频的音频和其他流复制到新视频中
    # -i temp_video_path: 输入处理后的视频（无音频）
    # -i input_video_path: 输入原始视频（有音频）
    # -map 0:v:0: 使用第一个输入的视频流（处理后的视频）
    # -map 1:a?: 使用第二个输入的所有音频流（原视频的音频）
    # -c:v copy: 复制视频流，不重新编码
    # -c:a copy: 复制音频流，不重新编码
    # -shortest: 以最短的流为准
    
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