import time, os, sys, json, requests, uuid, subprocess, threading, csv
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue

from flask import Flask, render_template, Response, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_cors import CORS

from config import *
from models import db
from .video_downloader import VideoDownloader

# Directory Setting
ROOT = Path(os.getcwd())
sys.path.append(str(ROOT.parent))
DOWNLOAD_DIR = ROOT / "api/resources/download_video"

# Flask App & DBConfig
app = Flask(__name__)
app.config.from_object(DBConfig)
app.config.from_object(PathConfig)
app.app_context().push()
app.config['SQLALCHEMY_DB_URI'] = DBConfig.SQLALCHEMY_DATABASE_URI
app.secret_key = 'secret_key'
db.init_app(app)

CORS(app)
api = Api(app)

# Video
video_downloader = VideoDownloader()

# Initializing - User & Video Info
video_urls = {}
camnums = {}
filenames = {}
video_paths = {}

# Initializing - Goal Detection
goal_deteciton_csv_filename = {}
add_camnum_filenum = {}
camera_number = {}
cmd_goal_deteciton = {}
proc_goal = {}

# Initializing - Player Detection
camera_number = {}
cmd_player_classification = {}
proc_pd = {}

# Initializing - Birds Eye View
add_camnum_filenums = {}
cmd_birds_eye_view = {}
proc_bev = {}

# Initializing - Heatmap
proc_heat = {}

# Youtube Test Video URL
# CAM2 : ahttps://www.youtube.com/watch?v=ovcnQJ2t0EI
# CAM4 : https://www.youtube.com/watch?v=jBlrOE6dHmg
# CAM6 : https://www.youtube.com/watch?v=0xtc_FBwR-g
# CAM8 : https://www.youtube.com/watch?v=9dSG69MkOhE

FLAG = False

@app.route('/')
def main_page():
    return jsonify({'message': 'Welcome to the main page!'}), 200, {'Content-Type': 'application/json'}

@app.route('/users', methods=['GET', 'POST'])
def user_info():
    if request.method == 'GET':
        # Make the uuid, if you want. 
        # UUID = uuid.uuid4
        session['UUID'] = '950522'
        return render_template('input_info.html')
    elif request.method == 'POST':
        return render_template('download_video.html')

@app.route('/download', methods=['GET', 'POST'])
def download():
    UUID = session.get('UUID', None)
    vest_color1 = request.form['vest_color1']
    vest_color2 = request.form['vest_color2']

    camnum1 = request.form['camnum1']
    camnum2 = request.form['camnum2']
    camnum3 = request.form['camnum3']
    camnum4 = request.form['camnum4']

    video_url1 = request.form['video_url1']
    video_url2 = request.form['video_url2']
    video_url3 = request.form['video_url3']
    video_url4 = request.form['video_url4']

    filename1 = str(camnum1) + str(UUID) + '.avi'
    filename2 = str(camnum2) + str(UUID) + '.avi'
    filename3 = str(camnum3) + str(UUID) + '.avi'
    filename4 = str(camnum4) + str(UUID) + '.avi'

    # video_code = video_url.lstrip('https://www.youtube.com/watch?v=')

    # Session
    session['UUID'] = UUID
    session['vest_color1'] = vest_color1
    session['vest_color2'] = vest_color2

    # Set the download Directory and File Name
    download_dir = Path(PathConfig.VIDEO_PATH) / str(UUID)
    download_dir.mkdir(parents=True, exist_ok=True)

    video_path1 = download_dir / camnum1.rstrip("_")
    video_path2 = download_dir / camnum2.rstrip("_")
    video_path3 = download_dir / camnum3.rstrip("_")
    video_path4 = download_dir / camnum4.rstrip("_")

    video_path1.mkdir(parents=True, exist_ok=True)
    video_path2.mkdir(parents=True, exist_ok=True)
    video_path3.mkdir(parents=True, exist_ok=True)
    video_path4.mkdir(parents=True, exist_ok=True)

    # Multi Threading - Video Download
    download_thread1 = threading.Thread(target=video_downloader.download, args=(video_url1, str(video_path1) + '/' + filename1))
    download_thread2 = threading.Thread(target=video_downloader.download, args=(video_url2, str(video_path2) + '/' + filename2))
    download_thread3 = threading.Thread(target=video_downloader.download, args=(video_url3, str(video_path3) + '/' + filename3))
    download_thread4 = threading.Thread(target=video_downloader.download, args=(video_url4, str(video_path4) + '/' + filename4))

    download_thread1.start()
    download_thread2.start()
    download_thread3.start()
    download_thread4.start()

    # Set the User Info
    camnums[UUID] = [camnum1, camnum2, camnum3, camnum4]
    video_urls[UUID] = [video_url1, video_url2, video_url3, video_url4]
    filenames[UUID] = [filename1, filename2, filename3, filename4]
    video_paths[UUID] = [video_path1, video_path2, video_path3, video_path4]

    return render_template('download_video.html', uuid=UUID)

@app.route('/load', methods=['GET', 'POST'])
def load():
    UUID = session.get('UUID')
    vest_color1 = session.get('vest_color1')
    vest_color2 = session.get('vest_color2')

    session['UUID'] = UUID
    session['vest_color1'] = vest_color1
    session['vest_color2'] = vest_color2
    
    progress_queue = Queue()

    def check_progress(video_url, path, index):
        progress = 0
        while progress < 100:
            progress = video_downloader.progress(video_url, path)
            progress_queue.put((index, progress))
            print('Video Download {}: {}%'.format(index, progress))
        return 1

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for i, video_url in enumerate([video_urls[UUID][0], video_urls[UUID][1], video_urls[UUID][2], video_urls[UUID][3]]):
            path = video_paths[UUID][i] / filenames[UUID][i]
            future = executor.submit(check_progress, video_url, path, i)
            futures.append(future)

    def generate():
        time.sleep(0.1)
        progress = 0
        while True:
            downloaded_videos = sum(check_progress(video_urls[UUID][i], video_paths[UUID][i] / filenames[UUID][i], i) for i in range(4))
            progress = int(downloaded_videos / 4 * 100)
            yield 'data: {}\n\n'.format(json.dumps({
                'percent': progress
            }))
            if downloaded_videos == 4:
                break

    return Response(generate(), mimetype='text/event-stream')

GOAL_DETECT_FLAG = False

@app.route('/analyze/detect/goal', methods=['GET', 'POST'])
def detect_goal():
    global GOAL_DETECT_FLAG
    UUID = request.args.get('UUID')

    goal_deteciton_path = PathConfig.GOAL_DETECITON_CSV_PATH + str(UUID)
    Path(goal_deteciton_path).mkdir(parents=True, exist_ok=True)

    if not GOAL_DETECT_FLAG:
        for i in range(4):
            add_camnum_filenum[i] = '/' + str(camnums[UUID][i])
            goal_deteciton_csv_filename[i] = add_camnum_filenum[i] + 'goal_tag.csv'
            cmd_goal_deteciton[i]= f'python3 {PathConfig.GOAL_DETECTION_SCRIPT_PATH} --input-path {video_paths[UUID][i]} --output-path {goal_deteciton_path} --output-filename {goal_deteciton_csv_filename[i].lstrip("/")} --host {DBConfig.HOST} --port {DBConfig.PORT} --user {DBConfig.USER} --password {DBConfig.PASSWORD} --db-name {DBConfig.DBNAME} --match-uuid {DBConfig.MATCH_UUID} --court-uuid {DBConfig.TEST_COURT_UUID}'

            subprocess.run(cmd_goal_deteciton[i], shell=True, check=True)
    
    GOAL_DETECT_FLAG = True

    with open(goal_deteciton_path + '/goal_tag.csv', 'w', newline='') as csvfile:
        fieldnames = ['camnum','team', 'min', 'sec']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    progress = 100

    def generate():
        yield 'data: {}\n\n'.format(json.dumps({'percent': progress}))

    return Response(generate(), mimetype='text/event-stream')

PLAYER_CLASSIFICATION_FLAG = False
BIRDS_EYE_VIEW_FLAG = False
CLUSTERING_FLAG = False
DETECT_FLAG = False

@app.route('/analyze/detect/player', methods=['GET', 'POST'])
def detect_player():
    global GOAL_DETECT_FLAG, PLAYER_CLASSIFICATION_FLAG, BIRDS_EYE_VIEW_FLAG, CLUSTERING_FLAG, DETECT_FLAG
    UUID = request.args.get('UUID')
    vest_color1 = request.args.get('vest_color1')
    vest_color2 = request.args.get('vest_color2')

    session['UUID'] = UUID
    session['vest_color1'] = vest_color1
    session['vest_color2'] = vest_color2

    for i in range(4):
        add_camnum_filenum[i] = '/' + str(camnums[UUID][i])
        camera_number[i] = camnums[UUID][i].lstrip("0")
        camera_number[i] = camera_number[i].rstrip("_")
        add_camnum_filenums[i] = add_camnum_filenum[i].lstrip('/')

    progress = 0

    # Player Classification
    player_classification_path = PathConfig.PLAYER_CLASSIFICATION_CSV_PATH + str(UUID)
    if not os.path.exists(player_classification_path):
        os.makedirs(player_classification_path)
    player_classification_csv_filename = 'player_classification_result.csv'

    if GOAL_DETECT_FLAG and not PLAYER_CLASSIFICATION_FLAG:
    #     # start = time.time()
        processes = []
        for i in range(4):
            cmd_player_classification[i] = f'python3 {PathConfig.PLAYER_CLASSIFICATION_SCRIPT_PATH} --source {video_paths[UUID][i]} --camera-number {int(camera_number[i])} --csv-path {player_classification_path + add_camnum_filenum[i] + player_classification_csv_filename} --vest-color1 {vest_color1} --vest-color2 {vest_color2}'
            proc_pd[i] = subprocess.Popen(cmd_player_classification[i], shell=True)
            processes.append(proc_pd[i])

        for process in processes:
            process.wait()

        # print("PLAYER_CLASSIFICATION RUNTIME : ", time.time() - start)
    PLAYER_CLASSIFICATION_FLAG = True
    progress = int(100 * 1 / 3)


    # Birds Eye View
    birds_eye_view_path = PathConfig.BIRDS_EYE_VIEW_CSV_PATH + str(UUID)
    folder_name = '/' + str(UUID)
    if not os.path.exists(birds_eye_view_path):
        os.makedirs(birds_eye_view_path)
    birds_eye_view_csv_filename = 'birds_eye_view_result.csv'

    if PLAYER_CLASSIFICATION_FLAG and not BIRDS_EYE_VIEW_FLAG:
        # start = time.time()
        cmd_birds_eye_view = f'python3 {PathConfig.BIRDS_EYE_VIEW_SCRIPT_PATH} --UUID {str(UUID)} --input-path {player_classification_path} --output-path {birds_eye_view_path} --folder-name {folder_name} --output-filename {birds_eye_view_csv_filename} --host {DBConfig.HOST} --port {DBConfig.PORT} --user {DBConfig.USER} --password {DBConfig.PASSWORD} --db-name {DBConfig.DBNAME} --court-uuid {DBConfig.TEST_COURT_UUID}'
        subprocess.run(cmd_birds_eye_view, shell=True, check=True)
    
        # print("BIRDS_EYE_VIEW RUNTIME : ", time.time() - start)
    BIRDS_EYE_VIEW_FLAG = True
    progress = int(100 * 2 / 3)

    # Clustering
    clustering_path = PathConfig.CLUSTERING_CSV_PATH + str(UUID)
    if not os.path.exists(clustering_path):
        PathConfig.GOAL_DETECITON_CSV_PATH + str(UUID) + '/' + os.makedirs(clustering_path)
    clustering_csv_filename = 'clustering_result.csv'

    if BIRDS_EYE_VIEW_FLAG and not CLUSTERING_FLAG:
        # start = time.time()
        cmd_clustering = f'python3 {PathConfig.CLUSTERING_SCRIPT_PATH} --UUID {str(UUID)} --input-path {birds_eye_view_path} --output-path {clustering_path} --output-filename {clustering_csv_filename}'
        subprocess.run(cmd_clustering, shell=True, check=True)

        # print("CLUSTERING RUNTIME : ", time.time() - start)
    CLUSTERING_FLAG = True
    progress = 100

    DETECT_FLAG = True
    
    def generate():
        
        yield 'data: {}\n\n'.format(json.dumps({'percent': progress}))
        time.sleep(1)
        
    return Response(generate(), mimetype='text/event-stream')

HEATMAP_FLAG = False

@app.route('/analyze/make/heatmap', methods=['GET', 'POST'])
def make_heatmap():
    global DETECT_FLAG, HEATMAP_FLAG
    UUID = request.args.get('UUID')
    vest_color1 = request.args.get('vest_color1')
    vest_color2 = request.args.get('vest_color2')

    session['UUID'] = UUID
    session['vest_color1'] = vest_color1
    session['vest_color2'] = vest_color2

    print('heatmap info : ', UUID, vest_color1, vest_color2)

    # Heatmap
    heatmap_path = PathConfig.HEATMAP_PATH + str(UUID)
    if not os.path.exists(heatmap_path):
        os.makedirs(heatmap_path, exist_ok=True)
    heatmap_save_path = PathConfig.HEATMAP_PATH + str(UUID)
    clustering_path = PathConfig.CLUSTERING_CSV_PATH + str(UUID)
    goal_tag_path = PathConfig.GOAL_DETECITON_CSV_PATH + str(UUID) + '/'

    # Goal Tag csv file Merge
    goal_tag1 = pd.read_csv(PathConfig.GOAL_DETECITON_CSV_PATH + str(UUID) + '/' + add_camnum_filenums[0] + 'goal_tag.csv')
    goal_tag2 = pd.read_csv(PathConfig.GOAL_DETECITON_CSV_PATH + str(UUID) + '/' + add_camnum_filenums[1] + 'goal_tag.csv')
    goal_tag3 = pd.read_csv(PathConfig.GOAL_DETECITON_CSV_PATH + str(UUID) + '/' + add_camnum_filenums[2] + 'goal_tag.csv')
    goal_tag4 = pd.read_csv(PathConfig.GOAL_DETECITON_CSV_PATH + str(UUID) + '/' + add_camnum_filenums[3] + 'goal_tag.csv')

    merged_df = pd.merge(goal_tag1, goal_tag2, how='outer')
    merged_df = pd.merge(merged_df, goal_tag3, how='outer')
    merged_df = pd.merge(merged_df, goal_tag4, how='outer')

    drop_duplicates_df = merged_df.drop_duplicates(subset=['min', 'sec'])
    drop_duplicates_df.to_csv(PathConfig.GOAL_DETECITON_CSV_PATH + str(UUID) + '/goal_tag.csv', index=False)

    if DETECT_FLAG and not HEATMAP_FLAG:
        cmd_heatmap = f'python3 {PathConfig.HEATMAP_SCRIPT_PATH} --UUID {str(UUID)} --refutsal-path {PathConfig.REFUTSAL_PATH} --input-path {clustering_path} --output-path {heatmap_save_path}  --goal-tag {goal_tag_path} --host {DBConfig.HOST} --port {DBConfig.PORT} --user {DBConfig.USER} --password {DBConfig.PASSWORD} --db-name {DBConfig.DBNAME} --court-uuid {DBConfig.MATCH_UUID} --vest-color1 {vest_color1} --vest-color2 {vest_color2}'
        subprocess.run(cmd_heatmap, shell=True, check=True)
    HEATMAP_FLAG = True

    progress = 100

    def generate():
        yield 'data: {}\n\n'.format(json.dumps({'percent': progress}))
        time.sleep(1)

    return Response(generate(), mimetype='text/event-stream')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    UUID = session.get('UUID')
    vest_color1 = session.get('vest_color1')
    vest_color2 = session.get('vest_color2')

    session['UUID'] = UUID
    session['vest_color1'] = vest_color1
    session['vest_color2'] = vest_color2

    response = requests.get(f"http://localhost:5000/analyze/detect/goal?UUID={UUID}&vest_color1={vest_color1}&vest_color2={vest_color2}")
    if response.status_code != 200:
        pass
    
    response = requests.get(f"http://localhost:5000/analyze/detect/player?UUID={UUID}&vest_color1={vest_color1}&vest_color2={vest_color2}")
    if response.status_code != 200:
        pass

    response = requests.get(f"http://localhost:5000/analyze/make/heatmap?UUID={UUID}&vest_color1={vest_color1}&vest_color2={vest_color2}")
    if response.status_code != 200:
        pass

    return render_template('analyze_video.html', uuid=UUID)

@app.route('/result', methods=['GET', 'POST'])
def result():
    return render_template('result.html')