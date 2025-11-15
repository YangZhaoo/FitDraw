from .base import ViewBase
from parser import Record
import cv2 as cv


class DebugInfoDraw(ViewBase):

    def __init__(self, enable_frame_info=False, next_view=None):
        super().__init__(next_view)
        self._color = (0, 255, 0)
        self._font = cv.FONT_HERSHEY_SIMPLEX
        self._font_scale = 1
        self._thickness = 2
        self._line_row_multiply_factor = 1.8
        self._aux_line_thickness = 1
        self._enable_frame_info = enable_frame_info

    def _draw(self, record: Record, image, **kargs):
        if self._enable_frame_info:
            # 添加信息文本，方便对齐image和record
            image_text = str.join('\n', [f"{key}: {value}" for key, value in kargs['debug_info'].items()]) if kargs is not None and 'debug_info' in kargs else ""
            info_text = str(record) + image_text
            height_start_idx = int(image.shape[0] * 0.3)

            (w, h), _ = cv.getTextSize("0",
                                       self._font,
                                       self._font_scale,
                                       self._thickness)

            for idx, text in enumerate(info_text.split('\n')):
                image = cv.putText(image, text,
                                                   (20, height_start_idx + int(idx * h * self._line_row_multiply_factor)),
                                                   self._font, self._font_scale, self._color, self._thickness)
        return image


    def _draw_box(self, image):
        w, h = image.shape[:2]
        # 绘制图片引导线：中线（绿色）、对角线（红色）
        cv.line(image, [int(h / 2), 0], [int(h / 2), w], (0, 255, 0), thickness=self._aux_line_thickness)
        cv.line(image, [0, int(w / 2)], [h, int(w / 2)], (0, 255, 0), thickness=self._aux_line_thickness)

        cv.line(image, [0, 0], [h, w], (0, 0, 255), thickness=self._aux_line_thickness)
        cv.line(image, [0, w], [h, 0], (0, 0, 255), thickness=self._aux_line_thickness)