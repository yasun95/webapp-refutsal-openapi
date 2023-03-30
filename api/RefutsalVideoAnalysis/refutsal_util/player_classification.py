#!/usr/bin/python3
import argparse

import cv2
#import cv2.aruco as aruco
import numpy as np


# def get_args():
#     parser = argparse.ArgumentParser()

#     parser.add_argument("--video-cap", type=bool, default=True)

#     parser.add_argument("--kernel", type=tuple, default=(5,5))

#     parser.add_argument("--bbox-area", type=int, default=150)
#     parser.add_argument("--bbox-length", type=int, default=120)

#     args = parser.parse_args()

#     return args


def create_data_form(data_len):
    team = np.zeros((data_len, 1), dtype=np.int16)
    playerid = np.zeros((data_len, 1), dtype=np.int16)

    return team, playerid


def find_team_and_id(img, id, marker_size=4, total_markers=50, draw=True):
     # ArUco id
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(aruco, f'DICT_{marker_size}X{marker_size}_{total_markers}')
    arucoDict = aruco.Dictionary_get(key)
    arucoParam = aruco.DetectorParameters_create()
    bbox, ids, _ = aruco.detectMarkers(gray, arucoDict, parameters=arucoParam)

    if draw:
        aruco.drawDetectedMarkers(img, bbox)

    if ids is not None:
        for i in range(0,len(ids)):
            if ids[i,0] is None:
                ids[i,0] = 0
            id[i] = ids[i,0]

    else:
        id = np.zeros((len(id), 1), dtype=np.int16)
        pass

    return id


def background_subtractor(img, algorithm):
    fgmask = algorithm.apply(img)
    ret, th_ = cv2.threshold(fgmask, 10, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    dst = cv2.copyTo(img, th_)

    return dst, fgmask


def get_color_range(color):
    if color == "blue" or color == "BLUE":
        lower_blue = np.array([105,100,100])
        upper_blue = np.array([125,255,255])

        return lower_blue, upper_blue

    elif color == "red" or color == "RED":
        lower_red = np.array([170,100,50])
        upper_red = np.array([180,255,255])

        return lower_red, upper_red

    elif color == "green" or color == "GREEN":
        lower_green = np.array([75,100,80])
        upper_green = np.array([95,255,255])
    
        return lower_green, upper_green

    # elif color == "orange" or color == "ORANGE":
    #     lower_orange = np.array([0,180,50])
    #     upper_orange = np.array([20,255,255])

    #     return lower_orange, upper_orange

    elif color == "yellow" or color == "YELLOW":
        lower_yellow = np.array([15,100,50])
        upper_yellow = np.array([35,255,255])

        return lower_yellow, upper_yellow


def img_processing(img):
    # args = get_args()
    kernel = (5,5)

    bgr = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
    blur = cv2.GaussianBlur(bgr, kernel, 3.5)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    ret, th_ = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    closing = cv2.morphologyEx(th_, cv2.MORPH_CLOSE, np.ones(kernel, dtype=np.float32), iterations=3)

    return blur, closing


def create_color_mask(img, lower1, upper1, lower2, upper2):    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)

    result1 = cv2.bitwise_and(img, img, mask=mask1)
    result2 = cv2.bitwise_and(img, img, mask=mask2)

    bgr1, result1 = img_processing(result1)
    bgr2, result2 = img_processing(result2)

    result_all = cv2.add(result1, result2)

    return result1, result2, result_all


# Not Used
def rediscovery_color_in_contour_bbox(img, array, w, h):
    #cv2.rectangle(img, (array[0], array[1], w, h), (255,0,255), 2)
    cut_image = img[array[1]:array[1]+h, array[0]-10:array[0]-10+w]

    return cut_image


# Used
# Plan A - find_contours
def create_bbox_detect_color_contours(img, binary_img, data, color, lower1, upper1, lower2, upper2, team, num=0):
    # args = get_args()
    # min_bbox_area = args.bbox_area
    # min_bbox_length = args.bbox_length    
    
    min_bbox_area = 150
    min_bbox_length = 120

    contours, hier = cv2.findContours(binary_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

    team = np.zeros((len(data[:,5]), 1), dtype=np.int16)
    contours_array = np.empty((0,1), dtype=np.uint16)
    array_size = 0

    # Data Mining Program
    #yolo_path = args.yolo_path
    #num += 1
    #text_num = format(num, '04')
    #tf = open(yolo_path + "/vest_labels/" + text_num + ".txt", 'w')

    for j in range(len(contours)):
        area = cv2.contourArea(contours[j])
        length = cv2.arcLength(contours[j], True)
        if area > min_bbox_area and length > min_bbox_length:
            contours_array = np.insert(contours_array, array_size, j)
            array_size += 1

    contours_array_sorted = np.asarray(contours_array)
    contours_array_copy = np.asarray(contours_array)

    for k in range(array_size):
        x, y, w, h = cv2.boundingRect(contours[contours_array[k]])
        contours_array_sorted = np.insert(contours_array_sorted, k, x)
        contours_array_sorted = np.delete(contours_array_sorted, -1)
    
    contours_array_copy = np.column_stack([contours_array, contours_array_sorted])
    contours_array_copy = np.array(sorted(contours_array_copy, key = lambda x : x[1]))

    for l in range(array_size):
        contours_array = np.insert(contours_array, l, contours_array_copy[l,0])
        contours_array = np.delete(contours_array, -1)

    #print("contour array : " ,contours_array)
    #print("contour size : ", len(contours_array))
    #print("array size : ", array_size)
    #print(len(team))
    for i in range(array_size):
        #print(array_size)
        #print("i : ", i)
        #print("contour : ", len(contours))
        #print("data : ", len(data))
        #print("x1 : ", data[i,0]," y1 : ", data [i,1]," x2 : ", data[i,2]," y2 : ",data [i,3])

        #cv2.drawContours(img, [contours[contours_array[i]]], 0, (0,0,255), 2)
        #cv2.putText(img, str(i), tuple(contours_array[i][0][0]), cv2.FONT_HERSHEY_COMPLEX, 0.8, color, 1)
        #print(i, hier[0][i], area, length)

        x, y, w, h = cv2.boundingRect(contours[contours_array[i]])

        # Vest Label's Argument x, y, w, h
        #x1 = round(((x + (x+w)) / 2) / img.shape[1], 6)
        #y1 = round(((y + (y+h)) / 2) / img.shape[0], 6)
        #x2 = round(w / img.shape[1], 6)
        #y2 = round(h / img.shape[0], 6)

        #print("contour box")
        #print("x1 : ", x," y1 : ", y," x2 : ", x+w ," y2 : ", y+h)
        #print("x1 : ", int(data[i,0])," y1 : ", int(data[i,1])," x2 : ", int(data[i,2]) ," y2 : ", int(data[i,3]))
        #for i in contours[contours_array]:

        # Bounding Box
        
        try:
            #Before bbox range
            #cv2.rectangle(img, (int(data[i,0]+interval),int(data[i,1]+interval+10)), (int(data[i,2]-interval*2), int((data[i,1]+data[i,3])/2+interval*3)), (255,255,255), 3)
            #cv2.rectangle(img, (int(x+(w/4)+interval/2),int(y+(h/4)+interval/2)), (int(x+w-interval/2),int(y+h-interval/2)), (0,255,0),3)

            # After bbox range
            cv2.rectangle(img, (int(x+(w/3)),int(y+(h/3))), (int(x+(w*2/3)),int(y+(h*2/3))), (0,255,0),3)
            #cv2.rectangle(img, (int(data[i,0]), int(data[i,1])), (int(data[i,2]), int(data[i,3])), (255,255,255), 3)
            #cv2.rectangle(img, (int((5*data[i,0]+data[i,2])/6),int((5*data[i,1]+data[i,3])/6)), (int((data[i,0]+5*data[i,2])/6),int((data[i,1]+5*data[i,3])/6)), (255,0,255), 3)
        except Exception:
            pass
        

        dst = img[y:y+h, x:x+w]

        dst_hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)
        rows, cols = dst_hsv.shape[:2]

        # Vest Label Text File Maker
        #text_num = format(num, '04')
        #tf = open(yolo_path + "/vest_labels/" + text_num + ".txt", 'a')

        #cv2.imshow("vest", dst)
        #cv2.waitKey(0)

        #if my recognition box in yolo box?:
        #data[:,0] = x1, data[:,1] = y1, data[:,2] = x2, data[:,3] = y2
        for j in range(len(data[:,5])):
            try:
                '''
                print("j : ", j)
                print(contours_array[j])
                
                # Bounding Box
                print("my x1 : ", x," my y1 : ", y," my x2 : ", x+w ," my y2 : ", y+h)
                print("yolo x1 : ", int(data[j,0])," yolo y1 : ", int(data[j,1])," yolo x2 : ", int(data[j,2]) ," yolo y2 : ", int(data[j,3]))
                '''
                
                if j > 0:
                    #Before bbox range
                    #cv2.rectangle(img, (int(data[j-1,0]),int(data[j-1,1]+interval)), (int((data[j-1,0]+data[j-1,2])/2+interval*2), int((data[j-1,1]+data[j-1,3])/2+interval*3)), (0,0,0), 3)
                #cv2.rectangle(img, (int(data[j,0]+interval/2),int(data[j,1]+interval)), (int((data[j,0]+data[j,2])/2+interval*2), int((data[j,1]+data[j,3])/2+interval*3)), (255,0,255), 3)
                    
                    #Afrter bbox range
                    cv2.rectangle(img, (int(data[j-1,0]), int(data[j-1,1])), (int(data[j-1,2]), int(data[j-1,3]*9/10)), (255,0,255), 3)
                #cv2.rectangle(img, (int(data[j,0]), int(data[j,1])), (int(data[j,2]), int(data[j,3])), (255,255,255), 3)
                #cv2.rectangle(img, (int(data[j+1,0]), int(data[j+1,1])), (int(data[j+1,2]), int(data[j+1,3])), (0,255,255), 3)

                    #cv2.rectangle(img, (int((5*data[j-1,0]+data[j-1,2])/6),int((5*data[j-1,1]+data[j-1,3])/6)), (int((data[j-1,0]+5*data[j-1,2])/6),int((data[j-1,1]+5*data[j-1,3])/6)), (255,255,255), 3)
                #cv2.rectangle(img, (int((5*data[j,0]+data[j,2])/6),int((5*data[j,1]+data[j,3])/6)), (int((data[j,0]+5*data[j,2])/6),int((data[j,1]+5*data[j,3])/6)), (255,255,255), 3)

                #if int(data[j,0]) < int(x+(w/3)) and int(data[j,1]+interval) < int(y+(h/3)) and int(x+(w*2/3)) < int(data[j,2]-interval*2) and int(y+(h*2/3)) < int((data[j,1]+data[j,3])/2+interval*3):
                if int(data[j,0]) < int(x+(w/3)) and int(data[j,1]) < int(y+(h/3)) and int(x+(w*2/3)) < int(data[j,2]) and int(y+(h*2/3)) < int((data[j,3]*9/10)):
                    if lower1[0] < dst_hsv[int(rows/4), int(cols/4)][0] < upper1[0] or lower1[0] < dst_hsv[int(rows/2), int(cols/2)][0] < upper1[0] or lower1[0] < dst_hsv[int(rows*3/4), int(cols*3/4)][0] < upper1[0] or lower1[0] < dst_hsv[int(rows*2/3), int(cols*2/3)][0] < upper1[0]:
                        cv2.putText(img, str("1"), tuple(contours[contours_array[i]][0][0]), cv2.FONT_HERSHEY_COMPLEX, 0.8, color, 1)
                        cv2.rectangle(img, (int(data[j,0]), int(data[j,1])), (int(data[j,2]), int(data[j,3]*9/10)), (255,255,255), 3)
                        #print("Team : 1")
                        team = np.insert(team, j, 1)
                        team = np.delete(team, j + 1)
                        break

                    elif lower2[0] < dst_hsv[int(rows/4), int(cols/4)][0] < upper2[0] or lower2[0] < dst_hsv[int(rows/2), int(cols/2)][0] < upper2[0] or lower2[0] < dst_hsv[int(rows*3/4), int(cols*3/4)][0] < upper2[0] or lower2[0] < dst_hsv[int(rows*2/3), int(cols*2/3)][0] < upper2[0]:
                        cv2.putText(img, str("2"), tuple(contours[contours_array[i]][0][0]), cv2.FONT_HERSHEY_COMPLEX, 0.8, color, 1)
                        cv2.rectangle(img, (int(data[j,0]), int(data[j,1])), (int(data[j,2]), int(data[j,3]*9/10)), (255,255,255), 3)
                        #print("Team : 2")
                        team = np.insert(team, j, 2)
                        team = np.delete(team, j + 1)
                        break

                    if j == len(data[:,5])-1:
                        cv2.putText(img, str("0"), tuple(contours[contours_array[i]][0][0]), cv2.FONT_HERSHEY_COMPLEX, 0.8, color, 1)
                        cv2.rectangle(img, (int(data[j,0]), int(data[j,1])), (int(data[j,2]), int(data[j,3]*9/10)), (255,255,255), 3)
                        #print("Team : None")
                        team = np.insert(team, j, 0)
                        team = np.delete(team, j + 1)
                        break

                #cv2.imshow("yaho", img)
                #cv2.waitKey(0)
            except Exception:
                pass
        #print(team)

        # Data Maining Label
        '''    
        tf.write(str(cls_idx) + " ")
        tf.write(str(x1) + " ")
        tf.write(str(y1) + " ")
        tf.write(str(x2) + " ")
        tf.write(str(y2) + "\n")
        '''

    team = np.column_stack([team])
    #tf.close()


    return img, team


# Not Used
# Plan B - Labeling 
def create_bbox_detect_color_labeling(img, src, min_bbox_area, count = 0):
    cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(img)
    for i in range(1, cnt):
        x, y, w, h, area = stats[i]
        if area < min_bbox_area:
            continue

        else:
            count = 1
            cv2.rectangle(src, (x,y,w,h), (0,0,255), 2)

        return count