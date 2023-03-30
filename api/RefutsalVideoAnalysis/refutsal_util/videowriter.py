import cv2
import os
import sys
# from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

class videoWriter:
    """
    원본 비디오에서 일부 구간 추출해 따로 저장
    example code
    video_path = 'F:\\test_video\\goal_sample'
    videoname = 'test_goal.avi'
    vm =videoWriter()
    vm.setOriginVideo(videopath, videoname) # 원본 영상 지정
    output_number = 2
    vm.makeClip(100, output_number) #골 넣은 프레임, 출력파일 넘버
    """
    def __init__ (self):
        self.out = None
        self.origin_vid_path = None
        self.origin_vid_name = None
        self.write_path = None

        self.filename = None
        self.fps = None
        self.w = None
        self.h = None

        self.foward_margin = 100
        self.back_margin = 100
    def setOriginVideo(self, origin_vid_path, origin_vid_name): # 클립 추출할 원본영상설정
        self.origin_vid_path = origin_vid_path
        self.origin_vid_name = origin_vid_name
        self.origin_vid = cv2.VideoCapture(os.path.join(origin_vid_path,origin_vid_name))
        if not self.origin_vid.isOpened():
            print("fail to open video")
            sys.exit()
        self.fps = self.origin_vid.get(cv2.CAP_PROP_FPS)
        self.w = self.origin_vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.h = self.origin_vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.length = self.origin_vid.get(cv2.CAP_PROP_FRAME_COUNT)
        self.origin_vid.release()
    def setWritePath(self, write_path): #클립 작성할 경로설정(directory)
        self.write_path = write_path
    def setMargin(self, foward_margin, back_margin): #골 프레임 기준 앞뒤 프레임기준 마진
        self.foward_margin = foward_margin
        self.back_margin = back_margin
    def setTimeMargin(self, foward_margin, back_margin): #골 프레임 기준 앞뒤 시간기준 마진

        self.foward_margin = foward_margin*self.fps
        self.back_margin = back_margin*self.fps
    def makeClip(self, center_frame, output_num=None, output_name=None): #클립 생성
        start_frame, end_frame = self.__clipBoundary(center_frame)
        start_time = int(start_frame/self.fps)
        end_time = int(end_frame/self.fps)
        videoname, ext = os.path.splitext(self.origin_vid_name)
        if output_name ==None:
            output_filename = videoname+"_goal"+str(output_num)+ext
        else:
            output_filename = videoname + output_name+ext
        origin_path = os.path.join(self.origin_vid_path, self.origin_vid_name)
        output_path = os.path.join(self.write_path, output_filename)
        # ffmpeg_extract_subclip(origin_path, start_time, end_time, output_path)
    def getFrameLength(self):
        return self.length
    def getFPS(self):
        return self.fps
    def __clipBoundary(self, center):
        if center-self.foward_margin > 0:
            start_frame = center-self.foward_margin
        else:
            start_frame = 0
        if center+self.back_margin < self.length:
            end_frame = center+self.back_margin
        else:
            end_frame=self.length
        return start_frame, end_frame