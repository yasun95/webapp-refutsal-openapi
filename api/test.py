import os
import pymysql
import json
from RefutsalVideoAnalysis.refutsal_util.json_config_paser import ConfigData
host = '3.36.242.44'
port = 3306
user = 'refutsal.tecs.club'
password = 'refutsal!@34'
db_name = 'refutsal.tecs.club'
court_uuid = '3ddfb499c0b44b92'

conn = pymysql.connect(
host = host,
port = port,
user = user,
password= password,
db= db_name,
charset= 'utf8'
)
cursor = conn.cursor()



cursor.execute("SELECT COURT_AUX_INFO FROM REFUTSAL_COURT_TABLE WHERE COURT_UUID LIKE '%s'" % (court_uuid))
data = cursor.fetchall()
str_data=data[0][0]
alldata = json.loads(str_data)
data=alldata["cameraSetting"]

print(alldata)

UUID ='d9a8f4da-b63e-418d-9246-6a2b5a1e41fa'

class Config:
    # My Local
    # USER = 'yasun95'
    # PASSWORD = '9522'
    # HOST = 'localhost'
    PORT = 3306
    DBNAME = 'refutsal.tecs.club'
    TEST_COURT_UUID = '3ddfb499c0b44b92'
    VID_PATH = os.path.abspath('api/resources/saved_videos/')
    OUTPUT_PATH = os.path.abspath('api/resources/result/')

    # Refutsal Local
    USER = 'yasun95'
    PASSWORD = 'tjswhd0522!'
    HOST = '3.36.242.44'

    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# from RefutsalVideoAnalysis.refutsal_util.goal_detection_db import GoalDetector
from RefutsalVideoAnalysis.refutsal_util.goal_detection_db import GoalDetector
gd = GoalDetector(videodir = Config.VID_PATH + '/' + str(UUID),
                    host = Config.HOST,
                    port = Config.PORT,
                    user = Config.USER, 
                    password = Config.PASSWORD, 
                    db = Config.DBNAME, 
                    court_uuid=Config.TEST_COURT_UUID,
                    )
print('dfdf')
gd.setWriteDir(Config.OUTPUT_PATH +  str(UUID))
gd.printFilePath()


for vidnum, vidname in enumerate(gd.getAllVideoPath()):
    print('dfddfd')
    if gd.setVideo(filenum=vidnum, resize=(1024,576)):
        #gd.setgoalmask(opt="read") #ROI 등록해야할때
        #gd.printChart()
        progress = gd.serchVideo(imgshow=False, color_filter='yellow')
        #gd.serchVideo(imgshow=True) #분석중함수 (영상 표시여부 True)
        gd.remapFrame(5)
    else:
        print("skip video : ", vidname, " \n\tdo not have enough goal points(least 4) on config file")
    print('vidnum : ', progress)
    progress = int(100 * (vidnum+1) / len(gd.getAllVideoPath()))

# yield 'data: {}\n\n'.format(json.dumps({'percent': progress}))
