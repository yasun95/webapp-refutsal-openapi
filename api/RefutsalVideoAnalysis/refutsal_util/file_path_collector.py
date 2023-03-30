
import os
import csv
import pandas as pd
import sys 
import os

class FilePathCollector:
    """
    폴더 내부에 특정 확장자 명으로 작성된 파일들의 경로를 모아줌
    example code - FilePath Collector

    forder_path = "F:\\bin\\Device\\Download\\11-21-30~40"
    path_collector = FilePathCollector(forder_path)
    path_collector.printFilePath()
    """
    def __init__(self, forder_path=None, findformat = ".avi",print_en = 0):
        self.filepath = []
        self.forder_path = forder_path
        self.csvwriter = None
        self.findformat = findformat
        if forder_path !=None:
            self.setForderPath(forder_path)

    def setForderPath(self, forder_path):
        #입력된 폴더 내의 .avi 파일 경로 배열로 리턴 및 클래스 내 변수에 추가
        self.filepath = []
        self.forder_path = forder_path
        forder = os.listdir(self.forder_path)
       
        for file in forder:
            name, ext = os.path.splitext(file)
            if ext == self.findformat: #.avi만 추출
                #path = self.forder_path+'\\'+file
                path = os.path.join(self.forder_path, file)
                #print(path)
                self.filepath.append(path)
        self.filepath.sort()
        
        return self.filepath

    def printFilePath(self):
        header ="{0:-^60}"
        header2 ="{0:^60}"
        index ="{0:^15}|{1:^45}"
        line = "{0:^15}|{1:>44}"
        print(header.format(""))
        print(header2.format(self.forder_path))
        print(header.format(""))
        print(index.format("file number", "file path"))
        for i, path in enumerate(self.filepath):
            print(line.format(i, os.path.basename(path)))
        print(header.format(""))
        
    def getVideoPath(self, camnum):
        return self.filepath[camnum]
    def getAllVideoPath(self):
        return self.filepath
    def findFilePath(self, findname): #디렉토리 내 특정 이름을 포함하는 파일의 경로 반환
        for filename in self.filepath:
            if filename.find(findname, len(self.forder_path)) != -1:
                return filename

        print("cant find matching file : %s"%findname)
        self.printFilePath()
        sys.exit()
    def getFileName(self, filenum): #디렉토리 내 N번째 파일의 경로 반환
        if filenum<0:
            print("file number error")
            sys.exit()
            
        elif filenum > len(self.filepath)-1:
            print("file number oversize error")
            sys.exit()
        return(os.path.basename(self.filepath[filenum]))
