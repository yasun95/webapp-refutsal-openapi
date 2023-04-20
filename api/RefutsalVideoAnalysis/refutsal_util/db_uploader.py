import json
import pymysql
import numpy as np
import math
import csv
import matplotlib.pyplot as plt
import json

import datetime
import dateutil
import pytz


class DbUploader:
    def __init__(self, host:str, port:int, user:str, password:str, db:str, uuid:str,
                left_team_color:str, right_team_color:str, goal_tag_table_name:str, heatmap_table_name:str
                ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        
        #table name
        self.goal_tag_table = goal_tag_table_name
        self.heatmap_table = heatmap_table_name
        
        self.conn = pymysql.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            password= self.password,
            db= self.db,
            charset= 'utf8'
        )
        #data val
        self.uuid = uuid
        self.left_team_color = left_team_color
        self.right_team_color = right_team_color
        self.goal_data = None #골 태그 데이터
        self.json_goal_tag = None
        self.cluster_data = None # 클러스터링 csv 읽은 결과
        self.left_team_score = 0
        self.right_team_score = 0
        
        #data format
        self.REPORT_AUX_INFO = {
            "heatmap":{
                "leftColumnTeam" : {},
                "rightColumnTeam" : {},
                "ballFromLeftSide" : {}
            },
            "attackRoute" :{
                "leftColumnTeam" : {},
                "rightColumnTeam" : {}
            },
            "heatmapBySection":{
                "leftColumnTeam" : {},
                "rightColumnTeam" : {}
            }
        }
        
    def readGoalCsv(self, file_path:str, time_gap = 10):
        #csv read
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            self.goal_data = [row for row in csv_reader]
        # 시간순 정렬
        before_tag_time = -100
        self.goal_data = sorted(self.goal_data, key=lambda x: int(x[2]) * 60 + int(x[3])) 
        now_tag_time = 0
        for tag in self.goal_data:
            now_tag_time = int(tag[2])*60+int(tag[3])
            if now_tag_time-before_tag_time < time_gap:
                self.goal_data.remove(tag)
            else:
                before_tag_time = now_tag_time
        return self.goal_data

    def makeGoalTag(self, goal_tags:list=[]) -> str:
        """
        goal_tags = [(id, team, min, sec),(id, team, min, sec)]
        미입력시 readGoalCsv()에서 읽었던 data 사용
        각팀 score 계산
        ex)(0, "Left_team", 3, 22)
        """
        self.left_team_score = 0
        self.right_team_score = 0
        if len(goal_tags) == 0:
            goal_tags = self.goal_data
        data = {}
        data['goal_tags'] = []
        for i in range(len(goal_tags)):
            data['goal_tags'].append({
                'id': i,
                'tag': goal_tags[i][1],
                'min': int(goal_tags[i][2]),
                'sec': int(goal_tags[i][3])
            })
            # 득점 추가
            if goal_tags[i][1] == "Left_team_goal":
                self.left_team_score +=1
            elif goal_tags[i][1] == "Right_team_goal":
                self.right_team_score += 1
        
        self.json_goal_tag = json.dumps(data['goal_tags'], separators=(',',':'))
        return self.json_goal_tag
    def __readClusterCsv(self, path):
        with open(path, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            self.cluster_data =  [row for row in csv_reader]
            return self.cluster_data
    def readCamSettingDb(self, court_uuid):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT COURT_AUX_INFO FROM REFUTSAL_COURT_TABLE WHERE COURT_UUID LIKE '%s'" % (court_uuid))
            data = cursor.fetchall()
            print(data)
        except:
            print("경기장 데이터 참조 실패")

    def makeHeatMap(self, csv_path, fps=30, time_min = 0, grid = (18,9), time_max = math.inf, stadium_size = (16000,8000)):
        """
        csv_path = clustering.csv #csv 파일경로
        time_min, time_max = 통계구간(min), 미지정시 전체 구간
        fps : 비디오 fps, 통계구간 미지정시 무관
        gird : tuple, 그리드 칸수 (높이 방향, 폭방향) : tuple
        stadium_size = 경기장 크기(높이방향, 폭방향)(mm) : tuple

        output = left team, rigiht team, ball
        """
        #frame/cls/playernum/
        data = self.__readClusterCsv(csv_path)
        left_team = [i for i in data if (i[3] == '1') and (time_min*fps<int(i[0])) and (int(i[0])<time_max*fps)]
        right_team = [i for i in data if i[3] == '2' and time_min*fps<int(i[0]) and int(i[0])<time_max*fps]
        ball = [i for i in data if i[1]=='32' and time_min*fps<int(i[0])and int(i[0])<time_max*fps]

        left_team_x = [int(i[4]) for i in left_team]
        left_team_y = [int(i[5]) for i in left_team]
        right_team_x = [int(i[4]) for i in right_team]
        right_team_y = [int(i[5]) for i in right_team]
        ball_x = [int(i[4]) for i in ball]
        ball_y = [int(i[5] )for i in ball]

        stadium_x = stadium_size[0]
        stadium_y = stadium_size[1]
        
        #선수, 공 상세 히트맵
        xedges = [i for i in range(-stadium_x, stadium_x, int(2*stadium_x/grid[0]))]
        yedges = [i for i in range(-stadium_y, stadium_y, int(2*stadium_y/grid[1]))]
        self.heatmap_left_team, _, _ = np.histogram2d(left_team_x, left_team_y, bins=(xedges,yedges))
        self.heatmap_right_team, _, _ = np.histogram2d(right_team_x, right_team_y, bins=(xedges,yedges))
        self.heatmap_ball, _, _ = np.histogram2d(ball_x, ball_y, bins=(xedges,yedges))
        #팀위치 기반 공격 경로
        xedges_33 = [i for i in range(-stadium_x, stadium_x, int(2*stadium_x/3))]
        yedges_33 = [i for i in range(-stadium_y, stadium_y, int(2*stadium_y/3))]
        self.heatmap_left_team_3x3y, _, _ = np.histogram2d(left_team_x, left_team_y, bins=(xedges_33,yedges_33))
        self.heatmap_right_team_3x3y, _, _ = np.histogram2d(right_team_x, right_team_y, bins=(xedges_33,yedges_33))
        #공위치 기반 공격경로
        xedges_32 = [-stadium_x, 0, stadium_x]
        yedges_32 = [i for i in range(-stadium_y, stadium_y, int(2*stadium_y/3))] #BUG i for i in range(-10, 10, 10)의 경우 마지막 수 즉 10이 포함되지 않음
        self.heatmap_ball_3x2y, _, _ = np.histogram2d(ball_x, ball_y, bins=(xedges_32,yedges_32))

        return self.heatmap_left_team, self.heatmap_right_team, self.heatmap_ball

    def rotate180(self, input_list):
        num_rows = len(input_list)
        num_cols = len(input_list[0])
        rotated_list = [[0 for _ in range(num_cols)] for _ in range(num_rows)]

        for i in range(num_rows):
            for j in range(num_cols):
                rotated_list[num_rows-i-1][num_cols-j-1] = input_list[i][j]

        return rotated_list

    def __heatmapToJson(self, heatmap, reverse=False):
        heatmap = (heatmap/np.sum(heatmap)*100)
        np.set_printoptions(precision=2)
        heatmap_list = heatmap.tolist()
        formatted_heatmap = []
        for sublist in heatmap_list:
            formatted_sublist = [float("{:.2f}".format(num)) for num in sublist]
            formatted_heatmap.append(formatted_sublist)
        if reverse: # 행열 180도 회전
            formatted_heatmap = self.rotate180(formatted_heatmap)
        return formatted_heatmap
    def __getLocalDate__(self)->str:
        date=dateutil.parser.parse(str(datetime.datetime.now(tz=pytz.utc).isoformat()))
        local_timezone = pytz.timezone('Asia/Seoul')
        local_date = date.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        return local_date.isoformat()

    def uploadHeatMapDb(self, showdata:bool=False):
        cursor = self.conn
        try:
            with self.conn.cursor() as cursor:
                # make json obj
                print(self.heatmap_ball_3x2y)
                self.REPORT_AUX_INFO["heatmap"]["leftColumnTeam"] = {'data': self.__heatmapToJson(self.heatmap_left_team)}
                self.REPORT_AUX_INFO["heatmap"]["rightColumnTeam"] = {'data': self.__heatmapToJson(self.heatmap_right_team, reverse=True)} # 수정 필요
                self.REPORT_AUX_INFO["heatmap"]["ballFromLeftSide"] = {'data': self.__heatmapToJson(self.heatmap_ball)}
                self.REPORT_AUX_INFO["attackRoute"]["leftColumnTeam"] = {'data': self.__heatmapToJson([self.heatmap_ball_3x2y[1]])} # 수정 필요
                self.REPORT_AUX_INFO["attackRoute"]["rightColumnTeam"] = {'data': self.__heatmapToJson([self.heatmap_ball_3x2y[0]], reverse=True)} # 수정 필요
                self.REPORT_AUX_INFO["heatmapBySection"]["leftColumnTeam"] = {'data': self.__heatmapToJson(self.heatmap_right_team_3x3y)}
                self.REPORT_AUX_INFO["heatmapBySection"]["rightColumnTeam"] = {'data': self.__heatmapToJson(self.heatmap_right_team_3x3y, reverse=True)} # 수정 필요
                date = self.__getLocalDate__()
                print(json.dumps(self.REPORT_AUX_INFO))
                # Insert data into table
                sql = "INSERT INTO [table_name] (MATCH_UUID, CREATED_AT, LAST_EDITED_AT, IS_DELETE, LEFT_COLUMN_TEAM_COLOR, RIGHT_COLUMN_TEAM_COLOR, LEFT_COLUMN_TEAM_SCORE, RIGHT_COLUMN_TEAM_SCORE, REPORT_AUX_INFO) VALUES (%s, %s, %s, %r, %s, %s, %s, %s, %s)"
                sql = sql.replace("[table_name]", self.heatmap_table)
                date = self.__getLocalDate__()
                cursor.execute(
                    sql,
                    (self.uuid,
                    date,
                    date,
                    False,
                    self.left_team_color,
                    self.right_team_color,
                    self.left_team_score,
                    self.right_team_score,
                    json.dumps(self.REPORT_AUX_INFO)
                    ))
                
                # Commit the changes to the database
                self.conn.commit()

                if showdata:
                    cursor.execute("SELECT * FROM %s" % self.heatmap_table)
                    result = cursor.fetchall()
                    print(result)
        finally:
            #self.conn.close()
            pass

    def uploadTagDb(self, showdata:bool = False):
        cursor = self.conn
        try:
            with self.conn.cursor() as cursor:
                # Insert data into table
                sql = "INSERT INTO [table_name] (MATCH_UUID, CREATED_AT, LAST_EDITED_AT, IS_DELETE, GOAL_TAG) VALUES (%s,%s,%s,%r,%s)"
                sql = sql.replace("[table_name]", self.goal_tag_table)
                date = self.__getLocalDate__()
                cursor.execute(sql, (self.uuid, date, date, False, self.json_goal_tag))
                
                # Commit the changes to the database
                self.conn.commit()

                if showdata:
                    cursor.execute("SELECT * FROM %s" % self.goal_tag_table)
                    result = cursor.fetchall()
                    print(result)
        finally:
            #self.conn.close()
            pass

    # SUNJONG EDIT / SAVE HEATMAP IMAGE
    def showHeatMap(self, heatmap_l, heatmap_r, heatmap_ball, save_path, extent=[-8000,8000,-16000,16000], cmap = 'hot'):
        fig = plt.figure()
        rows = 1
        cols = 3
        ax1 = fig.add_subplot(rows, cols, 1)
        #ax1.imshow(self.heatmap_left_team, cmap=cmap, extent=extent)
        ax1.imshow(heatmap_l, cmap=cmap, extent=extent)
        ax1.axis("off")
        ax1.set_title("team 1")

        ax2= fig.add_subplot(rows,cols, 2)
        ax2.imshow(heatmap_r, cmap=cmap, extent=extent)
        ax2.axis("off")
        ax2.set_title("team 2")

        ax3 = fig.add_subplot(rows, cols, 3)
        ax3.imshow(heatmap_ball, cmap=cmap, extent=extent)
        ax3.axis("off")
        ax3.set_title("ball")
        # plt.show()

        fig.savefig(save_path)