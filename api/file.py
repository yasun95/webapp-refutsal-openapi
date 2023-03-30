def download_video(video_url, filename, uuid):
    global video_size
    try:
        youtube = YouTube(video_url)
        video = youtube.streams.get_highest_resolution()
        video_size = video.filesize
        video.download(filename=filename)
    except (NameError, UnboundLocalError):
        pass

def download_function(video_path, video_size, uuid):
    # Need to change
    # directory name : uuid , file name : date + time + '.avi'
    # global video_size
    try:
        total_size = video_size
        downloaded_size = os.path.getsize(video_path)
        return downloaded_size / total_size * 100 if total_size != 0 else 0
    except (NameError, UnboundLocalError):
        pass

    # download_dir = os.path.abspath(f"api/resources/saved_videos/{uuid}")
    # os.makedirs(download_dir, exist_ok=True)
    # video_path = os.path.join(download_dir, filename)

    # youtube = YouTube(video_url)
    # video = youtube.streams.get_highest_resolution()
    # video_size = video.filesize

@app.route('/download', methods=['POST'])
def download():
    args = match_info_args.parse_args()
    result = MatchInfo(uuid=args['uuid'], camnum=args['camnum'], vest_color1=args['vest_color1'], vest_color2=args['vest_color2'], youtube_url=args['youtube_url'])
    # db.session.add(result)
    # db.session.commit()

    uuid = request.form['uuid']
    camnum = request.form['camnum']
    vest_color1 = request.form['vest_color1']
    vest_color2 = request.form['vest_color2']
    youtube_url = request.form['youtube_url']

    users[uuid] = {
        'camnum': camnum,
        'vest_color1': vest_color1,
        'vest_color2': vest_color2
    }

    filename = uuid +'.avi'
    download_dir = os.path.abspath('api/resources/videos/')
    os.makedirs(download_dir, exist_ok=True)
    video_path = os.path.join(download_dir, filename)

    download_thread = threading.Thread(target=download_video, args=(youtube_url, video_path))
    download_thread.start()

    return jsonify({'name': uuid})


@app.route('/downloading')
def downloading():
    def generate():
        # get the filename for the user's video
        uuid = request.args.get('uuid')
        filename = uuid + '.avi'
        file_size = os.path.getsize(filename)

        # wait for the file to be created, with timeout and max retries
        retries = 0
        while not os.path.exists(filename):
            time.sleep(1)
            retries += 1
            if retries > 5: # give up after 5 seconds
                return "Error: File not found"

        # send progress updates until the file is fully downloaded
        loaded_size = 0
        while loaded_size < file_size:
            loaded_size = os.path.getsize(filename)
            percent = int(loaded_size / file_size * 100)
            data = {'percent': percent}
            yield 'data: %s\n\n' % json.dumps(data)
            time.sleep(1)

        # redirect to the analyze page
        data = {'percent': 100}
        yield 'data: %s\n\n' % json.dumps(data)
        return Response(status=204)

    # return a response with the SSE content type
    return Response(generate(), mimetype='text/event-stream')


# @app.route('/analyze/<uuid>')
# def analyze(uuid):
#     user = users.get(uuid)
#     return render_template('analyze_video.html', user=user)

# @app.route('/analyzing')
# def analyze_progress():
#     def generate():
#         # get the filename for the user's video
#         uuid = request.args.get('uuid')
#         filename = uuid + '.avi'
#         file_size = os.path.getsize(filename)

#         while not os.path.exists(filename):
#             time.sleep(1)

#         # send progress updates until the file is fully analyzed
#         analyzed_size = 0
#         while analyzed_size < file_size:
#             analyzed_size = os.path.getsize(filename)
#             percent = analyzed_size / file_size * 100
#             data = {'percent': percent}
#             yield 'data: {}\n\n'.format(json.dumps(data))
#             time.sleep(1)

#         # run the analysis and get the results
#         results = run_analysis(filename)

#         # return the results to the client
#         return jsonify(results)

#     # return a response with the SSE content type
#     return app.response_class(generate(), mimetype='text/event-stream')




import youtube_dl
import cv2
from flask import request, send_file, Response
from flask_restful import Resource
from .app import db
from models import MatchInfo
import os
import time

class VideoResource(Resource):
    def get(self, uuid):
        match = MatchInfo.query.filter_by(uuid=uuid).first()

        import requests
        import json

        url = "http://127.0.0.1:5000"
        headers = {'Content-Type': 'application/json'}
        data = {"video_url": "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"}

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if not match:
            return {'message': 'Match not found'}, 404

        return match.to_dict(), 200

    def post(self):
        json_data = request.get_json(force=True)
        video_url = json_data.get('video_url')
        cam_num = json_data.get('cam_num')
        vest_color = json_data.get('vest_color')

        # Download video and extract video info
        ydl_opts = {
            'default_search': 'ytsearch',
            'quiet': True,
            'skip_download': True,
            'no_check_certificate': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(video_url, download=False)
            video_title = video_info['title']
            video_thumbnail = video_info['thumbnail']
            video_duration = video_info['duration']
            video_filename = f"{video_title.replace(' ', '_')}.mp4"
            ydl_opts['outtmpl'] = video_filename
            ydl.download([video_url])

        # Analyze video for vest detection
        video_capture = cv2.VideoCapture(video_filename)
        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        detected_frames = 0
        for i in range(total_frames):
            ret, frame = video_capture.read()
            if not ret:
                break

            # Use cv2 to detect the vest color in the frame
            # Replace the following line with your vest detection code
            vest_detected = True

            # If vest is detected, update the count and save the frame
            if vest_detected:
                detected_frames += 1
                cv2.imwrite(f"{i}.jpg", frame)

            # Update loading bar progress every second
            if i % int(video_capture.get(cv2.CAP_PROP_FPS)) == 0:
                progress = int((i / total_frames) * 100)
                yield f"data: {progress}\n\n"
                time.sleep(1)

        # Save match info to database
        match = MatchInfo(cam_num=cam_num, vest_color=vest_color, video_url=video_url)
        db.session.add(match)
        db.session.commit()

        # Clean up temp files
        os.remove(video_filename)
        for i in range(detected_frames):
            os.remove(f"{i}.jpg")

        return match.to_dict(), 201
