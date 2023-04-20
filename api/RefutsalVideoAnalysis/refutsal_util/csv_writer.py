import csv
import numpy as np
import os

class CsvWriter:
    """
    Clustering 후 CSV 파일 작성해주는 클래스
    CSV 파일을 한번에 저장하는것이 아닌 한 프레임씩 기록하기때문에 
    저장폴더 생성 / csv생성 및 열기 / 쓰기  / 닫기 함수가 각각 따로 있음

    위 순서대로 실행시키고 쓰기만 작성할 프레임 수 만큼 돌리면 됨
    
    """
    def __init__(self, make_csv=False, csv_path='D:\library\yolov5-master\\runs\\testcsv'):
        self.makeCsv = make_csv
        self.csv_path = csv_path
        self.csv_files =[]
        self.forder_path = None
        self.now_forder = os.getcwd()
        self.outputfolder = None
        self.outputfile = None
        self.wr = None #csv writer
        self.make_csv = make_csv
        self.f = None
        
    def makeOutputForder(self, outputpath=None, fordername ='\\output', filename = 'output.csv', fieldnames = ['dataA', 'dataB', 'dataC']):
        #실행파일의 경로에 폴더( /output )생성
        if outputpath == None:
            outputpath = os.path.dirname(os.path.abspath(__file__))

        self.outputfolder = outputpath
        self.outputfile = filename

        #만약 폴더가 없으면 생성 있으면 그대로 사용
        if not os.path.exists(self.outputfolder):
            os.mkdir(self.outputfolder)

        if self.make_csv == True:#헤더 생성
            with open(os.path.join(self.outputfolder,filename),'w', newline='') as outcsv:
                header_wr = csv.DictWriter(outcsv, fieldnames)
                header_wr.writeheader()

    def openCsv(self, mode='a'):
        if self.make_csv == True:
            save_path = os.path.join(self.outputfolder, self.outputfile)
            self.f = open(save_path,mode, newline='') # csv 파일 생성 w: write, a: append
            self.wr = csv.writer(self.f, delimiter=',')
    def writerowCsv(self, data):
        if self.make_csv == True:
            csv_data = np.column_stack(data)
            for line in csv_data:
                self.wr.writerow(line)
                print(line)
    def closeCsv(self):
        if self.make_csv:
            self.f.close()