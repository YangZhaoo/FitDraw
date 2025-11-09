from parser import Record, Location
from .base import ViewBase
from typing import List
import numpy as np
import cv2 as cv


class GlobalMap(ViewBase):

    def __init__(self):
        self._prepared = False
        self._map_size = 500
        self._map_edge_rate = 0
        self._map_edge_size = self._map_size * self._map_edge_rate
        self._map_box_inner_size = self._map_size * (1 - self._map_edge_rate * 2)

        self._image_h, self._image_w = None, None

        self._map = np.zeros((self._map_size, self._map_size, 3), dtype=np.uint8)
        self._min_log_lat = None
        self._max_log_lat = None


    def _convert_position(self, position: Location):
        np_position = np.array([position.longitude, position.latitude]).reshape(-1, 2)
        normailize_log_lat = (np_position - self._min_log_lat) * (self._max_log_lat - self._min_log_lat)
        draw_pos = np.array((normailize_log_lat * np.array([[1, -1]]) + np.array([[0, 1]])) * self._map_box_inner_size, dtype=np.int32)
        return draw_pos


    def _prepare(self, image, records: List[Record]):
        self._image_h, self._image_w = image.shape[:2]
        self._map = np.zeros_like(image, dtype=np.uint8)
        positions = np.asarray([(record.location.longitude, record.location.latitude)for record in records if record.location is not None])
        self._min_log_lat = np.array([np.min(positions[:, 0]), np.min(positions[:, 1])])
        self._max_log_lat = np.array([np.max(positions[:, 0]), np.max(positions[:, 1])])
        normailize_log_lat = (positions - self._min_log_lat) * (self._max_log_lat - self._min_log_lat)
        # 坐标变化 + 缩放
        draw_pos = np.array((normailize_log_lat * np.array([[1, -1]]) + np.array([[0, 1]])) * self._map_box_inner_size, dtype=np.int32) + np.array([self._image_w - self._map_size, self._map_edge_size])
        cv.polylines(self._map, [draw_pos], isClosed=False, color=(255, 255, 255), thickness=5)

    def _draw(self, record: Record, image, **kargs):
        if not self._prepared:
            self._prepare(image, kargs['records'])
            self._prepared = True
        image = np.where(self._map > 0, self._map, image)
        if record.location is None:
            return image
        current_point = self._convert_position(record.location)[0] +  + np.array([self._image_w - self._map_size, self._map_edge_size])
        cv.circle(image, current_point, 10, (0, 255, 0), lineType=cv.LINE_AA, thickness=-1)
        return image
