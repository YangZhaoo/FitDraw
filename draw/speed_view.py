import cv2 as cv
import numpy as np


class LoopSpeed:

    def __init__(self):
        self._center = None
        self._width = 200
        self._height = 200
        self._outer_radius = int(self._height / 2)
        self._inner_radius = int(self._outer_radius * 0.85)
        self._min_speed = 0
        self._max_speed = 60
        self._min_angle = -210
        self._max_angle = 30
        self._loop_color = (245, 179, 38)
        self._font_color = (255, 255, 255)

    def draw(self, speed, image):
        start_angle = self._min_angle
        end_angle = (speed - self._min_speed) / (
                self._max_speed - self._min_speed) * (
                            self._max_angle - self._min_angle) + self._min_angle
        text = f"{speed}"
        font = cv.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 1
        (text_width, text_height), baseline = cv.getTextSize(text, font,
                                                             font_scale,
                                                             font_thickness)

        panel = np.zeros_like(image, dtype=np.uint8)
        if self._center is None:
            image_height, image_width = image.shape[:2]
            self._center = (int(image_width * 0.1), int(image_height * 0.85))
        cv.ellipse(panel, self._center, (self._outer_radius, self._outer_radius), 0, start_angle,
                   end_angle, self._loop_color, -1, lineType=cv.LINE_AA)
        cv.circle(panel, self._center, self._inner_radius, (0, 0, 0), -1,
                  lineType=cv.LINE_AA)
        cv.putText(panel, text, (
        int(self._center[0] - text_width / 2), int(self._center[1] + text_height / 2)),
                   font, font_scale, self._font_color,
                   font_thickness)
        return cv.bitwise_or(image, panel, )

