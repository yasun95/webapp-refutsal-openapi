import sys, argparse
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from refutsal_util.refutsal_cluster import RefutsalCluster
start_time = time.time()

# SUNJONG EDIT
def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--UUID', type=str, default='')
    parser.add_argument('--input-path', type=str, default='')
    parser.add_argument('--output-path', type=str, default='')
    parser.add_argument('--output-filename', type=str, default='')
    opt = parser.parse_args()

    return opt

opt = parse_opt()

input_path = opt.input_path
output_path = opt.output_path


#분석기 초기화
#print_en  0: 프린트 없음  1 : 최소 정보 2: 최대정보
RC = RefutsalCluster(print_en=0)

#입력타입1. 파일명 하나씩 등록 
#RC.addFilePath('D:\library\yolov5-master\\runs\\testcsv\cam1r.csv')
#RC.addFilePath('D:\library\yolov5-master\\runs\\testcsv\cam2r.csv')
#RC.addFilePath('D:\library\yolov5-master\\runs\\testcsv\cam3r.csv')
#RC.addFilePath('D:\library\yolov5-master\\runs\\testcsv\cam4r.csv')

#입력타입2. 디렉토리 내부 모든 csv 파일 동시 등록
#RC.addForderPath('C:\\dev_program\\Refutsal_Dev_Repo\\data\\birds_eye_result')
# RC.addForderPath('C:\\dev_program\\RefutsalVideoAnalysis\\input\\test_service\\detect')
RC.addForderPath(input_path)


#결과 출력할 위치 생성
fieldnames = ['frame', 'cls','id', 'team','x', 'y', 'group']
#RC.makeOutputForder("C:\\dev_program\\Refutsal_Dev_Repo\\data", fieldnames=fieldnames)
# RC.makeOutputForder('C:\\dev_program\\RefutsalVideoAnalysis\\input\\test_service\\detect', fieldnames=fieldnames)

# SUNJONG EDIT / ADD FOLDER & FILE NAME
RC.makeOutputForder(output_path, filename=opt.output_filename, fieldnames=fieldnames)

#프레임별 분석
RC.openCsv()
while(RC.updateFrame()):
    #RC.makeDisMat() #거리행렬 계산(시각화용 버전)
    #RC.showDisMat() #거리행렬 시각화

    RC.makeDict() #거리행렬 계산(성능향상버전)
    
    #RC.cluster(distance=1500)#클러스터링 거리 35 이하까지 
    #RC.cluster(epoch=3 )#클러스터링 횟수 3회
    RC.cluster(leave_player=11, csv_write=True)#객체 15개 될때까지 클러스터링
    
    #데이터수 증가에따라 사람들간거리 문제 될수도...?
    #카메라 위치 생각해서 비중 포함시키기?

RC.printTimer()
print("=================    All success!    ==================")
print("time :", time.time() - start_time)  # 현재시각 - 시작시간 = 실행 시간
