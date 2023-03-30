import os
import sys
import cv2
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from refutsal_util.birds_eye_utils import getpoint
player =[]
ground_points = []
#player_pos= np.array([[]])
player_pos= np.empty((0,2), int)

# 기준좌표 작성해야할 영상 / 사진 (.jpg, .mp4, .avi)
VIDEO_PATH ="C:\dev_program\RefutsalVideoAnalysis\input\\video\\08_2022-12-09_235000_000000.avi"

cap = cv2.VideoCapture(VIDEO_PATH)
while cap.isOpened():
    ret, frame = cap.read()

    getpoint(frame)
    cap.release()
    break
#YoloDetect()
#testHomography()
#playerHomography()


