from pandas import DataFrame
from refutsal_util.csv_writer import CsvWriter
import numpy as np

class BirdsEyeTrans(CsvWriter):
    def __init__(self, H, make_csv=False, result_path=None):
        CsvWriter.__init__(self, make_csv=make_csv, csv_path=result_path)
        self.H_Metrix = H
        self.df = None
        self.data = None
        self.pos = []
        self.stadium_size_x = (20+2)*1000
        self.stadium_size_y = (10+2)*1000

    def readCsv(self, fname):
        #data = np.genfromtxt(fname, delimiter=',', skip_header=0)
        #print(data)
        
        from pandas import read_csv
        self.df = DataFrame({'frame', 'camnum', 'id', 'team', 'cls', 'x', 'y'})
        #self.df = read_csv(fname, delimiter=',',  index_col=0)
        self.df = read_csv(fname, delimiter=',')
        self.data = self.df.values
        print (self.data) 
        print(self.df.head)

    def setStadiumSize(self, x, y):
        self.stadium_size_x = (x+2)*1000
        self.stadium_size_y = (y+2)*1000


    def transform(self, H_Metrix, output_path = None, fordername = None, output_file_name = None, ball_ignore_points = None):
        self.makeOutputForder(outputpath=output_path, filename=output_file_name, fieldnames=['frame', 'camnum', 'id', 'team', 'cls', 'x', 'y'])
        self.openCsv()
        
        for each_player in self.df.itertuples():
            if(each_player.cls !=2) and (each_player.cls!=0): # 사람또는 공이 아닌경우 패스
                pass

            mypoints = np.append(each_player.x, each_player.y)
            mypoints = np.append(mypoints, 1)
            mypoints.reshape(3,1)
            mypoints = mypoints.astype(np.float64)
            #after = np.matmul(H_Metrix[0], mypoints)
            after = H_Metrix[0]@mypoints
            remapping = H_Metrix[0][2][0]*mypoints[0] + H_Metrix[0][2][1]*mypoints[1] +1
            after = after/ remapping
            #frame, camnum, id, team, cls, x, y
            final_arr = [each_player[1],each_player[2],each_player[3],each_player[4],each_player.cls,int(after[0]*1000),int(after[1]*1000)]
            
            #stadium_size_x = (20+2)*1000
            #stadium_size_y = (10+2)*1000
            skip = False
            if(each_player.cls ==32) and (len(ball_ignore_points)!=0):
                for ig_point in ball_ignore_points:
                    if abs(final_arr[5]-ig_point[0])+abs(final_arr[6]-ig_point[1])<500:
                        skip = True    
            if (abs(final_arr[5]) < self.stadium_size_x/2) & (abs(final_arr[6]) < self.stadium_size_y/2) & (not skip):
                self.writerowCsv(final_arr)
   
        self.closeCsv()
            
    def saveCsv(self):
        print(self.pos)
        return 0