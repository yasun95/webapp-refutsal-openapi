import os
import pandas as pd


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
        #self.nowDF = pd.DataFrame()
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
                #print(path)
                #self.forder_path.append(path)
                self.filepath.append(path)
                self.last_row.append(1)

        print(self.filepath)
        return self.filepath

    def readFrame(self):
        '''
        
        '''
        self.dfarr.clear()
        self.nowDF = pd.DataFrame(index=range(0), columns=self.output_colums)

        for i, path in enumerate(self.filepath): #csv 파일 순회 하면서 같은 프레임 모아서 self.nowDF에 붙여둠
            self.dfarr.append(pd.read_csv(path,
                                          header=None,
                                          names=self.output_colums,
                                          skiprows = self.last_row[i],
                                          chunksize = self.last_row[i]+self.once_read_row
                                          ))
            if self.print_en>=2: print('cam num : ',i+1)
            #print('scan index : ', self.dfarr[-1].get_chunk(self.once_read_row)['frame'].idxmax())
            #print(self.dfarr[-1].get_chunk(self.once_read_row).groupby('frame').get_group(self.last_frame))
            try:
                temp_df = self.dfarr[-1].get_chunk(self.once_read_row).groupby('frame').get_group(self.last_frame)
            except:
                print("=============== end frame cam", i+1," =================")
                self.enable = False
                return 0
                
            self.last_row[i]+=len(temp_df)
            if self.print_en >=2 : 
                print('temp_df size : ',len(temp_df))
                print(temp_df)
            self.nowDF = pd.concat([self.nowDF, temp_df], ignore_index=True)

        self.last_frame+=1
        return self.nowDF


    def getDF(self):
        return self.nowDF