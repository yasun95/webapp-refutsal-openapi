import cv2

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

def getimages(paths, frames):
    videoplayer = []
    images =[]
    for path in paths:
        videoplayer.append(cv2.VideoCapture(path))

    for n, video in enumerate(videoplayer):
        video.set(cv2.CAP_PROP_POS_FRAMES, frames[n])
        if not video.isOpened():
            print(" Could not Open %s", paths[n])
            exit(0)
        
        width = int(videoplayer[n].get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(videoplayer[n].get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(width, height)
        ret, img = video.read()
        img = cv2.resize(img, (int(width*0.18), int(height*0.18)))
        images.append(img)
        video.release()
    return images
