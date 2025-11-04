from parser import Record
from .base import ViewBase
from collections import deque
import numpy as np


class FrameBlend(ViewBase):
    def __init__(self, n_weights=[0.5, 0.25, 0.15, 0.1], next_view=None):
        super().__init__(next_view)
        self._n_weight = n_weights
        self._n_frames = len(self._n_weight)
        self._frame_queue = deque(maxlen=len(n_weights))


    def _draw(self, record: Record, image, **kargs):
        self._frame_queue.append(image.copy())
        if len(self._frame_queue) == self._n_frames:
            # 创建混合帧（初始为全黑）
            blended_frame = np.zeros_like(image, dtype=np.float32)

            # 按照权重混合前n帧
            for i, weight in enumerate(self._n_weight):
                frame_index = self._n_frames - 1 - i  # 从最近的帧开始
                frame_to_blend = self._frame_queue[frame_index].astype(np.float32)
                blended_frame += frame_to_blend * weight
            # 转换回uint8类型
            return np.clip(blended_frame, 0, 255).astype(np.uint8)
        else:
            return image