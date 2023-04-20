#Old Version Do Not Use
import cv2
import os
import csv
import pandas as pd
import sys 
import os

class FilePathCollector:
    """
    폴더 내부에 특정 확장자 명으로 작성된 파일들의 경로를 모아줌
    example code FilePath Collector

    forder_path = "F:\\bin\\Device\\Download\\11-21-30~40"
    path_collector = FilePathCollector(forder_path)
    path_collector.printFilePath()
    path_collector.changeTuneVal([0,0,0,0,0,0,1])
    path_collector.saveTuneVal()
    """
    def __init__(self, forder_path=None, findformat = ".avi",print_en = 0):
        self.filepath = []
        self.tuneval = []
        self.forder_path = forder_path
        self.csvwriter = None
        self.findformat = findformat
        if forder_path !=None:
            self.setForderPath(forder_path)
            self.dup = self.readTuneVal()

    def setForderPath(self, forder_path):
        #입력된 폴더 내의 .avi 파일 경로 배열로 리턴 및 클래스 내 변수에 추가
        self.filepath = []
        self.forder_path = forder_path
        forder = os.listdir(self.forder_path)
       
        for file in forder:
            name, ext = os.path.splitext(file)
            if ext == self.findformat: #.avi만 추출
                path = os.path.join(self.forder_path, file)
                self.filepath.append(path)
                self.tuneval.append(0)
        self.filepath.sort()
        
        return self.filepath

    def printFilePath(self):
        for i, path in enumerate(self.filepath):
            print(i, " : ", path)
    def getVideoPath(self, camnum):
        return self.filepath[camnum]
    def getAllVideoPath(self):
        return self.filepath
    def saveTuneVal(self):
        save_path = self.forder_path+'\\tune_val.csv'
        
        if self.dup:
            print("\n[Warnning] : File with same name already exsits")
            print("path : ", save_path,"\n")
            order = input("Are you sure overwrite csv file? (y/n)\n")
        else:
            order = "y"
        
        if order =="y":
            csvfile =open(save_path, 'w', newline='')
            self.csvwriter = csv.writer(csvfile, delimiter=',')
            self.csvwriter.writerow(self.tuneval)
            csvfile.close()
            print("tune file saved")
        else:
            print("Cancel file save")

    def readTuneVal(self):
        path = self.forder_path+'\\tune_val.csv'
        try:
            pandas_data = pd.read_csv(path, header = None)
            print("file read succed : ", path)
            self.tuneval = pandas_data.values.tolist()[0]
            print(self.tuneval)
            return 1
        except:
            print("[ Warning : can not find file ]\n check this path :  %s"% path)
            return 0
    def changeTuneVal(self, input_tune_list):
        self.tuneval = input_tune_list
    def findFilePath(self, findname): #특정 이름이 포함된 파일의 이름 반환
        for filename in self.filepath:
            if filename.find(findname, len(self.forder_path)) != -1:
                return filename
        print("cant find matching file : %s"%findname)
        self.printFilePath()
        sys.exit()
    def getFileName(self, filenum): #N번째 파일의 이름 반환
        if filenum<0:
            print("file number error")
            sys.exit()
            
        elif filenum > len(self.filepath)-1:
            print("file number oversize error")
            sys.exit()
        return(os.path.basename(self.filepath[filenum]))

# Test Video File Path
# filepath1 = "F:\\bin\\Device\\Download\\11-21-30~40\\08_2022-11-21_223000_224000.avi"
# filepath2 = "F:\\bin\\Device\\Download\\11-21-30~40\\07_2022-11-21_223000_224000.avi"
# filepath3 = "F:\\bin\\Device\\Download\\11-21-30~40\\06_2022-11-21_223000_224000.avi"
# filepath = "F:\\bin\\Device\\Download\\11-21-30~40\\01_2022-11-21_223000_224000.avi"


def getImage(path, frame, size=1):
    video = cv2.VideoCapture(path)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame)

    if not video.isOpened():
        print(" Could not Open %s", path)
        exit(0)

    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    ret, image0 = video.read()

    image0 = cv2.resize(image0, (int(width*size), int(height*size)))
    video.release()
    return image0

def getimages(paths, frames):
    videoplayer = []
    images =[]
    for path in paths:
        videoplayer.append(cv2.VideoCapture(path))

    for n, video in enumerate(videoplayer):
        video.set(cv2.CAP_PROP_POS_FRAMES, frames[n])
        if not video.isOpened():
            print(" Could not Open %s", paths[n])
            exit(0)
        
        width = int(videoplayer[n].get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(videoplayer[n].get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(width, height)
        ret, img = video.read()
        img = cv2.resize(img, (int(width*0.18), int(height*0.18)))
        images.append(img)
        video.release()
    return images
