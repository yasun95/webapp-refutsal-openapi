import os, argparse
import sys
import cv2

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from refutsal_util.json_config_paser import ConfigData
from refutsal_util.birds_eye_utils import showGrid
from refutsal_util.birds_eye_trans import BirdsEyeTrans
from refutsal_util.file_path_collector import FilePathCollector

# SUNJONG EDIT
def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--UUID', type=str, default='')
    parser.add_argument('--input-path', type=str, default='')
    parser.add_argument('--output-path', type=str, default='')
    parser.add_argument('--folder-name', type=str, default='')
    parser.add_argument('--output-filename', type=str, default='')
    parser.add_argument('--host', type=str, default='')
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--user', type=str, default='')
    parser.add_argument('--password', type=str, default='')
    parser.add_argument('--db-name', type=str, default='')
    parser.add_argument('--court-uuid', type=str, default='')
    opt = parser.parse_args()

    return opt

opt = parse_opt()

input_path = opt.input_path
output_path = opt.output_path

fp = FilePathCollector(input_path, findformat=".csv")
fp.printFilePath()
file_list = fp.getAllVideoPath()
settingdata = ConfigData(
                        host = opt.host,
                        port = opt.port,
                        user = opt.user,
                        password = opt.password,
                        db_name = opt.db_name,
                        court_uuid = opt.court_uuid
                        )

for file_path in file_list:
    filename = os.path.basename(file_path)
    camnum = int(filename[:2]) # 파일명 앞 2글자는 카메라 넘버

    data = settingdata.camdata[camnum]
    ball_ignore_point = settingdata.camdata[camnum].ignore_points
    frame_points = data.frame_points * 2/3
    real_points = data.real_points
    stadium_size = [settingdata.stadium_width, settingdata.stadium_height]

    H_Metrix = cv2.findHomography(frame_points, real_points, cv2.RANSAC, 5.0)
    bt = BirdsEyeTrans(H_Metrix, make_csv=True, result_path=output_path)
    bt.setStadiumSize(stadium_size[0], stadium_size[1])
    bt.readCsv(file_path)
    # SUNJONG EDIT / FILENAME
    bt.transform(H_Metrix, output_path=output_path, output_file_name=  '0' + str(camnum) + '_' + opt.output_filename, ball_ignore_points=ball_ignore_point)