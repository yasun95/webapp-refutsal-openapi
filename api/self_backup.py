# from flask import Flask, render_template, Response, request, redirect, url_for, jsonify, session, current_app
# from flask_sqlalchemy import SQLAlchemy
# from flask_restful import Api, reqparse
# from flask_cors import CORS

# from config import *
# from models import db, REFUTSAL_COURT_TABLE, REFUTSAL_MATCH_TABLE, REFUTSAL_REPORT_TABLE, REFUTSAL_TAG_TABLE
# from .video_downloader import VideoDownloader
# import threading
# import time, os, sys, json, requests, uuid, subprocess
# import cv2
# from pathlib import Path

# # Directory Setting
# ROOT = Path(os.getcwd())
# sys.path.append(str(ROOT.parent))
# DOWNLOAD_DIR = ROOT / "api/resources/download_video"

# # Flask App & DBConfig
# app = Flask(__name__)
# app.config.from_object(DBConfig)
# app.config.from_object(PathConfig)
# app.app_context().push()
# app.config['SQLALCHEMY_DB_URI'] = DBConfig.SQLALCHEMY_DATABASE_URI
# app.secret_key = 'secret_key'
# db.init_app(app)

# CORS(app)
# api = Api(app)

# # Video
# video_downloader = VideoDownloader()

# video_urls = {}
# filenames = {}

# FLAG = False

# @app.route('/')
# def main_page():
#     return jsonify({'message': 'Welcome to the main page!'}), 200, {'Content-Type': 'application/json'}

# @app.route('/users', methods=['GET', 'POST'])
# def user_info():
#     if request.method == 'GET':
#         session['UUID'] = '950522'
#         return render_template('input_info.html')
#     elif request.method == 'POST':
#         return render_template('download_video.html')

# @app.route('/download', methods=['GET', 'POST'])
# def download():
#     UUID = session.get('UUID', None)
#     camnum = request.form['camnum']
#     vest_color1 = request.form['vest_color1']
#     vest_color2 = request.form['vest_color2']
#     video_url = request.form['video_url']
    
#     print('download info : ', UUID, camnum, vest_color1, vest_color2)

#     filename = str(camnum) + str(UUID) + '.avi'
#     video_code = video_url.lstrip('https://www.youtube.com/watch?v=')

#     # Set the download Directory and File Name
#     download_dir = DOWNLOAD_DIR / str(UUID)
#     download_dir.mkdir(parents=True, exist_ok=True)

#     video_path = PathConfig.VIDEO_PATH + str(UUID)

#     download_thread = threading.Thread(target=video_downloader.download, args=(video_url, video_path + '/' + filename))
#     download_thread.start()

#     # Set the User Info
#     video_urls[UUID] = video_url
#     filenames[camnum, UUID] = filename

#     session['UUID'] = UUID
#     session['camnum'] = camnum
#     session['vest_color1'] = vest_color1
#     session['vest_color2'] = vest_color2
#     session['video_url'] = video_url

#     return render_template('download_video.html', name=UUID)

# @app.route('/load', methods=['GET', 'POST'])
# def load():
#     UUID = session.get('UUID')
#     camnum = session.get('camnum')
#     vest_color1 = session.get('vest_color1')
#     vest_color2 = session.get('vest_color2')

#     print('load info : ', UUID, camnum, vest_color1, vest_color2)

#     video_url = video_urls[UUID]
#     filename = filenames[camnum, UUID]

#     session['UUID'] = UUID
#     session['camnum'] = camnum
#     session['vest_color1'] = vest_color1
#     session['vest_color2'] = vest_color2

#     def generate():  
#         for i in range(1, 101):
#             time.sleep(0.1)
#             progress = video_downloader.progress(video_url, PathConfig.VIDEO_PATH + str(UUID) + '/' + filename)
#             yield 'data: {}\n\n'.format(json.dumps({'percent': progress}))
#             if progress == 100:
#                 return Response

#     return Response(generate(), mimetype='text/event-stream')

# @app.route('/analyze', methods=['GET', 'POST'])
# def analyze():
#     UUID = session.get('UUID')
#     camnum = session.get('camnum')
#     vest_color1 = session.get('vest_color1')
#     vest_color2 = session.get('vest_color2')

#     print('analyze info : ', UUID, camnum, vest_color1, vest_color2)

#     # Call the detect goal route
#     response = requests.get(f"http://localhost:5000/analyze/detect/goal?UUID={UUID}&camnum={camnum}&vest_color1={vest_color1}&vest_color2={vest_color2}")
#     if response.status_code != 200:
#         pass
    
#     response = requests.get(f"http://localhost:5000/analyze/detect/player?UUID={UUID}&camnum={camnum}&vest_color1={vest_color1}&vest_color2={vest_color2}")
#     if response.status_code != 200:
#         pass

#     response = requests.get(f"http://localhost:5000/analyze/make/heatmap?UUID={UUID}&camnum={camnum}&vest_color1={vest_color1}&vest_color2={vest_color2}")
#     if response.status_code != 200:
#         pass

#     return render_template('analyze_video.html', name=UUID)

# @app.route('/analyze/detect/goal', methods=['GET', 'POST'])
# def detect_goal():
#     from .RefutsalVideoAnalysis.refutsal_util.goal_detection_db import GoalDetector
#     UUID = request.args.get('UUID')
#     camnum = request.args.get('camnum')
#     vest_color1 = request.args.get('vest_color1')
#     vest_color2 = request.args.get('vest_color2')

#     print('Goal info : ', UUID, camnum, vest_color1, vest_color2)

#     goal_csv_path = PathConfig.GOAL_ANALYSIS_CSV_PATH + str(UUID)
#     Path(goal_csv_path).mkdir(parents=True, exist_ok=True)

#     gd = GoalDetector(videodir = PathConfig.VIDEO_PATH + str(UUID),
#                     host = DBConfig.HOST,
#                     port = DBConfig.PORT,
#                     user = DBConfig.USER, 
#                     password = DBConfig.PASSWORD, 
#                     db = DBConfig.DBNAME, 
#                     court_uuid=DBConfig.TEST_COURT_UUID,
#                     )
#     try:
#         gd.setWriteDir(PathConfig.GOAL_ANALYSIS_CSV_PATH + str(UUID))
#         gd.printFilePath()
#         gd.makeOutputCsv()

#     except ValueError:
#         print('Video file is not found.')

#     def generate():
#         try:
#             time.sleep(1)
#             for vidnum, vidname in enumerate(gd.getAllVideoPath()):
#                 if gd.setVideo(filenum=vidnum, camnum=camnum ,resize=(1024,576)):
#                     gd.serchVideo(imgshow=False, color_filter='yellow')
#                     gd.remapFrame(5)
#                 else:
#                     print("skip video : ", vidname, " \n\tdo not have enough goal points(least 4) on DBConfig file")
                
#                 progress = int(100 * (vidnum+1) / len(gd.getAllVideoPath()))
#                 yield 'data: {}\n\n'.format(json.dumps({'percent': progress}))
#         except Exception as e:
#             print('Caught exception : ', e)

#     return Response(generate(), mimetype='text/event-stream')

# @app.route('/analyze/detect/player', methods=['GET', 'POST'])
# def detect_player():
#     UUID = request.args.get('UUID')
#     camnum = request.args.get('camnum')
#     vest_color1 = request.args.get('vest_color1')
#     vest_color2 = request.args.get('vest_color2')

#     if UUID is None:
#         UUID = '950522'
#     if camnum is None:
#         camnum = '02_'
#     add_file = '/' + str(camnum)
#     camera_number = camnum.lstrip("0")
#     camera_number = camera_number.rstrip("_")

#     progress = {'player_classification': 0, 'birds_eye_view' : 0, 'clustering': 0}

#     PLAYER_CLASSIFICATION_FLAG = False
#     BIDRS_EYE_VIEW_FLAG = False
#     CLUSTERING_FLAG = False

#     print('detect info : ', UUID, camnum, vest_color1, vest_color2)

#     if not detect_player.subprocess_running and FLAG == False:
#         # Player Classification
#         player_classification_path = PathConfig.PLAYER_CLASSIFICATION_CSV_PATH + str(UUID)
#         if not os.path.exists(player_classification_path):
#             os.makedirs(player_classification_path)
#         player_classification_csv_filename = 'player_classification_result.csv'
#         cmd_player_classification = f'python3 {PathConfig.PLAYER_CLASSIFICATION_SCRIPT_PATH} --source {PathConfig.VIDEO_PATH + str(UUID)} --camera-number {int(camera_number)} --csv-path {player_classification_path + str(add_file) + player_classification_csv_filename} --vest-color1 {vest_color1} --vest-color2 {vest_color2}'
        
#         detect_player.subprocess_running = True
#         PLAYER_CLASSIFICATION_FLAG = True

#         print("detect player 1")
#         if PLAYER_CLASSIFICATION_FLAG == True and BIDRS_EYE_VIEW_FLAG == False and CLUSTERING_FLAG == False:
#             # subprocess.call(cmd, shell=True)
#             try : 
#                 proc = subprocess.Popen(cmd_player_classification, shell=True)
#                 proc.communicate()

#             except AssertionError as e:
#                 print('Video Not found : ', e)

#                 return Response

#         progress['player_classification'] = (1/3)*100            
#         PLAYER_CLASSIFICATION_FLAG = False
#         BIDRS_EYE_VIEW_FLAG = True

#         # Birds Eye View
#         print("birds eye view 1")
#         birds_eye_view_path = PathConfig.BIRDS_EYE_VIEW_CSV_PATH + str(UUID)
#         folder_name = '/' + str(UUID)
#         if not os.path.exists(birds_eye_view_path):
#             os.makedirs(birds_eye_view_path)
#         birds_eye_view_csv_filename = 'birds_eye_view_result.csv'
#         cmd_birds_eye_view = f'python3 {PathConfig.BIRDS_EYE_VIEW_SCRIPT_PATH} --UUID {str(UUID)} --input-path {player_classification_path} --output-path {birds_eye_view_path} --folder-name {folder_name} --output-filename {camnum + birds_eye_view_csv_filename} --host {DBConfig.HOST} --port {DBConfig.PORT} --user {DBConfig.USER} --password {DBConfig.PASSWORD} --db-name {DBConfig.DBNAME} --court-uuid {DBConfig.TEST_COURT_UUID}'

#         if PLAYER_CLASSIFICATION_FLAG == False and BIDRS_EYE_VIEW_FLAG == True and CLUSTERING_FLAG == False:
#             proc = subprocess.Popen(cmd_birds_eye_view, shell=True)
#             proc.communicate()

#         progress['birds_eye_view'] = (2/3)*100
#         BIDRS_EYE_VIEW_FLAG = False
#         CLUSTERING_FLAG = True


#         # Clustering
#         print("clustering 1")
#         clustering_path = PathConfig.CLUSTERING_CSV_PATH + str(UUID)
#         session['cluster_path'] = clustering_path
#         if not os.path.exists(clustering_path):
#             os.makedirs(clustering_path)
#         clustering_csv_filename = 'clustering_result.csv'
#         cmd_clustering = f'python3 {PathConfig.CLUSTERING_SCRIPT_PATH} --UUID {str(UUID)} --input-path {birds_eye_view_path} --output-path {clustering_path} --output-filename {clustering_csv_filename}'

#         if PLAYER_CLASSIFICATION_FLAG == False and BIDRS_EYE_VIEW_FLAG == False and CLUSTERING_FLAG == True:
#             proc = subprocess.Popen(cmd_clustering, shell=True)
#             proc.communicate()

#         detect_player.subprocess_running = False
#         CLUSTERING_FLAG = False
#         progress = 100

#     def generate():
#         # Simulate some work being done
#         time.sleep(1)
#         detect_player.subprocess_running = True
#         FLAG = True
#         yield 'data: {}\n\n'.format(json.dumps({'percent': progress}))
        
#     return Response(generate(), mimetype='text/event-stream')

# detect_player.subprocess_running = False

# @app.route('/analyze/make/heatmap', methods=['GET', 'POST'])
# def make_heatmap():
#     UUID = request.args.get('UUID')
#     camnum = request.args.get('camnum')
#     clustering_path = session.get('clustering_path')
#     vest_color1 = request.args.get('vest_color1')
#     vest_color2 = request.args.get('vest_color2')

#     print('heatmap info : ', UUID, camnum, vest_color1, vest_color2)

#     # Heatmap
#     heatmap_path = PathConfig.HEATMAP_PATH + str(UUID)
#     if not os.path.exists(heatmap_path):
#         os.makedirs(heatmap_path, exist_ok=True)
#     heatmap_save_path = PathConfig.HEATMAP_PATH + str(UUID)
#     heatmap_csv_filename = 'heatmap_result.csv'
#     cmd_heatmap = f'python3 {PathConfig.HEATMAP_SCRIPT_PATH} --UUID {str(UUID)} --refutsal-path {PathConfig.REFUTSAL_PATH} --input-path {clustering_path} --output-path {heatmap_save_path} --output-filename {heatmap_csv_filename} --goal-tag {PathConfig.GOAL_ANALYSIS_CSV_PATH + str(UUID)} --host {DBConfig.HOST} --port {DBConfig.PORT} --user {DBConfig.USER} --password {DBConfig.PASSWORD} --db-name {DBConfig.DBNAME} --court-uuid {DBConfig.MATCH_UUID} --vest-color1 {vest_color1} --vest-color2 {vest_color2}'

#     clustering_file = os.path.join(clustering_path, '/clustering_result.csv')

#     if not os.path.exists(clustering_file):
#         pass
#     else:
#         proc = subprocess.Popen(cmd_heatmap, shell=True)
#         proc.communicate()
#         exit_code = proc.wait()

#         if exit_code == 0:
#             progress = 100
#         else:
#             progress = 0

#     if 'progress' not in locals():
#         progress = 0

#     def generate():
#         time.sleep(1)
#         yield 'data: {}\n\n'.format(json.dumps({'percent': progress}))

#     return Response(generate(), mimetype='text/event-stream')

# @app.route('/result', methods=['GET', 'POST'])
# def result():
#     return render_template('result.html')