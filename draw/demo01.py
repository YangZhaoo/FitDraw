import cv2 as cv
import numpy as np
from speed_view import LoopSpeed


img = cv.imread(cv.samples.findFile("../img/01.png"))


loopView = LoopSpeed()
img = loopView.draw(30, img)
cv.imshow("img", img)

cv.waitKey(2000)