from video_process import FitDrawProcess
import os
from draw import *

if __name__ == '__main__':

    resource_path = '/Users/yangzhao/Desktop/20251001/'
    input_video_dir = os.path.join(resource_path, 'video/')
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
    video_files = [os.path.join(input_video_dir, file) for file in os.listdir(input_video_dir)[1:2]]
    count = len(video_files)
    for i, video_file in enumerate(video_files):
        print(f"\n\n{i + 1}/{count}: [{video_file}]\n")
        args_param = {
            'work_steps': work_steps,
            'input_video_path': video_file,
            'record_file_path': fit_file,
            'preview': False,
            'draw_box': True
        }
        process = FitDrawProcess(**args_param)
        process.do_process()