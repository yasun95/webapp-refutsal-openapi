import json
import numpy as np
import sys
import pymysql
from dataclasses import dataclass


@dataclass
class CamData():
    cali_frame_width = None
    cali_frame_height = None
    frame_points = None
    real_points = None
    goal_points = None
    ignore_points = None
    add_score = None

class ConfigData(CamData):
    stadium_uuid = None
    stadium_name = None
    stadium_width = None
    stadium_height = None
    camdata = []
    
    def __init__(self, 
                 json_path= None, #mode 1 / read data on json config file
                 str_data = None, #mode 2 / read data on string
                 host = None,   # mode 3 / read data on db
                 port = None,   # mode 3 / read data on db
                 user = None,   # mode 3 / read data on db
                 password = None,  # mode 3 / read data on db
                 db_name = None,  # mode 3 / read data on db
                 court_uuid = None  # mode 3 / read data on db
                 ):
        camdata = []
        cam_name_list = ['cam1','cam2','cam3','cam4','cam5','cam6','cam7','cam8']
        if json_path != None:
            with open(json_path, 'r') as file:
                data = json.load(file)


        elif str_data != None:
                alldata = json.loads(str_data)
                data=alldata["cameraSetting"]

        elif host != None:
            # Print The DB Info
            # print(host)
            # print(port)
            # print(user)
            # print(password)
            # print(db_name)
            # print(court_uuid)
             try:
                self.conn = pymysql.connect(
                host = host,
                port = port,
                user = user,
                password= password,
                db= db_name,
                charset= 'utf8'
                )
                cursor = self.conn.cursor()
                try:
                    cursor.execute("SELECT COURT_AUX_INFO FROM REFUTSAL_COURT_TABLE WHERE COURT_UUID LIKE '%s'" % (court_uuid))
                    data = cursor.fetchall()
                    str_data=data[0][0]
                    alldata = json.loads(str_data)
                    data=alldata["cameraSetting"]

                except:
                    print("[error] can not find data")
                    sys.exit()
             except:
                print("[error] db connect fail")
                sys.exit()
        else:
            print("[error] no parameter")
            sys.exit()
    
        self.stadium_uuid = data['uuid'] # 수정 필요
        self.stadium_name = data['name'] #수정 필요
        self.stadium_width = alldata["courtSize"]['width']
        self.stadium_height = alldata["courtSize"]['height']
        self.cam_data = []
        cam = CamData()

        self.camdata.append(cam)
        for camname in cam_name_list:
            cam = CamData()
            cam.cali_frame_width = data[camname]['frame_size']['width']
            cam.cali_frame_height = data[camname]['frame_size']['height']
            calibration_points = data[camname]['calibration_points']
            goal_points = data[camname]['goal_points']
            cam.frame_points=np.float32([[frame['frame_x'], frame['frame_y']] for frame in calibration_points])
            cam.real_points = np.float32([[real['real_x'], real['real_y']] for real in calibration_points])
            cam.goal_points = [[float(goal['x']), float(goal['y'])] for goal in goal_points]
            cam.goal_points = np.float32([[(goal['x']), (goal['y'])] for goal in goal_points])
            cam.add_score = data[camname]['add_score']
            ball_ignore_point = data[camname]['ball_ignore_point']
            cam.ignore_points = [np.float32([ig_point['x'], ig_point['y']]) for ig_point in ball_ignore_point]
            
            self.camdata.append(cam)
    def __str__(self):
        header1 = "{0:<50}\n"
        header2 = "{2:<10}{0:<10}:{1:<49}\n"
        
        output = (
            (header1.format(self.stadium_name+" stadium"))+
            header2.format("uuid",self.stadium_uuid,"")+
            header2.format("height",self.stadium_height,"")+
            header2.format("width",self.stadium_width,"")
        )
        return output
