from parser import Record
from .base import ViewBase
import cv2 as cv


class DebugInfoDraw(ViewBase):

    def __init__(self, next_view=None):
        super().__init__(next_view)
        self._color = (0, 255, 0)
        self._font = cv.FONT_HERSHEY_SIMPLEX
        self._font_scale = 1
        self._thickness = 2
        self._line_row_multiply_factor = 1.8

    def _draw(self, record: Record, image, **kargs):
        # 添加信息文本
        image_text = str.join('\n', [f"{key}: {value}" for key, value in kargs['debug_info'].items()]) if kargs is not None and 'debug_info' in kargs else ""
        info_text = str(record) + image_text
        height_start_idx = int(image.shape[0] * 0.3)

        (w, h), _ = cv.getTextSize("0",
                                   self._font,
                                   self._font_scale,
                                   self._thickness)

        for idx, text in enumerate(info_text.split('\n')):
            image_with_debug_info = cv.putText(image, text,
                                               (20, height_start_idx + int(idx * h * self._line_row_multiply_factor)),
                                               self._font, self._font_scale, self._color, self._thickness)
        return image_with_debug_info


class TextView(ViewBase):
    def __init__(self, next_view=None):
        super().__init__(next_view)

        # 时间配置
        self._font = cv.FONT_HERSHEY_SIMPLEX
        self._time_font_scale = 1.5
        self._time_font_thickness = 3
        self._time_font_color = (255, 255, 255)
        self._time_position_rate = 0.01
        self._x = None
        self._y = None

        # 坐标配置
        self._location_rate = 0.01
        self._location_font_scale = 1.5
        self._location_font_thickness = 2
        self._location_font_color = (255, 255, 255)
        self._location_x = None
        self._location_y = None

        self._prepared = False

    def _prepare_data(self, image, location: str):
        h, w = image.shape[:2]

        (time_char_width, time_char_height), _ = cv.getTextSize('0', self._font, self._time_font_scale,
                                                                self._time_font_thickness)
        time_position_offset = min(h, w) * self._time_position_rate
        self._time_x, self._time_y = int(time_position_offset), int(time_position_offset + time_char_height)

        (location_char_width, location_char_height), _ = cv.getTextSize(location, self._font, self._location_font_scale,
                                                                        self._location_font_thickness)
        location_position_offset = min(h, w) * self._location_rate
        self._location_x, self._location_y = int(w - location_position_offset - location_char_width), int(
            h - location_position_offset)

    def _draw(self, record: Record, image, **kargs):
        if not self._prepared:
            self._prepare_data(image, str(record.location))
        # 时间
        image_text = record.date_time.astimezone().strftime('%Y-%m-%d %H:%M:%S')

        cv.putText(image, image_text, (self._time_x, self._time_y),
                   self._font, self._time_font_scale, self._time_font_color, self._time_font_thickness)

        cv.putText(image, str(record.location), (self._location_x, self._location_y),
                   self._font, self._location_font_scale, self._location_font_color, self._location_font_thickness)

        return image
