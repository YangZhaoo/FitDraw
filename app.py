import cv2 as cv
from draw.speed_view import LoopSpeed


if __name__ == '__main__':
    img = cv.imread('./img/01.png')

    max_speed=40
    loopView = LoopSpeed(max_speed=max_speed)
    for i in range(max_speed):
        cv.imshow("img", loopView.draw(i, img.copy()))
        cv.waitKey(500)