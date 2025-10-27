import cv2 as cv
import numpy as np

class LoopSpeed:

    def __init__(self, max_speed=60):
        super().__init__()
        self._width = 200
        self._height = 200
        self._outer_radius = int(self._height / 2)
        self._inner_radius = int(self._outer_radius * 0.85)
        self._min_speed = 0
        self._max_speed = max_speed
        self._speed_unit = 'Km/h'
        self._min_angle = -210
        self._max_angle = 30
        self._loop_color = (245, 179, 38)


        # 速度
        self._font = cv.FONT_HERSHEY_SIMPLEX
        self._speed_font_scale = 1.5
        self._speed_font_thickness = 2
        self._speed_font_color = (255, 255, 255)

        # 单位
        self._unit_font_scale = 1
        self._unit_font_thickness = 1
        self._unit_font_color = (27, 52, 206)

        # 位置参数
        self._x_rate = 0.1
        self._y_rate = 0.85
        self._center = None

        self._prepared = False

    def _prepare_data(self, image):
        image_height, image_width = image.shape[:2]
        self._center = (int(image_width * 0.1), int(image_height * 0.85))
        (self._speed_char_width, self._speed_char_height), _ = cv.getTextSize("0",
                                                                  self._font,
                                                                  self._speed_font_scale,
                                                                  self._speed_font_thickness)

        (self._unit_width, self._unit__height), _ = cv.getTextSize(self._speed_unit,
                                                                  self._font,
                                                                  self._unit_font_scale,
                                                                  self._unit_font_thickness)

        self._prepared = True

    def draw(self, speed, image):
        if not self._prepared:
            self._prepare_data(image)

        panel = np.zeros_like(image, dtype=np.uint8)
        text = "--" if speed == 0 else str(speed)
        start_angle = self._min_angle
        end_angle = self._get_end_angle(speed)
        cv.ellipse(panel, self._center,
                   (self._outer_radius, self._outer_radius), 0, start_angle,
                   end_angle, self._loop_color, -1, lineType=cv.LINE_AA)
        cv.circle(panel, self._center, self._inner_radius, (0, 0, 0), -1,
                  lineType=cv.LINE_AA)

        # 速度
        cv.putText(panel, text, (
            int(self._center[0] - self._speed_char_width * len(text) / 2),
            int(self._center[1] + self._speed_char_height / 2)),
                   self._font, self._speed_font_scale, self._speed_font_color,
                   self._speed_font_thickness)

        # 单位
        cv.putText(panel, self._speed_unit, (
            int(self._center[0] - self._unit_width / 2),
            int(self._center[1] + self._height * 0.3)),
                   self._font, self._unit_font_scale, self._unit_font_color,
                   self._unit_font_thickness)

        gray_image = cv.cvtColor(panel, cv.COLOR_BGR2GRAY)
        # self.image_show(cv.cvtColor(gray_image, cv.COLOR_GRAY2BGR))
        _, image_mask = cv.threshold(cv.cvtColor(gray_image, cv.COLOR_GRAY2BGR),
                                     127, 255, cv.THRESH_BINARY_INV)
        return cv.bitwise_or(cv.bitwise_and(image_mask, image), panel)

    def _get_end_angle(self, speed):
        angle = (speed - self._min_speed) / (
            self._max_speed - self._min_speed) * (
            self._max_angle - self._min_angle)
        return max(angle, 1) + self._min_angle