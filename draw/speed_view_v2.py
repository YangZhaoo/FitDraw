import cv2 as cv
import numpy as np

from draw.base import ViewBase


class LoopSpeedV2(ViewBase):

    def __init__(self, max_speed=60, next_view=None):
        super().__init__(next_view)
        self._panel_box_out_size = 600
        self._panel_box_edge_rate = 0.05

        self._panel_box_edge = int(self._panel_box_out_size * self._panel_box_edge_rate)
        self._panel_box_inner_size = int(self._panel_box_out_size * (1 - self._panel_box_edge_rate * 2))
        self._outer_radius = int(self._panel_box_inner_size / 2)
        self._inner_radius = int(self._outer_radius * 0.75)
        self._min_speed = 0
        self._max_speed = max_speed
        self._speed_unit = 'Km/h'
        self._min_angle = -210
        self._max_angle = 30
        self._loop_color = (245, 179, 38)

        # 速度
        self._font = cv.FONT_HERSHEY_SIMPLEX
        self._speed_font_scale = 2.5
        self._speed_font_thickness = 3
        self._speed_font_color = (255, 255, 255)

        # 单位
        self._unit_font_scale = 2
        self._unit_font_thickness = 3
        self._unit_font_color = (27, 52, 255)

        # 位置参数
        self._panel_box_position = None
        self._center = np.array([int(self._panel_box_out_size / 2), int(self._panel_box_out_size / 2)])
        self._cache = {}
        self._prepared = False

    def _prepare_data(self, image):
        self._image_h, self._image_w = image.shape[:2]
        (self._speed_char_width, self._speed_char_height), _ = cv.getTextSize(
            "0",
            self._font,
            self._speed_font_scale,
            self._speed_font_thickness)

        (self._unit_width, self._unit_height), _ = cv.getTextSize(
            self._speed_unit,
            self._font,
            self._unit_font_scale,
            self._unit_font_thickness)

        # 位置坐标：左下角
        self._panel_box_position = np.array([200, self._image_h - self._panel_box_out_size - 100])
        self._prepared = True

    def _get_speed_mask(self, speed):
        if speed in self._cache:
            return self._cache[speed]
        text = "--" if speed == 0 else f'{speed:.2f}'
        panel = np.zeros((self._panel_box_out_size, self._panel_box_out_size, 3), dtype=np.uint8)
        start_angle = self._min_angle
        end_angle = self._get_end_angle(speed)

        # 绘制速度圆环
        cv.ellipse(panel, self._center,
                   (self._outer_radius, self._outer_radius), 0, start_angle,
                   end_angle, self._loop_color, -1, lineType=cv.LINE_AA)
        cv.circle(panel, self._center, self._inner_radius, (0, 0, 0), -1,
                  lineType=cv.LINE_AA)

        # 绘制速度数字，坐标位置，左下角。
        cv.putText(panel, text, (
            int(self._center[0] - self._speed_char_width * len(text) / 2),
            int(self._center[1] + self._speed_char_height / 2)),
                   self._font, self._speed_font_scale, self._speed_font_color,
                   self._speed_font_thickness)

        # 绘制单位，坐标位置，左下角。
        cv.putText(panel, self._speed_unit, (
            int(self._center[0] - self._unit_width / 2),
            int(self._center[
                    1] + self._speed_char_height / 2 + self._unit_height * 1.5)),
                   self._font, self._unit_font_scale, self._unit_font_color,
                   self._unit_font_thickness)

        panel_mask = np.any(panel > 0, axis=2)
        self._cache[speed] = (panel, panel_mask)
        return panel, panel_mask

    def _draw(self, record, image, **kargs):
        if not self._prepared:
            self._prepare_data(image)

        speed = record.speed if record.speed is not None else 0
        panel, panel_mask = self._get_speed_mask(speed)
        image_roi = image[self._panel_box_position[1]: self._panel_box_position[1] + self._panel_box_out_size,
                    self._panel_box_position[0]: self._panel_box_position[0] + self._panel_box_out_size,
                    :]
        image_roi[panel_mask] = panel[panel_mask]

        return image

    def _draw_box(self, image):
        cv.rectangle(image, self._panel_box_position + np.array([self._panel_box_edge, self._panel_box_edge]),
                     self._panel_box_position + np.array([self._panel_box_edge, self._panel_box_edge]) + np.array(
                         [self._panel_box_inner_size, self._panel_box_inner_size]),
                     (0, 0, 255), thickness=1)
        cv.rectangle(image, self._panel_box_position,
                     self._panel_box_position + np.array(
                         [self._panel_box_out_size, self._panel_box_out_size]),
                     (0, 255, 0), thickness=1)

    def _get_end_angle(self, speed):
        angle = (speed - self._min_speed) / (
            self._max_speed - self._min_speed) * (
                    self._max_angle - self._min_angle)
        return max(angle, 1) + self._min_angle