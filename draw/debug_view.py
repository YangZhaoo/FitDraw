from parser import Record
from .base import ViewBase
import cv2 as cv


class DebugInfoDraw(ViewBase):

    def __init__(self):
        self._color = (0, 255, 0)
        self._font = cv.FONT_HERSHEY_SIMPLEX
        self._font_scale = 1
        self._thickness = 2
        self._line_row_multiply_factor = 1.8


    def draw(self, record: Record, image, **kargs):

        # 添加信息文本
        image_text = str.join('\n', [f"{key}: {value}" for key, value in kargs.items()]) if kargs is not None and len(kargs) > 0 else ""
        info_text = str(record) + image_text
        height_start_idx = int(image.shape[0] * 0.3)

        (w, h), _ = cv.getTextSize("0",
                       self._font,
                       self._font_scale,
                       self._thickness)

        for idx, text in enumerate(info_text.split('\n')):
            image_with_debug_info = cv.putText(image, text, (20, height_start_idx + int(idx * h * self._line_row_multiply_factor)),
                                               self._font, self._font_scale, self._color, self._thickness)
        return image_with_debug_info