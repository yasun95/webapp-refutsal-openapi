import cv2
import os
import sys
import numpy as np
import time
import datetime
import pymysql

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from refutsal_util.file_path_collector import FilePathCollector
from refutsal_util.getImage import getImage
from refutsal_util.videowriter import videoWriter
from refutsal_util.json_config_paser import ConfigData
from refutsal_util.csv_writer import CsvWriter
def mouse_callback(event, x, y, flags, param): 
    if event == cv2.EVENT_FLAG_LBUTTON:
        print("마우스 이벤트 발생, x:", x ," y:", y) # 이벤트 발생한 마우스 위치 출력
        return x, y

class GoalDetector(FilePathCollector):
    def __init__ (self, videodir,
                host:str=None, port:int=None, user:str=None, password:str=None, db:str=None,
                cam_setting_path=None, court_uuid=None
                ):
        """
        if cam_setting_path == None:
            try:
                self.conn = pymysql.connect(
                host = host,
                port = port,
                user = user,
                password= password,
                db= db,
                charset= 'utf8'
                )
                cursor = self.conn.cursor()
                
                try:
                    cursor.execute("SELECT COURT_AUX_INFO FROM REFUTSAL_COURT_TABLE WHERE COURT_UUID LIKE '%s'" % (court_uuid))
                    data = cursor.fetchall()
                    self.cam_setting = ConfigData(str_data=data[0][0])
                except:
                    print("[error] can not find data")
                    sys.exit()
            except:
                print("[error] db connect fail")
                sys.exit()
        """
        
        # print(host)
        # print(type(host))
   
        if cam_setting_path == None:
            self.cam_setting = ConfigData(
                        host = host,
                        port = port,
                        user = user,
                        password = password,
                        db_name = db,
                        court_uuid = court_uuid
                        )

        elif cam_setting_path != None:
            self.cam_setting = ConfigData(cam_setting_path)

        super(GoalDetector, self).__init__()
        self.goalframe = [] # 골 넣은 프레임 넘버 기억
        self.goalpoints = np.empty((0,2), dtype=np.int32)
        self.goalmask = None
        #self.config_data = ConfigData(cam_setting_path)
        self.setVideoDir(videodir)

        self.videodir = videodir #인식시킬 비디오 경로
        self.videoname = None #인식시킬 비디오 이름

        self.writedir =None #클립저장할경로
        self.resize = (None, None) #분석시 압축할경우 사이즈

        #프린팅용 변수들
        self.videolength = None
        self.videofps = None
        self.video_originsize = (None, None)
        self.csv_camsetting_size =None
        self.start_time = None
    def __readCamSettingDb(self, court_uuid):
        cursor = self.conn.cursor()
        #cursor.execute("SELECT COURT_AUX_INFO FROM REFUTSAL_COURT_TABLE")
        try:
            cursor.execute("SELECT COURT_AUX_INFO FROM REFUTSAL_COURT_TABLE WHERE COURT_UUID LIKE '%s'" % (court_uuid))
            data = cursor.fetchall()
            # print(data)
        except:
            print("경기장 데이터 참조 실패")

    def setVideoDir(self, path):
        self.videodir = path
        self.setForderPath(path)
    def setWriteDir(self, path):
        self.writedir=path

    #serchVideo를 위해 어떤 동영상을 설정할지, 분석에 필요한 파라미터들 선언
    def setVideo(self, filename=None, filenum=None, camnum =1, resize=(None, None)):
        """
        폴더내 특정 비디오 선택시 세팅값 변경 적용됨
        filename or filenum 둘중 하나만 선택가능
        -goalmask
        -videoname
        -settingratio : csv에서 저장된 크기와 실제 영상의 화면 비율
        -video_h , video_w : 비디오의 화면 사이즈
        -setting_frame_h, setting_frame_w : csv 파일에 저장된 값의 화면 사이즈
        """
        if filename !=None and filenum !=None:
            print("setVideo() function should be choose one option in filename or filenum")
        elif filename !=None: #폴더내 파일명으로 파일 선택
            self.videoname = filename
            #print("\n==== Set New Video [%s] ===="%self.videoname)
        elif filenum !=None: #폴더내 파일 넘버로 파일 선택
            self.videoname = self.getFileName(filenum)
            #print("\n==== Set New Video [%s] ===="%self.videoname)
        else:
            print("setVideo() function should be choose one option in filename or filenum")
        
        if str.isdigit(self.videoname[:2]): #파일명 첫 2글자가 숫자인경우 camnumber로 인식
            self.camnum = int(self.videoname[:2])
            #print("detect cam number : %d"%self.camnum)
        else:
            print("detect cam number : Fail")
            print("\n[Warring] Fail to detect cam number")
            self.camnum = camnum # 캠넘버 인식 안됬을때 
        if self.cam_setting.camdata[self.camnum] == None:
            print(self.camnum," is empty, chedck config file!!!!!!!!!!!!!")
        self.resize =resize
        path = os.path.join(self.videodir, self.videoname)
        cap = cv2.VideoCapture(path)

        self.videolength = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.videofps = cap.get(cv2.CAP_PROP_FPS)
        self.video_originsize = (cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.__calSettingRatio()
        self.goalpoints = self.cam_setting.camdata[self.camnum].goal_points
        if len(self.goalpoints) <4 :
            return False
        self.goalpoints = self.goalpoints*self.setting_ratio
        self.goalpoints = self.goalpoints.astype(np.int32)
        self.setgoalmask(opt="load_csv")
        return True

    #화면비율을 변경하거나, 카메라 세팅시 적용한 화면 사이즈가 다른경우 이를 계산
    def __calSettingRatio(self):
        if self.resize ==(None,None):
            #print("set Origin size")
            path = os.path.join(self.videodir, self.videoname)
            img = getImage(path, 100)
            self.video_h,self.video_w,d=np.shape(img)
            #print("set video size : ",self.video_h,"*",self.video_w)
        else:
            #print("set resize")
            self.video_w, self.video_h = self.resize

        setting_frame = [self.cam_setting.camdata[self.camnum].cali_frame_width,self.cam_setting.camdata[self.camnum].cali_frame_height]
        self.setting_frame_w = 1024
        # int(self.cam_setting.camdata[self.camnum].cali_frame_width)
        self.setting_frame_h = 576
        # int(self.cam_setting.camdata[self.camnum].cali_frame_height)

        #print("cam setting size", setting_frame[0][0], "*",setting_frame[0][1])
        self.csv_camsetting_size = setting_frame

        if self.video_h/self.setting_frame_h == self.video_w/self.setting_frame_w:
            self.setting_ratio = self.video_h/self.setting_frame_h
            #print("setting frame ratio = %f"%self.setting_ratio)

        else:
            print("[Error] Frame ratio Error")
            sys.exit()
    
    #골대 영역 ROI를 마스크로 만듬
    def setgoalmask(self, ratio = 1, opt="set"):
        """
        opt = "set" : 직접 드래그로 설정
              "default" : 코드에 박힌 임시값
              "load_csv" : csv read값 사용
        """
        if opt =="set":
            path = os.path.join(self.videodir, self.videoname)
            self.goalpoints = np.array([])
            img = getImage(path, 100)
            #img = cv2.resize(img, (1024,576))
            while True:
                x, y, w, h = cv2.selectROI(img)
                print(x, y)
                if(x==0 and y==0): 
                    break
                img = cv2.circle(img, (x,y), 3,(255,0,0),3)
                pos = np.array([x,y])
                
                self.goalpoints = np.append(self.goalpoints, np.array([pos], dtype=np.int32),axis=0)
            print("reset goal points : ",self.goalpoints)
        elif opt =="default":
            self.goalpoints = np.array(
                [[916, 249],
                [952, 252],
                [942, 121],
                [923,   2],
                [879,   1],
                [903,  67]]
                , dtype=np.int32)
        elif opt =="load_csv":
            #print("cam setting : [cam%d]"%self.camnum)
            pass
        elif opt =="read":
            path = os.path.join(self.videodir, self.videoname)
            self.goalpoints = np.array([])
            img = getImage(path, 100)
            img = cv2.resize(img, (1024, 576))
            cv2.imshow("image", img)
            cv2.setMouseCallback('image', mouse_callback)
            while True:
                cv2.imshow("image", img)
                k = cv2.waitKey(1)& 0xFF
                if k ==27:
                    break
                

        else:
            print("wrong opt value : %s"%opt)
        if self.resize == (None, None):
            blank = np.zeros((int(self.setting_frame_h*self.setting_ratio),int(self.setting_frame_w*self.setting_ratio)), dtype=np.uint8) # 영상크기에 맞게 수정 필요
        else:
            blank = np.zeros((int(self.resize[1]),int(self.resize[0])), dtype=np.uint8) # 영상크기에 맞게 수정 필요
        #print(self.goalpoints)
        self.goalmask = cv2.fillConvexPoly(blank,self.goalpoints,255)

    # Sunjong make for earn to the progress. 
    #동영상에서 지속적으로 프레임을 가져오면서 골이 감지된 프레임을 탐색
    def serchVideo(self, analyze_progress=0, imgshow=False, color_filter = None):
        path = os.path.join(self.videodir, self.videoname)
        #print(" - serch File : %s"%path)
        
        cap = cv2.VideoCapture(path)

        self.fps = cap.get(cv2.CAP_PROP_FPS)
        if not cap.isOpened():
            print('Video open failed!')
            sys.exit()
        elif self.resize != (None, None):
            pass
        elif self.goalmask.shape[1]!= cap.get(cv2.CAP_PROP_FRAME_WIDTH) or self.goalmask.shape[0]!=cap.get(cv2.CAP_PROP_FRAME_HEIGHT):
            print("goal mask size is not same width input stream")
            print("- input video size = ",(cap.get(cv2.CAP_PROP_FRAME_HEIGHT), cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
            print("- input mask       = ", self.goalmask.shape)
            sys.exit()
        
        bs = cv2.createBackgroundSubtractorKNN()
        bs.setDetectShadows(False)
        frame_cnt = 0
        self.goal_detect_frame =[]
        #시작 프레임 임의 설정
        #cap.set(cv2.CAP_PROP_POS_FRAMES, 8800)
        self.start_time = time.time() #분석 시작시간 기록
        while True:
            if(frame_cnt%15==0):
                self.__progressbar(frame_cnt)
                
            ret, frame = cap.read()
            
            frame_cnt+=1
            if not ret:
                break
            if self.resize !=(None, None):
                frame = cv2.resize(frame, self.resize, interpolation=cv2.INTER_NEAREST)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_goal = cv2.bitwise_and(gray, gray, mask=self.goalmask)
            # fgmask = 0, 128, 255 3가지값
            # 128 = 그림자
            fgmask = bs.apply(gray_goal)

            #모폴로지 침식
            k=cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            #fgmask = cv2.erode(fgmask, k)
            fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, k)
            fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_DILATE, k)
            ret, binmask = cv2.threshold(fgmask,250,255, cv2.THRESH_BINARY)
        
            if color_filter != None:
                mask_frame = cv2.bitwise_and(frame, frame, mask = binmask)
                mask_frame = cv2.cvtColor(mask_frame, cv2.COLOR_BGR2HSV)
                if color_filter == 'yellow':    
                    lower_fillter = (5, 45, 60)
                    upper_fillter = (60, 220, 240)
                mask_frame = cv2.inRange(mask_frame, lower_fillter, upper_fillter)

            # 학습된 배경 출력
            #back = bs.getBackgroundImage()
                cnt, _, stats, _ = cv2.connectedComponentsWithStats(mask_frame)
            else:
                cnt, _, stats, _ = cv2.connectedComponentsWithStats(fgmask)

            for i in range(1, cnt):
                (x,y,w,h, area) = stats[i]

                x = int(x/self.setting_ratio)
                y = int(y/self.setting_ratio)
                w = int(w)
                h = int(h)
                area = int(area)
                if self.checkball(w, h, area, color_filter=color_filter):
                    self.goal_detect_frame.append(frame_cnt)
                    if imgshow:
                        #print("detect ", frame_cnt)
                        #print(x, y, w, h, area)
                        cv2.circle(frame, (int((x+int(w/2))*self.setting_ratio),int((y+int(h/2))*self.setting_ratio)), 15,(0,0,255), 3)
                        cv2.imshow("frame", frame)
                        cv2.imshow("roi", fgmask)
                        #cv2.imshow("mask_frame", mask_show_frame)
                        #cv2.waitKey(0)
            #cv2.imshow('frame', frame)
            #cv2.imshow('back', back)
            #cv2.imshow('fgmask', fgmask)

            if imgshow:
                #cv2.imshow("mask_frame", mask_frame)
                #cv2.imshow("roi", fgmask)
                if color_filter ==None:
                    mask_show_frame = cv2.bitwise_and(frame, frame, mask = binmask)
                    cv2.imshow("mask_frame", mask_show_frame)
                else:
                    cv2.imshow("mask_frame", mask_frame)
                frame = cv2.polylines(frame, [self.goalpoints], True, (255,0,0))
                cv2.imshow('frame', frame)
                cv2.imshow("roi", fgmask)
                
                if cv2.waitKey(1) == ord('q'):
                    break
        #print("detect frame")
        #print(self.goal_detect_frame)
        cap.release()

    #골 감지 프레임중 중복된 데이터 삭제 
    def remapFrame(self, ignore_time):
        ignore_frame = ignore_time*self.fps
        last_frame = -1000
        i=0

        while len(self.goal_detect_frame)>i:
            if self.goal_detect_frame[i]-last_frame<ignore_frame:
                last_frame = self.goal_detect_frame[i]
                del self.goal_detect_frame[i]
            else:
                last_frame = self.goal_detect_frame[i]
                i+=1
        if len(self.goal_detect_frame) !=0: #초반10 프레임 이전 노이즈 무시        
            if self.goal_detect_frame[0]<10:
                del self.goal_detect_frame[0]
        #print(self.goal_detect_frame)
        print("\n","[analysis end]")
        
        if len(self.goal_detect_frame):
            header = "{0:_^60}"
            line = "{0:^10}|{1:^49}"
            print(header.format("[Goal time table]"))
            for i, time in enumerate(self.goal_detect_frame):
                sec= int(time/self.fps%60)
                min= int(time/self.fps//60)
                print(line.format("goal "+str(i+1), str(min)+"min "+str(sec)+"sec"))
                
        else:
            print("[Goal didn't detected]")
    def getResult(self):
        return self.goal_detect_frame
    def getVideoTime(self):
        return self.videolength/self.videofps
    def makeClip(self, ask=False):
        make_clip = 'y'
        if ask:
            make_clip = input("make clip? (y/n) : ")
        
        if make_clip =='y'or make_clip =="Y":
            vm =videoWriter()
            vm.setOriginVideo(self.videodir, self.videoname) # 원본 영상 지정
            vm.setWritePath(self.writedir) #클립 저장경로 변경가능
            vm.setTimeMargin(5,5) #클립 마진 앞으로 5초 뒤로 5초 클립

            for goal_number, goal_frame in enumerate(self.goal_detect_frame):
                vm.makeClip(goal_frame, goal_number)
            
            header2 ="{0:-^60}"
            print(header2.format("maked %d clips"%len(self.goal_detect_frame)))
    def makeOutputCsv(self, make_csv:bool=True):
        """
        
        """
        # print(make_csv)
        print(self.writedir)
        self.cw = CsvWriter(
            make_csv=True, 
            csv_path=self.writedir
            )
        self.cw.makeOutputForder(
            outputpath=self.writedir,
            filename='goal_tag.csv',
            fieldnames=['camnum','team', 'min', 'sec'])

    def writeData(self):
        self.cw.openCsv()
        for frame in self.goal_detect_frame:
            print(self.videofps)
            sec = (frame//self.videofps)%60
            min = (frame//self.videofps)//60
            self.cw.writerowCsv([self.camnum, self.cam_setting.camdata[self.camnum].add_score+"_goal", int(min), int(sec)])
            #self.cam_setting.camdata[self.camnum].cali_frame_height
        pass

    #감지된 컨투어가 공인지 확인
    def checkball(self, w, h, area, color_filter =None):
        #ball_check_setting at frame height : 1440*576
        if color_filter == None:
            if(area<100) or (area>300):
                return 0
            #print (w, h, area)
            if w>60 or h> 60:
                return 0
            if w<10 or h< 10:
                return 0
            ratio = w/h
            if ratio < 0.6 or ratio>1.8:
                return 0
            if area/(w*h)>0.4:
                return 1
            return 0
        else:
            if(area<30) or (area>300):
                return 0
            #print (w, h, area)
            if w>60 or h> 60:
                return 0
            if w<5 or h< 5:
                return 0
            ratio = w/h
            if ratio < 0.4 or ratio>2:
                return 0
            if area/(w*h)>0.4:
                return 1
            return 0    

    
    def printChart(self):
        header ="{0:^60}"
        header2 ="{0:-^60}"
        cht_1="{0:<20}|{1:>39}"
        print("\n",)
        print(header2.format(""))
        print(header.format(self.videodir))
        print(header2.format(self.videoname))
        print(cht_1.format("Video name",self.videoname) )
        print(cht_1.format("camera number","cam"+str(self.camnum)) )
        print(cht_1.format("origin video size",str(int(self.video_originsize[0]))+"*"+str(int(self.video_originsize[1])) ))
        if self.resize !=(None, None):
            print(cht_1.format("resize video size",str(int(self.resize[0]))+"*"+str(int(self.resize[1]))))
        else:
            print(cht_1.format("resize video size", "Not Used"))
        print(cht_1.format("csv standard size",str(int(self.setting_frame_w))+"*"+str(int(self.setting_frame_h))))
        print(cht_1.format("resize ratio",self.setting_ratio))
        print(cht_1.format("video frame count", str(self.videolength)+" frame"))

        sec = self.videolength/self.videofps #비디오 영상 길이 계산(전체 프레임수 / 영상 FPS)
        hour = int(sec//3600)
        min = int(sec//60-hour*60)
        sec = int(sec%60)
        print(cht_1.format("video play time", str(hour)+":"+str(min)+":"+str(sec)))
        print(cht_1.format("video fps", self.videofps))
        print(header2.format(""))
    def __progressbar(self, framecount):
        barformat ="{0:░<50}{1:<4}{2:>5}"
        progress = int(framecount/self.videolength*100)
        bar = "█"*int(progress/2)
        runtime = int(time.time()-self.start_time) 
        runtime_split = str(datetime.timedelta(seconds=runtime)).split(".")
        print(barformat.format(bar, str(progress)+"%",runtime_split[0]), end ="\r")    