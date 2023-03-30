from moviepy.editor import *

# Load the videos to be merged
video1 = VideoFileClip("C:\Program Files (x86)\VideoPlayTool\\bin\Device\Download\CAM4\\04_2023-01-18_224500_230000.avi")
video2 = VideoFileClip("C:\Program Files (x86)\VideoPlayTool\\bin\Device\Download\CAM4\\04_2023-01-18_224500_230000.avi")


# Add the videos to a list
videos = [video1, video2]

# Concatenate the videos
final_video = concatenate_videoclips(videos)

# Write the final video to a file
final_video.write_videofile("final_video.mp4")
