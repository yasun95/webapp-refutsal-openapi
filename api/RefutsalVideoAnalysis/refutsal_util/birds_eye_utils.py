import cv2
import numpy as np
import sys
import os
def mouse_event(event, x, y, flags, param):
    
    #cv2.resizeWindow(winname="point_setting", width= 1024, height=648)
    if event == cv2.EVENT_LBUTTONUP:
        print(x, y)
        cv2.circle(param, (x,y), 3, (0,0,255), 3)
        cv2.putText(param, str((x,y)), (x, y), 3, 2, (0,0,0))
        cv2.imshow("point_setting", param)

    if flags == cv2.EVENT_FLAG_CTRLKEY:
        path = os.getcwd()
        path = os.path.dirname(os.path.realpath(__file__))
        file_name = "get_points.jpg"
        print("save path = ",path)
        cv2.imwrite(os.path.join(path, file_name),param)
        print("save path = ",os.path.join(path, file_name))
        cv2.destroyWindow("point_setting")


    
def getpoint(img):
    cv2.namedWindow("point_setting", cv2.WINDOW_NORMAL)

    cv2.imshow("point_setting", img)
    cv2.setMouseCallback("point_setting", mouse_event, img)
    print("Sellect point on img\n save img : ctrl")

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return img
        

def showBirdsEyeView(player_pos, color = (255,0,0)):
    meter2fix = 80
    margin = int(0.5*meter2fix)
    rows = int(17*meter2fix+ margin*2) #경기장 사이즈
    cols = int(34*meter2fix+ margin*2)
    
    x= 5.0564
    y = 2.5617
    point_color = (0, 0, 255)
    white_color = (255,255,255)
    #new_Board = np.ones((rows, cols, 3), dtype = np.uint8)*([0,255,0])
    new_board = np.full((rows, cols, 3), (71,193,129), dtype = np.uint8)
    new_board = cv2.circle(new_board, (int(cols/2), int(rows/2)), 100, white_color, 10)
    new_board = cv2.rectangle(new_board, (margin, margin), (cols-margin, rows-margin), white_color, 10)
    new_board = cv2.line(new_board, (int(cols/2), margin),(int(cols/2), rows-margin), white_color, 10)

    i = 0
    if len(player_pos) == 0 :
        player_pos= np.empty((0,2), int)

    #player_pos= np.array([78,530,1674],[587,457,500])

    for footpoint in player_pos:
        new_board = cv2.circle(new_board, (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), 10, point_color, 10)
        new_board = cv2.putText(new_board, str(i), (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), cv2.FONT_HERSHEY_COMPLEX, 1 , color)
        print(i, footpoint/1000)
        i=i+1
    cv2.namedWindow("ground", cv2.WINDOW_NORMAL)
    cv2.imshow("ground", new_board)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def getStadium(teamA, teamB, teamX):
    meter2fix = 80
    margin = int(0.5*meter2fix)
    rows = int(17*meter2fix+ margin*2) #경기장 사이즈
    cols = int(34*meter2fix+ margin*2)

    white_color = (255,255,255)
    new_board = np.full((rows, cols, 3), (71,193,129), dtype = np.uint8)
    new_board = cv2.circle(new_board, (int(cols/2), int(rows/2)), 100, white_color, 10)
    new_board = cv2.rectangle(new_board, (margin, margin), (cols-margin, rows-margin), white_color, 10)
    new_board = cv2.line(new_board, (int(cols/2), margin),(int(cols/2), rows-margin), white_color, 10)
    i = 0
    for footpoint in teamA:
        new_board = cv2.circle(new_board, (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), 10, (0,255,0), 10)
        new_board = cv2.putText(new_board, str(i), (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), cv2.FONT_HERSHEY_COMPLEX, 1 , (0,255,0))
        print(i, footpoint/1000)
        i=i+1
    for footpoint in teamB:
        new_board = cv2.circle(new_board, (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), 10, (255,0,0), 10)
        new_board = cv2.putText(new_board, str(i), (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), cv2.FONT_HERSHEY_COMPLEX, 1 , (255,0,0))
        print(i, footpoint/1000)
        i=i+1
    for footpoint in teamX:
        new_board = cv2.circle(new_board, (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), 10, (0,0,0), 10)
        new_board = cv2.putText(new_board, str(i), (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), cv2.FONT_HERSHEY_COMPLEX, 1 , (0,0,0))
        print(i, footpoint/1000)
        i=i+1
    cv2.namedWindow("result", cv2.WINDOW_NORMAL)
    cv2.imshow("result", new_board)
    cv2.waitKey(0)
    return new_board

def getBirdsEyeImg(new_board, player_pos, color = (255,0,0)):

    i = 0
    if len(player_pos) == 0 :
        player_pos= np.empty((0,2), int)

    #player_pos= np.array([78,530,1674],[587,457,500])
    meter2fix = 80
    margin = int(0.5*meter2fix)
    rows = int(17*meter2fix+ margin*2) #경기장 사이즈
    cols = int(34*meter2fix+ margin*2)
    for footpoint in player_pos:
        new_board = cv2.circle(new_board, (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), 10, color, 10)
        new_board = cv2.putText(new_board, str(i), (int(cols/2+footpoint[0]/1000*meter2fix), int(rows/2-footpoint[1]/1000*meter2fix)), cv2.FONT_HERSHEY_COMPLEX, 1 , color)
        print(i, footpoint/1000)
        i=i+1
    return new_board

def getImage(path, frame, size=1):
    video = cv2.VideoCapture(path)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame)

    if not video.isOpened():
        print(" Could not Open %s", path)
        exit(0)

    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    ret, image0 = video.read()

    image0 = cv2.resize(image0, (int(width*size), int(height*size)))
    video.release()
    return image0

def showGrid(fname, frame_point, ground_point):
    name, exp = os.path.splitext(fname)
    if exp == '.jpg':
        img = cv2.imread(fname)
    elif exp == '.avi' or exp == '.mp4':
        img = getImage(fname, 10)
    else:
        raise("fname must be .jpg, .avi, .mp4")
    if len(frame_point) != len(ground_point):
        print("[warnning] frame point != ground_point")
    
    points_i = min(len(frame_point), len(ground_point))
    for i in range(points_i):
        print(i, (frame_point[i][0],frame_point[i][1]))
        cv2.circle(img, (int(frame_point[i][0]),int(frame_point[i][1])), 10, (0,0,255),10)
        cv2.putText(img, str((ground_point[i][0],ground_point[i][1])),(int(frame_point[i][0]),int(frame_point[i][1])),5,2,(0,0,0))

    cv2.namedWindow("check_grid", cv2.WINDOW_NORMAL)
    cv2.imshow("check_grid", img)
    cv2.waitKey(0)


