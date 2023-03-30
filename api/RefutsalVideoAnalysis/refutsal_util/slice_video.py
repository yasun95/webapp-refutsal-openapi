import os
import sys
from videowriter import videoWriter

VID_DIR = 'C:\dev_program\RefutsalVideoAnalysis\input\TTA_origin_video'
VID_NAME = '06_origin13.avi'
WRITE_PATH = 'C:\dev_program\RefutsalVideoAnalysis\input\TTA_origin_video'

vm = videoWriter()
vm.setOriginVideo(VID_DIR, VID_NAME) # 원본 영상 지정
vm.setTimeMargin(7,5)
vm.setWritePath(WRITE_PATH)
vm.makeClip(1885, output_name='miss_clip1') #골 넣은 프레임, 출력파일 넘버
vm.makeClip(2333, output_name='miss_clip2') #골 넣은 프레임, 출력파일 넘버
vm.makeClip(3000, output_name='miss_clip3') #골 넣은 프레임, 출력파일 넘버