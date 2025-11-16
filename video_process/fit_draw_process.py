from .stream_process import StreamProcessTemplate
from tqdm import tqdm
from draw import ViewBase
from typing import List
from parser import Record
import cv2 as cv
from util import get_video_file_start_timestamp
from parser import FitParser
from datetime import datetime
import time


class FitDrawProcess(StreamProcessTemplate):

    def __init__(self, work_steps: List[ViewBase], input_video_path, record_file_path, preview: bool = False, draw_box: bool = False, time_offset: int = 275,
                 preview_window_name: str = '预览'):
        super().__init__(input_video_path, record_file_path)
        self._preview = preview
        self._draw_box = draw_box
        self._preview_window_name = preview_window_name
        self._time_offset = time_offset
        self._work_flow = self._construct_work_flow(work_steps)

    def _construct_work_flow(self, step: List[ViewBase]) -> ViewBase:
        for i in range(len(step) - 1):
            step[i].next_view = step[i + 1]
        return step[0]

    def _stream_process(self, records: List[Record]):
        # 逐帧处理
        frame_count = 0

        records_map = {record.timestamp: record for record in records}
        video_start_timestamp = get_video_file_start_timestamp(
            self._input_video_path)
        global_info = {
            'records': records
            # 'geo_info': GeoInfo(province='北京市', city='',district='朝阳',township='八里庄',street='四环东路')
        }
        default_record = Record(**{
            'timestamp': int(time.time()),
            'date_time': datetime.now(),
            'speed': None,
            'location': None,
            'distance': None
        })

        with tqdm(total=self._total_frames, unit='frame') as pbar:
            while True:
                ret, frame = self._cap.read()
                if not ret:
                    break
                # 相机倒置拍摄，需要手动旋转180
                # frame = cv.rotate(frame, cv.ROTATE_180)
                # 计算当前帧的时间戳（秒）
                current_time_in_video = frame_count / self._fps

                # 计算当前帧对应的实际时间戳
                current_timestamp = video_start_timestamp + current_time_in_video
                record_key = int(current_timestamp - self._time_offset)
                current_record = records_map.get(record_key, None)
                if current_record is not None:
                    extract_speed = current_record.speed + ((records_map[record_key + 1].speed - current_record.speed) * (
                        (frame_count % int(self._fps)) / int(self._fps))) if (record_key + 1) in records_map else 0
                    current_record.speed = round(extract_speed, 2)
                else:
                    default_record.timestamp = record_key
                    default_record.date_time = datetime.fromtimestamp(record_key)
                    current_record = default_record
                # 绘制速度信息
                # frame_with_speed = loopView.draw(current_record, frame)
                attribute = {
                    'frame': {
                        '\nvideo info': '',
                        'frame': f'{frame_count}/{self._total_frames}',
                        'fps': round(self._fps, 2),
                        'current timestamp': round(current_timestamp, 2),
                        'current frame time offset': round(current_time_in_video, 2),
                        'camera & recorder time diff': self._time_offset
                    },
                    'record_info': {
                        'recent_record': [
                            records_map.get(record_key - 1, None),
                            records_map.get(record_key, None),
                            records_map.get(record_key + 1, None),
                        ]
                    },
                    'global_info': global_info
                }

                final_frame = self._work_flow.do_draw(current_record, frame, self._draw_box, **attribute)

                # 显示进度
                frame_count += 1
                pbar.update(1)

                if self._preview:
                    cv.imshow(self._preview_window_name, final_frame)
                    wait_time = int(1000 / self._fps)
                    _ = cv.waitKey(wait_time)
                    continue

                try:
                    self._ffmpeg_process.stdin.write(final_frame.tobytes())
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
