from parser import Record
from .base import ViewBase
import cv2 as cv
import numpy as np

class TextView(ViewBase):
    def __init__(self, next_view=None):
        super().__init__(next_view)

        # 时间配置
        self._font = cv.FONT_HERSHEY_SIMPLEX
        self._time_font_scale = 1.5
        self._time_font_thickness = 3
        self._time_font_color = (255, 255, 255)
        self._time_position_rate = 0.025
        self._time_x = None
        self._time_y = None
        self._time_char_width = None
        self._time_char_height = None

        # 坐标配置
        self._location_rate = self._time_position_rate
        self._location_font_scale = 1.5
        self._location_font_thickness = 2
        self._location_font_color = (255, 255, 255)
        self._location_x = None
        self._location_y = None
        self._location_char_width = None
        self._location_char_height = None

        self._prepared = False

    def _prepare_data(self, image, time_str: str, location: str):
        h, w = image.shape[:2]

        (self._time_char_width, self._time_char_height), _ = cv.getTextSize(time_str, self._font, self._time_font_scale,
                                                                self._time_font_thickness)
        time_position_offset = min(h, w) * self._time_position_rate
        self._time_x, self._time_y = int(time_position_offset), int(time_position_offset + self._time_char_height)

        (self._location_char_width, self._location_char_height), _ = cv.getTextSize(location, self._font, self._location_font_scale,
                                                                        self._location_font_thickness)
        location_position_offset = min(h, w) * self._location_rate
        self._location_x, self._location_y = int(w - location_position_offset - self._location_char_width), int(
            h - location_position_offset)

    def _draw(self, record: Record, image, **kargs):
        image_text = record.date_time.astimezone().strftime('%Y-%m-%d %H:%M:%S')
        if not self._prepared:
            self._prepare_data(image, image_text, str(record.location))
        # 时间

        cv.putText(image, image_text, (self._time_x, self._time_y),
                   self._font, self._time_font_scale, self._time_font_color, self._time_font_thickness)

        if record.location is not None:
            cv.putText(image, str(record.location), (self._location_x, self._location_y),
                       self._font, self._location_font_scale, self._location_font_color, self._location_font_thickness)

        return image

    def _draw_box(self, image):
        time_original_position = np.array([self._time_x, self._time_y - self._time_char_height])
        time_target_position = time_original_position + np.array([self._time_char_width, self._time_char_height])
        cv.rectangle(image, time_original_position, time_target_position, (0, 0, 255), 1)

        location_original_position = np.array([self._location_x, self._location_y - self._location_char_height])
        location_target_position = location_original_position + np.array([self._location_char_width, self._location_char_height])
        cv.rectangle(image, location_original_position, location_target_position, (0, 0, 255), 1)
