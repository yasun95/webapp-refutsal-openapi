import cv2
import os
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from refutsal_util.videowriter import videoWriter
from refutsal_util.file_path_collector import FilePathCollector
VIDEO_PATH = "C:\dev_program\RefutsalVideoAnalysis\input\TTA_origin_video"
WRITE_PATH = "C:\dev_program\RefutsalVideoAnalysis\output\TTA_random_clip"
#CLIP_FRAME_LENGTH = 120
RANDOM_SEED = 42
SAMPLE_NUM = 3
SAMPLE_LENGTH = 10 #sec

fpc = FilePathCollector(VIDEO_PATH, findformat=".avi")
files = fpc.getAllVideoPath()
print(files)
for vid_path in files:
    vw = videoWriter()
    vw.setOriginVideo(os.path.dirname(vid_path), os.path.basename(vid_path))
    vw.setTimeMargin(0,SAMPLE_LENGTH)
    vw.setWritePath(WRITE_PATH)

    np.random.seed(42)
    rand_point = np.random.randint(0,vw.getFrameLength()-SAMPLE_LENGTH*vw.getFPS(),SAMPLE_NUM)
    #rand_point = np.sort(rand_point)
    print("sampleling points(frame)")
    print(rand_point)

    name = "_clip_{0}"

    for clip_num, start_frame in enumerate(rand_point):
        vw.makeClip(start_frame, output_name=name.format(clip_num))
