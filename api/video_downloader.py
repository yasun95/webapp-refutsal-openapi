import os
from pytube import YouTube

class VideoDownloader:
    def download(self, video_url, filename):
        yt = YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        stream.download(filename=filename)

    def progress(self, video_url, video_path):
        # Need to change
        # directory name : uuid , file name : date + time + '.avi'
        progress = 0
        try:
            yt = YouTube(video_url)
            stream = yt.streams.get_highest_resolution()
            total_size = stream.filesize
            downloaded_size = os.path.getsize(video_path)
            progress = downloaded_size / total_size * 100 if total_size != 0 else 0

            # Download size
            # print('ts : ',total_size, 'ds : ', downloaded_size)

        except Exception as e:
            print("Please wait a second...")

        return progress