import cv2
import os
import sys
from dataclasses import dataclass
import pandas as pd
import numpy as np
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from refutsal_util.file_path_collector import FilePathCollector

@dataclass
class CamData():
    real_pos = None
    pixel_pos = None
    goal_pos = None
    frame_size =None
    stadium_size = None
class CamCsvReader(FilePathCollector): 
    """
    dir에 cam_setting1.csv형태의 파일 찾아서 데이터 클래스(CamData)로 읽어줌
    ex)
    settingdata = CamCsvReader("D:\\dir\\path")
    camnum = 0
    print(settingdata[camnum].pixel_pos)
    """
    def __init__(self, dir):
        fpc = FilePathCollector(findformat=".csv")
        fpc.setForderPath(dir)
        cam_setting_file_list = ["cam_setting1.csv","cam_setting2.csv",
            "cam_setting3.csv","cam_setting4.csv","cam_setting5.csv"]
        self.cam_setting = []

        for i, setting_file in enumerate(cam_setting_file_list):
            cam = CamData()
            path = fpc.findFilePath(setting_file)
            self.camdata = pd.read_csv(path, delimiter=',') # 여기에 세팅값 다들어있음
            cam.pixel_pos = self.__makePos("pix_x", "pix_y")
            cam.real_pos = self.__makePos("real_x", "real_y")
            cam.goal_pos = self.__makePos("goal_x", "goal_y")
            cam.frame_size = self.__makePos("width", "height")
            cam.stadium_size = self.__makePos("stadium_x", "stadium_y")
            self.cam_setting.append(cam)
        
        print("load cam settings succed")

    def getCamSetting(self, camnum):
        if camnum-1 >=0 and camnum-1 <= len(self.cam_setting):
            return self.cam_setting[camnum-1]
        else:
            print("wrong cam number input")
            sys.exit()

    def __makePos(self, x_name: str, y_name: str):
        x = self.camdata[x_name].to_numpy()
        x = x[~np.isnan(x)]
        x=x.reshape(-1,1)
        y = self.camdata[y_name].to_numpy()
        y = y[~np.isnan(y)]
        y=y.reshape(-1,1)
        pos = np.hstack([x, y])
        return pos