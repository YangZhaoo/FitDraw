from video_process import fit_draw_process
import os

if __name__ == '__main__':

    # 获取当前脚本的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建resource目录的绝对路径
    resource_path = os.path.join(current_dir, 'resource')

    file_name = 'DJI_20251001132807_0130_D'
    # 视频文件路径
    input_video_path = os.path.join(resource_path, f'{file_name}.MP4')
    temp_video_path = os.path.join(resource_path, f'{file_name}_speed_temp.MP4')
    output_video_path = os.path.join(resource_path, f'{file_name}_speed.MP4')
    fit_file_path = os.path.join(resource_path, f'20251001.fit')

    process = fit_draw_process(input_video_path, output_video_path, temp_video_path, fit_file_path, preview=False)
    process.do_process()