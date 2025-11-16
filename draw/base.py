from abc import ABC, abstractmethod
from parser import Record


class ViewBase(ABC):

    def __init__(self, next_view=None):
        self.next_view = next_view

    def do_draw(self, record: Record, image, draw_box, **kargs):
        image = self._draw(record, image, **kargs)
        if draw_box:
            self._draw_box(image)
        if self.next_view is not None:
            image = self.next_view.do_draw(record, image, draw_box, **kargs)
        return image


    @abstractmethod
    def _draw(self, record: Record, image, **kargs):
        pass

    @abstractmethod
    def _draw_box(self, image):
        pass

    def clean_session_status(self):
        pass
