from parser import Record
from .base import ViewBase
from typing import List
import numpy as np
import cv2 as cv
from numpy import ndarray
from third import GaoDe
from PIL import Image, ImageDraw, ImageFont


class GlobalMap(ViewBase):

    def __init__(self):

        # 可以修改
        self._map_size = 800
        self._map_edge_rate = 0.1
        self._map_track_color = (255, 255, 255)
        self._map_track_thickness = 15
        self._current_sign_radius = 13
        self._current_sign_color = (0, 0, 255)

        self._font = cv.FONT_HERSHEY_SIMPLEX
        self._distance_font_scale = 1.5
        self._distance_font_thickness = 3
        self._distance_font_color = (255, 255, 255)

        (_, distance_char_height), _ = cv.getTextSize('0', self._font,
                                                      self._distance_font_scale,
                                                      self._distance_font_thickness)

        # 不可修改
        self._prepared = False
        self._geo_prepared = False
        self._map_edge_size = int(self._map_size * self._map_edge_rate)
        self._map_box_inner_size = int(self._map_size * (
            1 - self._map_edge_rate * 2))
        self._image_h, self._image_w = None, None
        self._map = np.zeros((self._map_size, self._map_size, 3),
                             dtype=np.uint8)
        self._map_inner_delta_position = np.array(
            [self._map_edge_size, self._map_edge_size])
        self._distance_position = self._map_inner_delta_position + np.array(
            [int(self._map_box_inner_size / 2), 0])
        self._geo_position = self._map_inner_delta_position + np.array(
            [0, self._map_box_inner_size])
        self._map_out_delta_position = None
        self._min_log_lat = None
        self._max_log_lat = None

    def _convert_position(self, np_position: ndarray):
        normailize_log_lat = (np_position - self._min_log_lat) / (
            self._max_log_lat - self._min_log_lat)
        # 坐标归一化 + 缩放
        draw_pos = np.array((normailize_log_lat * np.array(
            [[1, -1]]) + np.array([[0, 1]])) * self._map_box_inner_size,
                            dtype=np.int32)
        # 距离外框做坐标变化
        draw_pos += self._map_inner_delta_position
        return draw_pos

    def _prepare_data(self, image, records: List[Record]):
        self._image_h, self._image_w = image.shape[:2]
        self._map = np.zeros((self._map_size, self._map_size, 3),
                             dtype=np.uint8)
        # 小地图的位置 右上角
        self._map_out_delta_position = np.array(
            [self._image_w - self._map_size - 100, 100])
        self._distance_position += self._map_out_delta_position
        positions = np.asarray(
            [record.location.getNpArray() for record in records if
             record.location is not None])
        self._min_log_lat = np.array(
            [np.min(positions[:, 0]), np.min(positions[:, 1])])
        self._max_log_lat = np.array(
            [np.max(positions[:, 0]), np.max(positions[:, 1])])
        draw_pos = self._convert_position(positions)
        cv.polylines(self._map, [draw_pos], isClosed=False,
                     color=self._map_track_color,
                     thickness=self._map_track_thickness)
        self._map_mask = np.any(self._map > 0, axis=2)

    def _get_regeo_info(self, location):
        gaode = GaoDe()
        return gaode.regeo(location)

    def _cv2_add_chinese_text(self, img, text, position, font_size, color):
        """
        在图像上添加中文文本
        """
        # 转换 OpenCV 图像为 PIL 图像
        img_pil = Image.fromarray(cv.cvtColor(img, cv.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        # 加载中文字体
        try:
            # font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)  # 黑体
            font = ImageFont.truetype("/System/Library/Fonts/Arial Unicode.ttf",
                                      font_size)  # 黑体
        except:
            font = ImageFont.truetype("/System/Library/Fonts/Arial Unicode.ttf",
                                      font_size)  # Mac
            # 或者使用其他中文字体路径

        # 绘制文本
        draw.text(position, text, font=font, fill=color)

        # 转换回 OpenCV 格式
        img = cv.cvtColor(np.array(img_pil), cv.COLOR_RGB2BGR)
        return img

    def _prepare_geo(self, record: Record, **kargs):
        global_info = kargs['global_info']
        geo_info = None
        if 'geo_info' in global_info:
            geo_info = global_info['geo_info']
        elif record.location is not None:
            geo_info = self._get_regeo_info(record.location)
            global_info['geo_info'] = geo_info
        else:
            pass
        if geo_info is not None:
            self._map = self._cv2_add_chinese_text(self._map, geo_info.getSimpleInfo(),
                                       self._geo_position,
                                       50, (255, 255, 255))
            self._map_mask = np.any(self._map > 0, axis=2)
            self._geo_prepared = True

    def _draw(self, record: Record, image, **kargs):
        if not self._prepared:
            self._prepare_data(image, kargs['global_info']['records'])
            self._prepared = True

        if not self._geo_prepared:
            self._prepare_geo(record, **kargs)

        image_roi = image[self._map_out_delta_position[1]:
                          self._map_out_delta_position[1] + self._map_size,
                    self._map_out_delta_position[0]:
                    self._map_out_delta_position[0] + self._map_size,
                    :]
        image_roi[self._map_mask] = self._map[self._map_mask]

        global_info = kargs['global_info']
        current_location = global_info.get('last_geo', None)
        if record.location is not None:
            current_location = record.location
            global_info['last_geo'] = current_location

        if current_location is not None:
            current_point = \
            self._convert_position(current_location.getNpArray())[
                0] + self._map_out_delta_position
            cv.circle(image, current_point, self._current_sign_radius,
                      self._current_sign_color, lineType=cv.LINE_AA,
                      thickness=-1)

        distance = global_info.get('last_distance', None)
        if record.distance is not None:
            global_info['last_distance'] = record.distance
            distance = record.distance

        if distance is not None:
            cv.putText(image, f"{distance:.2f}m",
                       self._distance_position,
                       self._font, self._distance_font_scale,
                       self._distance_font_color, self._distance_font_thickness)

        return image

    def _draw_box(self, image):
        cv.rectangle(image,
                     self._map_out_delta_position + self._map_inner_delta_position,
                     self._map_out_delta_position + self._map_inner_delta_position + np.array(
                         [self._map_box_inner_size, self._map_box_inner_size]),
                     (0, 0, 255), thickness=1)
        cv.rectangle(image, self._map_out_delta_position,
                     self._map_out_delta_position + np.array(
                         [self._map_size, self._map_size]),
                     (0, 255, 0), thickness=1)
