import cv2 as cv
from draw.speed_view import LoopSpeed


if __name__ == '__main__':
    img = cv.imread('../img/01.png')

    loopView = LoopSpeed()
    img = loopView.draw(30, img)
    cv.imshow("img", img)

    cv.waitKey(2000)