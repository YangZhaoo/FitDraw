import cv2 as cv
from abc import ABC, abstractmethod
from parser import Record

class ViewBase(ABC):

    def __init__(self):
        self._window_name = "Demo"

    def image_show(self, image):
        cv.imshow(self._window_name, image)
        if cv.waitKey(0) & 0xFF == ord('q'):
            return

    @abstractmethod
    def draw(self, record: Record, image):
        pass
