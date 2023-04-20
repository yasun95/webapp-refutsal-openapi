import os
import pandas as pd
import csv
import time


class CsvReader: 
    """
    CSV 파일 읽어다주는 클래스
    읽을 파일 경로 지정 방법:
        addfilePath   : 파일명으로 읽어오는 방법
        addForderPath : 디렉토리내 모든 csv 파일을 읽어주는 방법
    파일 읽는 방식:
        csv 파일 8개를 읽어오기 때문에 용량이 너무큼
        때문에 한프레임씩 읽어옴
        readFrame : 실행시 현재 저장된 프레임 지우고, 다음프레임을 읽어옴
                    읽어온 프레임은 self.nowDF 라는 이름으로 pandas Data Frame 형태로 저장
    데이터 참조 : 
        readDF

    """
    def __init__(self, print_en=0, output_colums=['frame', 'camnum', 'id', 'team', 'cls', 'x', 'y']):
        self.filepath =[]
        self.dfarr=[]
        self.last_row =[]
        self.last_frame = 1
        self.once_read_row = 25
        self.nowDF = pd.DataFrame(index=range(0), columns=['frame', 'camnum', 'id', 'team', 'cls', 'acc', 'x', 'y'])
        self.enable = True
        self.print_en = print_en
        self.forder_path = []
        self.output_colums = output_colums
        self.nextframe = 1 #[hot fix]

        self.fake_df = pd.DataFrame()
        self.fake_df['frame']=[self.last_frame]
        self.fake_df['camnum'] = [9]
        self.fake_df['id'] = [0]
        self.fake_df['team'] = [0]
        self.fake_df['cls']=[0]
        self.fake_df['x'] = [-10000000]
        self.fake_df['y'] = [-10000000]

    def getStauts(self):
        return self.enable

    def addFilePath(self, inputpath):
        self.filepath.append(inputpath)
        self.last_row.append(1)

    def addForderPath(self, forder_path):
        #입력된 폴더 내의 .csv 파일 경로 배열로 리턴 및 클래스 내 변수에 추가
        self.forder_path = forder_path
        forder = os.listdir(self.forder_path)
       
        for file in forder:
            name, ext = os.path.splitext(file)
            if ext == '.csv': #csv만 추출
                path = self.forder_path+'/'+file
                self.filepath.append(path)
                self.last_row.append(1)

        print(self.filepath)
        return self.filepath

    def readFrame(self):
        self.dfarr.clear()
        self.nowDF = pd.DataFrame(index=range(0), columns=self.output_colums)
        for i, path in enumerate(self.filepath): #csv 파일 순회 하면서 같은 프레임 모아서 self.nowDF에 붙여둠
            if self.last_row[i] > 180000:
                print("[erase row] : ", self.last_row)
                print(self.filepath[i])
                self.__erase_csv_frame(self.filepath[i], self.last_frame)
                self.last_row[i] = 1
                time.sleep(0.1)
            if self.last_row[i] == 0:
                frame = self.__getFirstFrame(self.filepath[i])
                print(self.filepath[i])
                print(frame)


            self.dfarr.append(pd.read_csv(path,
                                          header=None,
                                          names=self.output_colums,
                                          skiprows = self.last_row[i],
                                          chunksize = self.last_row[i]+self.once_read_row
                                          ))
            if self.print_en>=2: print('cam num : ',i+1)

            try:
                temp_df = self.dfarr[-1].get_chunk(self.once_read_row).groupby('frame').get_group(self.last_frame)
                self.last_row[i]+=len(temp_df)

            except:
                if self.last_frame > 15000:
                    self.enable = False
                    return 0
                else: 
                    temp_df = self.fake_df

            if self.print_en >=2 : 
                print('temp_df size : ',len(temp_df))
                print(temp_df)

            self.nowDF = pd.concat([self.nowDF, temp_df], ignore_index=True)
        self.last_frame+= 1
        return self.nowDF
    
    def setStartFrame(self, frame):
        self.last_frame = frame

    def setReadFrame(self, frame):
        self.nextframe = frame

    def getDF(self):
        return self.nowDF
    
    def __erase_csv(self, file, line):
        path = file
        copy_path = 'C:\dev_program\RefutsalVideoAnalysis\\refutsal_test\\temp.csv' #temp
        with open(path, mode='r') as original_file, open(copy_path, mode='w', newline='') as new_file:
            reader = csv.reader(original_file)
            writer = csv.writer(new_file)

            # Copy the header row to the new file
            header = next(reader)
            writer.writerow(header)

            # Copy all rows except for lines 2-5
            for i, row in enumerate(reader):
                if  i > line:
                    writer.writerow(row)
                    
        # Rename the new file to the original filename
        import os
        os.replace(copy_path, path)

    def __erase_csv_frame(self, file, frame):
        path = file
        copy_path = 'C:\dev_program\RefutsalVideoAnalysis\\refutsal_test\\temp.csv' #temp
        with open(path, mode='r') as original_file, open(copy_path, mode='w', newline='') as new_file:
            reader = csv.reader(original_file)
            writer = csv.writer(new_file)

            # Copy the header row to the new file
            header = next(reader)
            writer.writerow(header)

            # Copy all rows except for lines 2-5
            for i, row in enumerate(reader):
                if  int(row[0]) >= frame:
                    writer.writerow(row)
                    
        # Rename the new file to the original filename
        import os
        os.replace(copy_path, path)
    def __getFirstFrame(self, path):
        with open(path, mode='r') as file:
            reader = csv.reader(file)
            header = next(file)
            for i, row in enumerate(reader):
                return row[0]