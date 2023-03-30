import cv2
import os
import sys
import pandas as pd
import numpy as np
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from refutsal_util.csv_reader import CsvReader

class PosVisualizer(CsvReader):
    '''
    cluseter를 통해 획득한 csv파일을 분석해 프레임별로 시각화 및 동영상 생성
    '''

    def __init__(self, print_en=0, data_type = 'birds_eye'):
        if(data_type == 'birds_eye'):
            self.mode = 'birds_eye'
            CsvReader.__init__(self, print_en, output_colums=['frame', 'camnum', 'id', 'team', 'cls','x', 'y'])
        elif(data_type == 'clustering'):
            self.mode = 'clustering'
            CsvReader.__init__(self, print_en, output_colums=['frame', 'cls', 'id', 'team', 'x', 'y', 'group'])
        else:
            exit()
        self.fps = 30
        self.path = None
        self.nowFrame = None
        
    def setData(self, path):
        self.path = path
        self.addFilePath(path)

    def drawBoarld():
        pass

def showBirdsEyeView(frame_data, color = (255,0,0)):
    meter2fix = 80
    margin = int(0.5*meter2fix)
    rows = int(17*meter2fix+ margin*2) #경기장 사이즈
    cols = int(34*meter2fix+ margin*2)
    
    x= 5.0564
    y = 2.5617
    red_color = (0, 0, 255)
    blue_color = (255, 0, 0)
    black_color = (0,0,0)
    puple_color = (255,0,255)
    white_color = (255,255,255)
    #new_Board = np.ones((rows, cols, 3), dtype = np.uint8)*([0,255,0])
    new_board = np.full((rows, cols, 3), (71,193,129), dtype = np.uint8)
    new_board = cv2.circle(new_board, (int(cols/2), int(rows/2)), 100, white_color, 10)
    new_board = cv2.rectangle(new_board, (margin, margin), (cols-margin, rows-margin), white_color, 10)
    new_board = cv2.line(new_board, (int(cols/2), margin),(int(cols/2), rows-margin), white_color, 10)

    i = 0
    if len(frame_data) == 0 :
        frame_data= np.empty((0,2), int)

    #player_pos= np.array([78,530,1674],[587,457,500])
    print(type(frame_data))
    for i in range(len(frame_data)):
        #print(frame_data.iloc[i].x)
        footpoint = [frame_data.iloc[i].x, frame_data.iloc[i].y]
        #new_board = cv2.circle(new_board, (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), 10, black_color, 10)
        try:
            if  frame_data.iloc[i].group <2:
                continue
        except:
            pass
        if frame_data.iloc[i].cls ==32:
            new_board = cv2.circle(new_board, (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), 10, black_color, 10)
        elif frame_data.iloc[i].team == 0:
            new_board = cv2.circle(new_board, (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), 10, puple_color, 10)
        elif frame_data.iloc[i].team == 1:
            new_board = cv2.circle(new_board, (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), 10, red_color, 10)
        elif frame_data.iloc[i].team == 2:
            new_board = cv2.circle(new_board, (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), 10, blue_color, 10)

        #new_board = cv2.putText(new_board, str(i), (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), cv2.FONT_HERSHEY_COMPLEX, 1 , color)
    
    cv2.namedWindow("ground", cv2.WINDOW_NORMAL)
    cv2.imshow("ground", new_board)
    if cv2.waitKey(20) == ord('q'):
        sys.exit()

#CSV_PATH ="C:\dev_program\Refutsal_Dev_Repo\data\\birds_eye_result\\08_2022-12-09_235000_000000.csv"
#pv = PosVisualizer(data_type='birds_eye') # data_type = "clustering"

CSV_PATH ="C:\dev_program\Refutsal_Dev_Repo\data\output\leave15.csv"
pv = PosVisualizer(data_type='clustering') # data_type = "clustering"

#pv.setData("C:\dev_program\Refutsal_Dev_Repo\data\output\output.csv")
pv.setData(CSV_PATH)
while pv.getStauts():
    pv.readFrame()
    #print(pv.nowDF)
    print(pv.nowDF)
    showBirdsEyeView(pv.nowDF)
    print("---------")