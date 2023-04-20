import sys, argparse
import os
import csv
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from refutsal_util.db_uploader import DbUploader
"""
goal_detection_db에서 생성한 태그정보 (csv)를 읽고
캠간 중복인식된 데이터를 제거하고 json format으로 변경,
DB에 업로드
"""

# SUNJONG EDIT
def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--UUID', type=str, default='')
    parser.add_argument('--refutsal-path', type=str, default='')
    parser.add_argument('--input-path', type=str, default='')
    parser.add_argument('--output-path', type=str, default='')
    parser.add_argument('--goal-tag', type=str, default='')
    parser.add_argument('--host', type=str, default='')
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--user', type=str, default='')
    parser.add_argument('--password', type=str, default='')
    parser.add_argument('--db-name', type=str, default='')
    parser.add_argument('--court-uuid', type=str, default='')
    parser.add_argument("--vest-color1", type=str, default='RED')
    parser.add_argument("--vest-color2", type=str, default='BLUE')
    opt = parser.parse_args()

    return opt

opt = parse_opt()

#path
ROOT = opt.refutsal_path
GOALTAG = opt.goal_tag + 'goal_tag.csv'
CLUSTER_RESULT_PATH = opt.input_path + '/clustering_result.csv'
HEATMAP_SAVE_PATH = opt.output_path + '/heatmap_result.png'

#config
TIME_GAP = 10 #중복 제거할 타임갭

#DB 설정
sw = DbUploader(
    host = opt.host,
    port = opt.port,
    user = opt.user,
    password = opt.password,
    db = opt.db_name,
    uuid = opt.court_uuid,
    left_team_color = opt.vest_color1,
    right_team_color = opt.vest_color2,
    goal_tag_table_name = "REFUTSAL_TAG_TABLE",
    heatmap_table_name = "REFUTSAL_REPORT_TABLE"
    )

## DB read
#sw.readCamSettingDb(TEST_COURT_UUID)

## TAG
#csv 읽기, 정렬, 중복 제거
tag_data=sw.readGoalCsv(GOALTAG)
#json 포맷
json_data = sw.makeGoalTag(tag_data)
#태그 업로드
sw.uploadTagDb(showdata=True)

## HEAT MAP
#클러스터링 결과 csv 읽고 히트맵 작성
heatmap_l, heatmap_r, heatmap_ball = sw.makeHeatMap(CLUSTER_RESULT_PATH)
#히트맵 시각화
sw.showHeatMap(heatmap_l, heatmap_r, heatmap_ball, HEATMAP_SAVE_PATH)
#히트맵 6종 업로드
sw.uploadHeatMapDb()
print('All Data Upload is done.')
