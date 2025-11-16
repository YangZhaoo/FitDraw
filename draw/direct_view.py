from collections import deque
from typing import List

from parser import Record
from .base import ViewBase
import numpy as np
import cv2 as cv


class DirectView(ViewBase):

    def __init__(self):

        # 可以修改
        self._direct_out_size = 300
        self._direct_edge_rate = 0.3
        self._direct_fill_color = (240, 240, 240)
        self._center = (
        int(self._direct_out_size / 2), int(self._direct_out_size / 2))

        # 不可修改
        self._prepared = False
        self._direct_edge_size = int(
            self._direct_out_size * self._direct_edge_rate)
        self._direct_inner_size = int(
            self._direct_out_size * (1 - self._direct_edge_rate * 2))

        self._image_h, self._image_w = None, None
        self._direct_sign, self._direct_mask = None, None  # 90度，正北方向
        self._init_angle = 90
        self._direct_out_position = None

        self._recent_location = deque()
        self._recent_location_set = set()
        self._cache = {}

    def _prepare_data(self, image):
        self._image_h, self._image_w = image.shape[:2]
        self._direct_sign = np.zeros(
            (self._direct_out_size, self._direct_out_size, 3), dtype=np.uint8)
        # 方向图标位置：右 中
        self._direct_sign_position = np.array(
            [self._image_w - self._direct_out_size - 100,
             int(self._image_h / 2 - self._direct_out_size / 2)])

        points = np.array([
            [int(self._direct_out_size / 2), self._direct_edge_size],
            [self._direct_edge_size,
             self._direct_out_size - self._direct_edge_size],
            [int(self._direct_out_size / 2),
             int(self._direct_edge_size + self._direct_inner_size * 0.8)],
            [self._direct_out_size - self._direct_edge_size,
             self._direct_out_size - self._direct_edge_size]
        ])
        cv.fillPoly(self._direct_sign, [points], self._direct_fill_color)
        self._direct_mask = np.any(self._direct_sign > 0, axis=2)
        self._cache[self._init_angle] = (self._direct_sign, self._direct_mask)

    def _get_direct_and_mask(self, angle):
        if angle in self._cache:
            return self._cache[angle]

        trun_angle = angle - self._init_angle
        rotation_matrix = cv.getRotationMatrix2D(self._center, trun_angle, 1)
        # 应用仿射变换
        sign = cv.warpAffine(self._direct_sign, rotation_matrix,
                                (self._direct_out_size, self._direct_out_size))
        mask = np.any(sign > 0, axis=2)
        self._cache[angle] = (sign, mask)
        return (sign, mask)

    def _draw(self, record: Record, image, **kargs):
        if not self._prepared:
            self._prepare_data(image)
            self._prepared = True

        global_info = kargs['global_info']
        recent_record: List[Record] = kargs['record_info']['recent_record']
        if recent_record is not None and recent_record[0] is not None and recent_record[-1] is not None:
            angle = recent_record[0].location.getAngle(recent_record[-1].location)
            global_info['last_angle'] = angle
        else:
            angle = global_info.get('last_angle', self._init_angle)

        kargs['frame']['current_angle'] = angle

        direct_sign, direct_mask = self._get_direct_and_mask(angle)

        image_roi = image[
                    self._direct_sign_position[1]: self._direct_sign_position[
                                                       1] + self._direct_out_size,
                    self._direct_sign_position[0]: self._direct_sign_position[
                                                       0] + self._direct_out_size,
                    :]
        image_roi[direct_mask] = direct_sign[direct_mask]
        return image

    def _draw_box(self, image):
        cv.rectangle(image, self._direct_sign_position + np.array([self._direct_edge_size, self._direct_edge_size]),
                     self._direct_sign_position + np.array([self._direct_edge_size, self._direct_edge_size]) + np.array(
                         [self._direct_inner_size, self._direct_inner_size]),
                     (0, 0, 255), thickness=1)
        cv.rectangle(image, self._direct_sign_position,
                     self._direct_sign_position + np.array(
                         [self._direct_out_size, self._direct_out_size]),
                     (0, 255, 0), thickness=1)