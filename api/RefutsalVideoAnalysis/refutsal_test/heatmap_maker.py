import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import pandas as pd
# 시계열로 히트맵 변화 보여줌
ROOT = "C:\\dev_program\\RefutsalVideoAnalysis"
CSV_PATH = 'C:\\dev_program\\Refutsal_Dev_Repo\\data\\output\\test.csv'
CSV_PATH = 'C:\\dev_program\\Refutsal_Dev_Repo\\data\\output\\leave15.csv'
import matplotlib.pyplot as plt
import numpy as np
import csv
from matplotlib.animation import FuncAnimation

def readCsv(file_path):
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        return [row for row in csv_reader]

data = [[1,0,0,1,-11444,322,2],
        [1,0,0,1,-13333,-2001,2],
        [1,32,0,0,-14653,1690,2],
        [1,32,0,0,-15925,1338,1],
        [1,32,0,0,-15132,-221,1]]

data = readCsv(CSV_PATH)


fig = plt.figure()
fps = 25
video_time = 600
sampling_time = 10   
overlap = 3

def update(frame):
    time_min = int(frame-sampling_time*overlap)
    time_max = int(frame)
    print(time_min,"~", time_max)
    team_1 = [i for i in data if (i[3] == '1') and (time_min*fps<int(i[0])) and (int(i[0])<time_max*fps)]
    team_2 = [i for i in data if i[3] == '2' and time_min*fps<int(i[0]) and int(i[0])<time_max*fps]
    ball = [i for i in data if i[1]=='32' and time_min*fps<int(i[0])and int(i[0])<time_max*fps]

    xedges = [i for i in range(-16000, 16000, 1000)]
    yedges = [i for i in range(-8000,8000,1000)]

    team1_x = [int(i[4]) for i in team_1]
    team1_y = [int(i[5]) for i in team_1]
    team2_x = [int(i[4]) for i in team_2]
    team2_y = [int(i[5]) for i in team_2]
    ball_x = [int(i[4]) for i in ball]
    ball_y = [int(i[5] )for i in ball]

    heatmap_team1, xedges, yedges = np.histogram2d(team1_x, team1_y, bins=(xedges,yedges))
    heatmap_team2, xedges, yedges = np.histogram2d(team2_x, team2_y, bins=(xedges,yedges))
    heatmap_ball, _, _ = np.histogram2d(ball_x, ball_y, bins=(xedges,yedges))

    extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]


    rows = 1
    cols = 3
    cmap = 'hot'
    ax1 = fig.add_subplot(rows, cols, 1)
    ax1.imshow(heatmap_team1, cmap=cmap, extent=extent)
    ax1.axis("off")
    ax1.set_title("team 1")

    ax2= fig.add_subplot(rows,cols, 2)
    ax2.imshow(heatmap_team2, cmap=cmap, extent=extent)
    ax2.axis("off")
    ax2.set_title("team 2")

    ax3 = fig.add_subplot(rows, cols, 3)
    ax3.imshow(heatmap_ball, cmap=cmap, extent=extent)
    ax3.axis("off")
    ax3.set_title("ball")
    print(frame)

print(np.linspace(0,video_time*fps,int(video_time/sampling_time)))
print(data[-1])
ani = FuncAnimation(fig, update, frames=np.linspace(0,video_time,int(video_time/sampling_time)), interval=60)
plt.show()
#ani.save("heatmap_animation.mp4", writer="ffmpeg")
