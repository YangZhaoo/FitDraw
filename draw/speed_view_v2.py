import cv2 as cv
import numpy as np

from draw.base import ViewBase


class LoopSpeedV2(ViewBase):

    def __init__(self, max_speed=60, next_view=None):
        super().__init__(next_view)
        self._width = 400
        self._height = 400
        self._outer_radius = int(self._height / 2)
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
        self._unit_font_scale = 1.5
        self._unit_font_thickness = 2
        self._unit_font_color = (27, 52, 255)

        # 位置参数
        self._x_rate = 0.15
        self._y_rate = 0.80
        self._center = None # 使用center_x、center_y来代替
        self._cache = {}

        self._prepared = False

    def _prepare_data(self, image):
        image_height, image_width = image.shape[:2]
        self._panel_template = np.zeros_like(image, dtype=np.uint8)
        self._center = (int(image_width * 0.1), int(image_height * 0.85))
        (self._speed_char_width, self._speed_char_height), _ = cv.getTextSize("0",
                                                                  self._font,
                                                                  self._speed_font_scale,
                                                                  self._speed_font_thickness)

        (self._unit_width, self._unit_height), _ = cv.getTextSize(self._speed_unit,
                                                                  self._font,
                                                                  self._unit_font_scale,
                                                                  self._unit_font_thickness)

        self._prepared = True


    def _get_speed_mask(self, speed):
        if speed in self._cache:
            return self._cache[speed]
        text = "--" if speed == 0 else str(speed)
        panel = self._panel_template.copy()
        start_angle = self._min_angle
        end_angle = self._get_end_angle(speed)

        # 绘制速度圆环
        cv.ellipse(panel, self._center,
                   (self._outer_radius, self._outer_radius), 0, start_angle,
                   end_angle, self._loop_color, -1, lineType=cv.LINE_AA)
        # super().image_show(panel)
        cv.circle(panel, self._center, self._inner_radius, (0, 0, 0), -1,
                  lineType=cv.LINE_AA)
        # super().image_show(panel)

        # 绘制速度数字，坐标位置，左下角。
        cv.putText(panel, text, (
            int(self._center[0] - self._speed_char_width * len(text) / 2),
            int(self._center[1] + self._speed_char_height / 2)),
                   self._font, self._speed_font_scale, self._speed_font_color,
                   self._speed_font_thickness)
        # super().image_show(panel)

        # 绘制单位，坐标位置，左下角。
        cv.putText(panel, self._speed_unit, (
            int(self._center[0] - self._unit_width / 2),
            int(self._center[1] + self._speed_char_height / 2 + self._unit_height * 1.5)),
                   self._font, self._unit_font_scale, self._unit_font_color,
                   self._unit_font_thickness)
        # super().image_show(panel)

        # 创建掩码：找出 panel 中非黑色的区域
        gray_panel = cv.cvtColor(panel, cv.COLOR_BGR2GRAY)
        # super().image_show(gray_panel)
        _, mask = cv.threshold(gray_panel, 1, 255, cv.THRESH_BINARY)
        # super().image_show(mask)


        # 将 mask 转换为3通道
        mask_3ch = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
        self._cache[speed] = (panel, mask_3ch)
        return panel, mask_3ch

    def _draw(self, record, image, **kargs):
        speed = record.speed
        if not self._prepared:
            self._prepare_data(image)

        result = image.copy()
        # 创建一个临时画布用于绘制速度仪表盘

        # super().image_show(panel)


        # super().image_show(mask_3ch)

        panel, mask_3ch = self._get_speed_mask(speed)

    # 使用 np.where 直接在结果图像上叠加速度仪表盘
        # 这样可以避免复杂的位运算，保持原图像不变
        result = np.where(mask_3ch > 0, panel, result)
        # super().image_show(result)
        return result

    def _get_end_angle(self, speed):
        angle = (speed - self._min_speed) / (
            self._max_speed - self._min_speed) * (
            self._max_angle - self._min_angle)
        return max(angle, 1) + self._min_angle