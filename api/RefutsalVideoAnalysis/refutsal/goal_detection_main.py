import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from refutsal_util.goal_detection_db import GoalDetector
#for SW subject
#세팅폴더경로 / 원본 영상폴더 경로 / 클립저장할 폴더 경로
# CAM_SETTING = 'C:\dev_program\RefutsalVideoAnalysis\\refutsal_config\stadium\\test_cali.json'
# VID_PATH = 'C:\dev_program\RefutsalVideoAnalysis\input\\test_service'
# OUTPUT_PATH = 'C:\dev_program\RefutsalVideoAnalysis\input\\test_service'

CAM_SETTING = os.path.abspath('refutsal_config/stadium/test_cali.json')
VID_PATH = os.path.abspath('input/test_service')
OUTPUT_PATH = os.path.abspath('input/test_service')

#refutsal.com
HOST = '3.36.242.44'
PORT = 3306
USER = 'refutsal.tecs.club'
PASSWORD = 'refutsal!@34'
DBNAME = 'refutsal.tecs.club'
UUID = '0xtest_taguploader'
TEST_COURT_UUID='3ddfb499c0b44b92'

#폴더내 모든 영상 분석
#객체 선언 및 경로 설정 / 정보 확인

#gd = GoalDetector(videodir = VID_PATH, cam_setting_path=CAM_SETTING) #로컬 json setting file
gd = GoalDetector(videodir = VID_PATH,
                  host= HOST,
                  port = PORT,
                  user = USER, 
                  password = PASSWORD, 
                  db = DBNAME, 
                  court_uuid=TEST_COURT_UUID,
                  ) # DB setting file
gd.setWriteDir(OUTPUT_PATH)
gd.printFilePath() #출력 1  
gd.makeOutputCsv()
# 디렉토리 내 모든 동영상 분석

for vidnum, vidname in enumerate(gd.getAllVideoPath()):
    if gd.setVideo(filenum=vidnum, resize=(1024,576)): #분석할 파일 선택 원본영상은 2560*1440 성능위해 프레임 축소후 분석
      #gd.setgoalmask(opt="read") #ROI 등록해야할때
      gd.printChart() #출력2
      gd.serchVideo(imgshow=False, color_filter='yellow') #분석중함수 (영상 표시여부 True)
      #gd.serchVideo(imgshow=True) #분석중함수 (영상 표시여부 True)
      gd.remapFrame(5) #중복제거할 타임갭 5초
      #gd.makeClip(ask=False) #ask = True 일경우 저장여부 물어봄
      gd.writeData()
    else:
      print("skip video : ", vidname, " \n\tdo not have enough goal points(least 4) on config file")

    """
출력 1 예시
------------------------------------------------------------
             F:\test_video\goal_detection\input
------------------------------------------------------------
  file number  |                  file path
       0       |             02_2022-11-24_193000_194000.avi
       1       |             04_2022-11-24_201000_202000.avi
------------------------------------------------------------
"""

"""
출력 2 예시
------------------------------------------------------------
             F:\test_video\goal_detection\input
--------------02_2022-11-24_193000_194000.avi---------------
Video name          |        02_2022-11-24_193000_194000.avi
camera number       |                                   cam2
origin video size   |                              2560*1440
resize video size   |                               1024*576
csv standard size   |                              2560*1440
resize ratio        |                                    0.4
video frame count   |                            17991 frame
video play time     |                                 0:10:0
video fps           |                                  29.97
------------------------------------------------------------
█████████████████████████████████████████████████░99% 0:10:46
"""