import cv2
import os
import csv
import pandas as pd

import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from refutsal_util.sync_match import getimages

"""
프레임 싱크 체크용 프로그램
동영상 8개의 지정한 프레임을 한화면에 동시에 볼수있음
"""
# Add the path
paths = []
# example : paths.append("F:\\bin\\Device\\Download\\11-21-30~40\\01_2022-11-21_223000_224000.avi")

frames = [100,100,100,100,100,100,100,100 ]

images = getimages(paths, frames)
row1 = cv2.hconcat([images[0], images[1], images[2], images[3]])
row2 = cv2.hconcat([images[4], images[5], images[6], images[7]])
full = cv2.vconcat([row1, row2])

cv2.imshow('testshow',full)
cv2.waitKey(0)