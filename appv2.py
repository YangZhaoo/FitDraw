from video_process import FitDrawProcess
import os
from draw import *

if __name__ == '__main__':

    resource_path = '/Users/yangzhao/Desktop/20251001/'
    input_video_dir = os.path.join(resource_path, 'video/')
    output_video_dir = os.path.join(resource_path, 'video_speed/')
    fit_file = os.path.join(resource_path, f'20251001.fit')
    work_steps = [
        # FrameBlend(skip=True),
        GlobalMap(),
        DirectView(),
        TextView(),
        LoopSpeedV2(60),
        DebugInfoDraw(False),
        None
    ]
    all_process_video = set([file for file in os.listdir(input_video_dir) if file.endswith(".MP4")])
    complete_process_video = set([file.replace('_speed', '') for file in os.listdir(output_video_dir) if file.endswith(".MP4")])
    need_process_video = all_process_video - complete_process_video

    video_files = [file for file in need_process_video if file.find('20251001123150') > 0]
    count = len(video_files)
    for i, video_file in enumerate(video_files):
        print(f"\n\n{i + 1}/{count}: [{video_file}]\n")
        args_param = {
            'work_steps': work_steps,
            'input_video_path': os.path.join(input_video_dir, video_file),
            'output_video_path': output_video_dir,
            'record_file_path': fit_file,
            'preview': True,
            'draw_box': False
        }
        process = FitDrawProcess(**args_param)
        process.do_process()