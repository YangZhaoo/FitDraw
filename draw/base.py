import cv2 as cv


class ViewBase:

    def __init__(self):
        self._window_name = "Demo"

    def image_show(self, image):
        cv.imshow(self._window_name, image)
        cv.waitKey(2000)