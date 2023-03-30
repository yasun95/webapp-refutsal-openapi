import os

class DBConfig:
    # My Local
    # USER = 'yasun95'
    # PASSWORD = '9522'
    # HOST = 'localhost'

    # Refutsal Local
    USER = 'refutsal.tecs.club'
    PASSWORD = 'refutsal!@34'
    HOST = '3.36.242.44'
    PORT = 3306
    DBNAME = 'refutsal.tecs.club'
    TEST_COURT_UUID = '3ddfb499c0b44b92'

    # Goal Tag Upload Config
    MATCH_UUID = '0xtest_230220_1'
    GOAL_TAG_DBNAME = 'refutsal_test_db'

    # SQLALCHEMY 
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class PathConfig:
    # RefutsalVideoAanlysis
    REFUTSAL_PATH = os.path.abspath('api/RefutsalVideoAnalysis') + '/'

    # YOLOv5
    YOLO_PATH = os.path.abspath('api/RefutsalVideoAnalysis/yolov5') + '/'

    # Video Download
    VIDEO_PATH = os.path.abspath('api/resources/download_video') + '/'

    # Goal Tag
    GOAL_ANALYSIS_CSV_PATH = os.path.abspath('api/resources/csv/goal_tag') + '/'

    # Player Classification
    PLAYER_CLASSIFICATION_SCRIPT_PATH = os.path.abspath('api/RefutsalVideoAnalysis/refutsal/refutsal_detector.py')
    PLAYER_CLASSIFICATION_CSV_PATH = os.path.abspath('api/resources/csv/player_classification') + '/'

    # Birds Eye View
    BIRDS_EYE_VIEW_SCRIPT_PATH = os.path.abspath('api/RefutsalVideoAnalysis/refutsal/birds_eye_main.py')
    BIRDS_EYE_VIEW_CSV_PATH = os.path.abspath('api/resources/csv/birds_eye_view') + '/'

    # Clustering
    CLUSTERING_SCRIPT_PATH = os.path.abspath('api/RefutsalVideoAnalysis/refutsal/clustering_main.py')
    CLUSTERING_CSV_PATH = os.path.abspath('api/resources/csv/clustering') + '/'

    # Heatmap
    HEATMAP_SCRIPT_PATH = os.path.abspath('api/RefutsalVideoAnalysis/refutsal/tag_uploader.py')
    HEATMAP_PATH = os.path.abspath('api/resources/heatmap') + '/'
    HEATMAP_CSV_PATH = os.path.abspath('api/resources/csv/heatmap') + '/'
