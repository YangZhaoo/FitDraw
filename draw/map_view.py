from parser import Record
from .base import ViewBase
from typing import List
import numpy as np
import cv2 as cv
from numpy import ndarray


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

        (_, distance_char_height), _ = cv.getTextSize('0', self._font, self._distance_font_scale,
                                                                    self._distance_font_thickness)

        # 不可修改
        self._prepared = False
        self._map_edge_size = int(self._map_size * self._map_edge_rate)
        self._map_box_inner_size = int(self._map_size * (
            1 - self._map_edge_rate * 2))
        self._image_h, self._image_w = None, None
        self._map = np.zeros((self._map_size, self._map_size, 3),
                             dtype=np.uint8)
        self._map_inner_delta_position = np.array(
            [self._map_edge_size, self._map_edge_size])
        self._distance_position = self._map_inner_delta_position + np.array([0, self._map_box_inner_size + distance_char_height])
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

    def _draw(self, record: Record, image, **kargs):
        if not self._prepared:
            self._prepare_data(image, kargs['record_info']['records'])
            self._prepared = True
        image_roi = image[self._map_out_delta_position[1]:
                          self._map_out_delta_position[1] + self._map_size,
                    self._map_out_delta_position[0]:
                    self._map_out_delta_position[0] + self._map_size,
                    :]
        image_roi[self._map_mask] = self._map[self._map_mask]

        if record.location is None:
            return image
        current_point = self._convert_position(record.location.getNpArray())[
                            0] + self._map_out_delta_position
        cv.circle(image, current_point, self._current_sign_radius,
                  self._current_sign_color, lineType=cv.LINE_AA,
                  thickness=-1)
        if record.distance is not None:
            cv.putText(image, f"{record.distance:.2f}m", self._distance_position,
                       self._font, self._distance_font_scale, self._distance_font_color, self._distance_font_thickness)

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
