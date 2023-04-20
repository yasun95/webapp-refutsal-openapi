import pandas as pd
import time
import math
import statistics
import seaborn as sns
import matplotlib.pyplot as plt
from refutsal_util.csv_writer import CsvWriter
from refutsal_util.csv_reader import CsvReader

class RefutsalCluster(CsvReader, CsvWriter):
    """
    동일 시간 다양한 각도에서 촬영한 여러개의 프레임에서 인식한 좌표(csv)를 입력
    여러 csv 파일을 통합하여 하나의 csv파일로 출력
    """
    def __init__(self,  print_en=0):
        CsvReader.__init__(self, print_en)
        CsvWriter.__init__(self, make_csv=True)
        self.origindata = pd.DataFrame(index=range(0), columns=['frame', 'camnum', 'id', 'team', 'cls', 'x', 'y'])
        self.dismat = []
        self.datasize = 0
        self.cluster_tree = []
        self.print_en = print_en
        self.disdict = {}
        self.group_data = []
        self.debug = False
        self.maxcamnum = 4

        self.Timer = [0,0,0,0,0]
        self.start_time = 0

    def timerStart(self):
        self.start_time = time.time()
    def timerStop(self, timernum):
        self.Timer[timernum]+= (time.time()-self.start_time)
        
    def printTimer(self):
        print("0: cluster() 1:updateFrame() 2:makeDict() ")
        print(self.Timer)

    def updateFrame(self):
        """
        csv reader 클래스 이용해서 여러 파일에서 한 프레임 씩 가져오기
        가져온 프레임은 self.origindata에 pandas DataFrame 형태로 저장
        """
        print("last_frame : ",self.last_frame)
        print(self.last_row)
        self.timerStart()

        #before get new frame init all data
        self.group_data = []
        self.disdict = {}
        self.cluster_tree = []
        self.datasize = 0
        self.dismat = []
        self.origindata = pd.DataFrame(index=range(0), columns=['frame', 'camnum', 'id', 'team', 'cls','x', 'y'])

        # Skip the frame
        skip_time = 20
        for i in range(skip_time):
            self.origindata = self.readFrame()
  
        self.timerStop(1)
        if self.getStauts():
            self.data_size = len(self.origindata)
            for i in range(len(self.origindata)):
                self.group_data.append([int(i)])
            return True
        else:
            return False #데이터 끝

    def __calRefutsalDistance(self, X, Y):
        """
        클러스터링을 위해 두 데이터간 유사도 거리를 계산하는 함수
        """
        camnum1 = X.camnum
        team1 = X.team
        id1=X.id
        cls1 = X.cls
        x1=X.x
        y1=X.y

        camnum2=Y.camnum
        team2=Y.team
        id2=Y.id
        cls2 =Y.cls
        x2=Y.x
        y2=Y.y
        
        if(camnum1==camnum2): #cam number에 대한 보상 (같은 카메라의 대상끼린 군집X)
            dis = 1000
            return dis
        if((cls1 != cls2)): # 인식된 라벨이 다르면 군집 X
            dis = 1001
            return dis

        dis = math.sqrt((x1-x2)**2 + (y1-y2)**2)

        if((team1 != 0)&(team2!=0)): # team type 에 대한 거리보상(팀이다르면 군집 X)
            if(team1 == team2):
                dis = dis*0.5
            else:
                dis = 999
        return dis

    def makeDisMat(self):
        """
        makeDict와 같은 기능 But 더느림/ 시각화 가능
        두데이터간 거리를 프레임내 모든 데이터에 대해 계산하여 행렬을 만드는 함수
        시간 복잡도가 n^2이기때문에 막쓰면 안되는 함수임 넣는 데이터의수가 많으면 좋지 몬함
        """
        X = self.origindata
        Y = self.origindata
        self.dismat = []
        for idx, rowx in X.iterrows():
            self.dismat.append([])
            for idy, rowy in Y.iterrows():
                if idx == idy:
                    self.dismat[idx].append(0)
                elif idx> idy:
                    self.dismat[idx].append(self.dismat[idy][idx])
                else:
                    self.dismat[idx].append(int(self.__calRefutsalDistance(rowx, rowy)))
        return self.dismat
    def showDisMat(self):
        sns.heatmap(self.dismat, annot=False)
        plt.show(block=False)
        plt.pause(10000)
        plt.close()
    def getDisMat(self):
        return self.dismat
    def makeDict(self):
        """
        makeDisMat과 동일한 기능 But 더 빠름
        거리행렬에서 나온 모든 거리값을 정렬하여 Dictionary 형태로 변경
        ex) distance, (data1, data2)
        Dictinary를 정렬해서 추후 거리가 가까운 데이터 끼리 그룹화 진행
        """
        self.timerStart()
        self.disdict = {}
        X = self.origindata
        Y = self.origindata
        #iterrow 쓸때보다 itertuples가 8배 빠름
        idx = 0
        for rowx in X.itertuples():
            idy = 0
            for rowy in Y.itertuples():

                if idx > idy: 
                    pass
                elif rowx.camnum == rowy.camnum: #카메라 넘버 같으면 계산 X
                    pass
                elif rowx.cls != rowy.cls: #인식된 객체 다르면 계산 X
                    pass
                else:
                    self.disdict[idx, idy] = self.__calRefutsalDistance(rowx, rowy) 
                                    
                idy+=1
            idx +=1
    
        #거리행렬 정렬
        self.disdict = sorted(self.disdict.items(), reverse=False, key = lambda item:item[1])
        if self.print_en >= 1:print("disdict size : ", len(self.disdict))
        
        if self.debug: print(self.disdict)

        graph_list = []
        for data in self.disdict:
            graph_list.append(data[1])

        self.timerStop(2)

    def _find(self, val):
        """
        player data가 groupdata들중 어디 들어있는지 찾아주는 함수
        ex) self.group_data = [[0,7],[1],[2],[3],[4],[5,6]]
            self._find(3) -> 3
            self._find(7) -> 0
        """
        for i, row in enumerate(self.group_data):
            if len(row)==1:
                if row[0] == val:
                    return i
            else:
                for j in range(len(row)):
                    #print(j, row)
                    if row[j] == val:
                        return i
        print("!! can not find data !!")
    def _checkCamnumOverlap(self, id1, id2):
        """
        두 그룹(id1 id2) 내 player의 origindata 접근해서 두그룹간 겹치는 camnum 이 있는지 확인 
        return 0 : 중복 없음
        return 1: 중복 발견
        """
        temp = self.group_data[id1]+ self.group_data[id2]
        camnum = []

        for player in temp:
            camnum.append(self.origindata.iloc[player].camnum)
        if len(camnum) == len(set(camnum)): #중복 체크
            return 0 #중복없음
        else:
            return 1 #중복있음
    def _checkTeamOverlap(self, id1, id2):
        """
        두 그룹(id1 id2) 내 player의 origindata 접근해서 두그룹간 상반된 team label 이 있는지 확인 
        return 0 : 상관 없음
        return 1: 상반된 팀 발견
        """
        temp = self.group_data[id1]+ self.group_data[id2]
        team_labels = []

        for player in temp:
            team_labels.append(self.origindata.iloc[player].team)
        if 1 in team_labels:
            if 2 in team_labels:
                #상반 있음
                return 1
        else:
            #상반 없음
            return 0

    def _combine(self, id1, id2):
        """
        2개의 group_data를 합쳐주는 함수
        ex) self.group_data = [[0],[1],[2],[3],[4],[5,6]]
            self.combine(0, 3)
            
            self.group_data : [[0,3],[1],[2],[4],[5,6]]
        """
        if(id1 == id2):
            return
        temparr = self.group_data[id1] + self.group_data[id2] 
        if self.print_en>=2:print("temp : ", temparr)
        self.group_data.insert(id1, temparr)
        del self.group_data[id1+1]
        del self.group_data[id2]

    def __findMode__(self, list):
        if len(list) == 0:
            return 0
        return statistics.mode(list)

    def calMeanPos(self, idxarr): #그룹데이터 인덱스 들고오면 그룹끼리 평균내줌
        sum_x = 0
        sum_y = 0
        team_labels = []
        id_labels = []
        for player in idxarr:
            #player의 csv 원본 정보는  
            #self.origindata.iloc[player].x -> x라벨 데이터 요런식으로 
            if self.print_en >=2:
                print(self.origindata.iloc[player])
            sum_x +=self.origindata.iloc[player].x
            sum_y +=self.origindata.iloc[player].y
            cls = self.origindata.iloc[player].cls
            
            if self.origindata.iloc[player].team != 0:
                team_labels.append(self.origindata.iloc[player].team)

            if self.origindata.iloc[player].id != 0:
                team_labels.append(self.origindata.iloc[player].id)

        frame = self.last_frame-1
        meanX = int(sum_x/len(idxarr))
        meanY = int(sum_y/len(idxarr))

        team = self.__findMode__(team_labels)
        id = self.__findMode__(id_labels)
        group = len(idxarr)
        if self.print_en >=1: # 매칭 결과
            print("frame :", frame)
            print("assemble array :", idxarr)
            print("meanpos : ", meanX, meanY) 
            print("team : ", team) 
            print("id : ", id)
            print("cls : ", cls)
            print("-----------------------------------")

        outputarr = [frame, cls, id, team, meanX, meanY, group]
        return outputarr
    
    def cluster(self, epoch=None, distance=None, leave_player=None, csv_write=False):
        """
        epoch: 결합 수
        distance : 최대 결합거리
        leave_player : 남길 오브젝트 수
        """
        self.timerStart()
        self.cluster_tree.append(self.group_data[:])
        if self.print_en >=2:
            print("init_tree: ")
            print(self.cluster_tree[:])
        

        i = 0
        
        for match in self.disdict: 
            #disdict : 거리 행렬을 거리순으로 정렬해둔것
            #즉 거리가 낮은 순서쌍(match)부터 순서대로 호출됨
            #match형식 (distance, (row1, row2))
            id1 = self._find(match[0][0])
            id2 = self._find(match[0][1])
            if self.print_en >=2: print(id1,":",match[0][0], "<-", id2,":",match[0][1])

            # 클러스터링 조건 체크 (그룹화 했을때 데이터 수가 9개 이하인지)
            # 그룹내에 같은 카메라 넘버가 없는지
            temparr = self.group_data[id1] + self.group_data[id2]
            if(id1 == id2):
                pass
            elif(len(self.group_data[id1])+len(self.group_data[id2])) > self.maxcamnum: #클러스터링 했을때 수가 카메라 수보다 커지면 클러스터링X
                pass
            elif self._checkCamnumOverlap(id1, id2): #중복된 카메라 있는지 체크
                pass
            elif self._checkTeamOverlap(id1, id2):
                pass
            else:
                self._combine(id1, id2)
                temp = self.group_data[:]
                self.cluster_tree.append(temp)

            if(self.print_en >= 2):
                print("n =",len(self.group_data))
                print(self.group_data)
                print("-----------------------------------------------")
            #clustering 종료 시점 컨트롤
            i+=1
            if epoch!=None: #매칭 횟수 반영 exit
                if i>epoch :
                    break
            if distance!=None: # 거리 반영 매칭 exit
                if self.print_en >=2:print("dis : ", match[1])
                if match[1] > distance: break
            if leave_player!=None: # 남은 객체 수 반영 매칭 exit
                if self.print_en >=2:print("object count : ",len(self.group_data) ,"/",leave_player )
                if leave_player >= len(self.group_data):
                    print(self.group_data)############
                    break
            
            #combine_group 
        if self.print_en >=1: #클러스터링 (프레임별)결과 출력
            print("count: ", len(self.group_data), " object")
            print("group data : ",self.group_data)
            print("----------------------------------------")
        
        for group in self.group_data:
            self.writerowCsv(self.calMeanPos(group))
        self.timerStop(0)