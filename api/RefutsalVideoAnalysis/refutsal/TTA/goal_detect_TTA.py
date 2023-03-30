import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from refutsal_util.goal_detection_json import GoalDetector
from refutsal_util.csv_writer import CsvWriter
#for SW subject
#세팅폴더경로 / 원본 영상폴더 경로 / 클립저장할 폴더 경로
#VID_PATH = 'C:\dev_program\RefutsalVideoAnalysis\input\TTA_test_mix'
#OUTPUT_PATH = 'C:\dev_program\RefutsalVideoAnalysis\input\TTA_test_mix'

TEST = 4

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
CONFIG_PATH = 'RefutsalVideoAnalysis\\refutsal_config\stadium\\test_cali.json'

#test1
if(TEST==1):
  VID_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\goal_clips\\test1'
  OUTPUT_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\goal_clips\\test1'
elif TEST==2:
  VID_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\goal_clips\\test2'
  OUTPUT_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\goal_clips\\test2'
elif TEST==3:
  VID_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\goal_clips\\test3'
  OUTPUT_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\goal_clips\\test3'
elif TEST==4:
  VID_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\\time_test_video'
  OUTPUT_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\\time_test_video'


#폴더내 모든 영상 분석
#객체 선언 및 경로 설정 / 정보 확인

gd = GoalDetector(CONFIG_PATH, VID_PATH)
gd.setWriteDir(OUTPUT_PATH)
gd.printFilePath() #영상경로출력 1 
cw = CsvWriter(make_csv=True, csv_path=OUTPUT_PATH)

csv_header = ['video', 'result', 'start time', 'end time', 'process time', 'video_length']
cw.makeOutputForder(outputpath = OUTPUT_PATH, filename='result.csv', fieldnames=csv_header)
cw.openCsv()
# 디렉토리 내 모든 동영상 분석

for vidnum, vidname in enumerate(gd.getAllVideoPath()):
    start_time = time.time() #TTA)분석 시작시간 저장
    if gd.setVideo(filenum=vidnum, resize=(1024,576)): #분석할 파일 선택 원본영상은 2560*1440 성능위해 프레임 축소후 분석
      #gd.setgoalmask(opt="read") #ROI 등록해야할때
      gd.printChart() #출력2
      #gd.serchVideo(imgshow=False) #분석중함수 (영상 표시여부 True)
      gd.serchVideo(imgshow=False, color_filter="yellow") #TTA)비디오 분석 함수 (영상 표시여부 True)
      gd.remapFrame(3) #중복제거할 타임갭 5초
      #gd.makeClip(ask=False) #ask = True 일경우 저장여부 물어봄

      name = os.path.basename(vidname)
      if  not gd.getResult(): #TTA) 골 감지된 프레임이 없을때 False/ 있을때 True
        result = False
      else:
        result = True
      end_time = time.time() #TTA)분석 종료시간 저장
      process_time = end_time-start_time #TTA)분석 시간 계산
      video_length = gd.getVideoTime()

      cw.writerowCsv([name, result, start_time, end_time, process_time, video_length]) #csv 파일 기록
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