from .stream_process import stream_process_template
from tqdm import tqdm
from draw.speed_view_v2 import LoopSpeedV2
from typing import List
from parser import Record
import cv2 as cv
from util import get_video_file_start_timestamp
from parser import FitParser
from datetime import datetime


class fit_draw_process(stream_process_template):

    def __init__(self, input_video_path, output_video_path, temp_video_path,
        record_file_path, preview: bool = False,
        preview_window_name: str = '预览'):
        super().__init__(input_video_path, output_video_path, temp_video_path,
                       record_file_path)
        self._preview = preview
        self._preview_window_name = preview_window_name

    def _stream_process(self, records: List[Record]):
        # 逐帧处理
        frame_count = 0
        loopView = LoopSpeedV2(max_speed=60)

        records_map = {record.timestamp: record for record in records}
        video_start_timestamp = get_video_file_start_timestamp(
            self._input_video_path)
        with tqdm(total=self._total_frames, unit='frame') as pbar:
            while True:
                ret, frame = self._cap.read()
                if not ret:
                    break
                # 相机倒置拍摄，需要手动旋转180
                frame = cv.rotate(frame, cv.ROTATE_180)
                # 计算当前帧的时间戳（秒）
                current_time_in_video = frame_count / self._fps

                # 计算当前帧对应的实际时间戳
                current_timestamp = video_start_timestamp + current_time_in_video
                closest_record = records_map[int(current_timestamp - 275)]

                # 绘制速度信息
                frame_with_speed = loopView.draw(closest_record, frame)

                # 显示进度
                frame_count += 1
                pbar.update(1)

                if self._preview:
                    cv.imshow(self._preview_window_name, frame_with_speed)
                    wait_time = int(1000 / self._fps)
                    _ = cv.waitKey(wait_time)
                    continue

                try:
                    self._ffmpeg_process.stdin.write(frame_with_speed.tobytes())
                except BrokenPipeError:
                    print("❌ ffmpeg 管道断开")
                    break

    def _get_records(self, file_path):
        # 解析 FIT 文件
        fitParser = FitParser(file_path)
        records = fitParser.parser()

        if not records:
            print("No records found in FIT file")
            exit(1)

        fit_start_timestamp = records[0].timestamp
        fit_end_timestamp = records[-1].timestamp
        print(
            f"FIT 文件时间范围: {datetime.fromtimestamp(fit_start_timestamp)} ~ {datetime.fromtimestamp(fit_end_timestamp)}")
        print(f"总共 {len(records)} 条记录")
        return records
