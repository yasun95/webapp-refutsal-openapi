# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
"""
Run inference on images, videos, directories, streams, etc.

Usage - sources:
    $ python path/to/detect.py --weights yolov5s.pt --source 0              # webcam
                                                             img.jpg        # image
                                                             vid.mp4        # video
                                                             path/          # directory
                                                             path/*.jpg     # glob
                                                             'https://youtu.be/Zgi9g1ksQHc'  # YouTube
                                                             'rtsp://example.com/media.mp4'  # RTSP, RTMP, HTTP stream

Usage - formats:
    $ python path/to/detect.py --weights yolov5s.pt                 # PyTorch
                                         yolov5s.torchscript        # TorchScript
                                         yolov5s.onnx               # ONNX Runtime or OpenCV DNN with --dnn
                                         yolov5s.xml                # OpenVINO
                                         yolov5s.engine             # TensorRT
                                         yolov5s.mlmodel            # CoreML (macOS-only)
                                         yolov5s_saved_model        # TensorFlow SavedModel
                                         yolov5s.pb                 # TensorFlow GraphDef
                                         yolov5s.tflite             # TensorFlow Lite
                                         yolov5s_edgetpu.tflite     # TensorFlow Edge TPU
"""
import torch
import pandas as pd
import argparse
import os
import platform
import sys
from pathlib import Path
from cv2 import preCornerDetect
import numpy as np
import torch
import torch.backends.cudnn as cudnn

import csv

# SUNJONG's EDIT - Environment folder name
# ROOT_ABS = "C:\dev_program\yolov5" #ROOT = yolov5 path
ROOT_ABS = '/home/yasun95/workspace/flask/open_api_v1/api/RefutsalVideoAnalysis/yolov5'
# REPO_ABS = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) # REPO = ../Refutsal_Dev_Repo
REPO_ABS = '/home/yasun95/workspace/flask/open_api_v1/api/RefutsalVideoAnalysis'
header1 = "{0:_^60}"
header2 = "{0:=^60}"
textline = "{0:<20}{1:<40}"
process_count= 0

if str(ROOT_ABS) not in sys.path:
    sys.path.append(str(ROOT_ABS))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT_ABS, Path.cwd()))  # relative

if str(REPO_ABS) not in sys.path:
    sys.path.append(str(REPO_ABS))  # add ROOT to PATH
REPO = Path(os.path.relpath(REPO_ABS, Path.cwd()))  # relative

from yolov5.models.common import DetectMultiBackend
from yolov5.utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from yolov5.utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args, scale_boxes, scale_segments, strip_optimizer, xyxy2xywh)
from yolov5.utils.plots import Annotator, colors, save_one_box
from yolov5.utils.torch_utils import select_device, time_sync

from refutsal_util.player_classification import create_data_form, background_subtractor, get_color_range, img_processing, create_color_mask, create_bbox_detect_color_contours

def process():
    print(process_count)
    return process_count + 1

@torch.no_grad()
def run(
        weights=ROOT / 'yolov5s.pt',  # model.pt path(s)
        source=REPO / 'input/test_service',  # file/dir/URL/glob, 0 for webcam
        data=ROOT / 'data/coco128.yaml',  # dataset.yaml path
        imgsz=(640, 640),  # inference size (height, width)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img=False,  # show results
        save_txt=False,  # save results to *.txt
        make_csv=True,  # save results to *.csv
        save_birds_eye_image =False,
        save_img= False,
        save_conf=False,  # save confidences in --save-txt labels
        save_crop=False,  # save cropped prediction boxes
        nosave=True,  # do not save images/videos
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        update=False,  # update all models
        ##project=ROOT / 'runs/detect',  # save results to project/name
        project = os.path.join(REPO, "output"),
        name='exp',  # save results to project/name
        exist_ok=False,  # existing project/name ok, do not increment
        line_thickness=3,  # bounding box thickness (pixels)
        hide_labels=False,  # hide labels
        hide_conf=False,  # hide confidences
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
        camera_number=None,
        csv_path=None,
        video_cap=True,
        kernel=(5,5),
        bbox_area=150,
        bbox_length=120,
        vest_color1='',
        vest_color2=''
):
    print(header2.format("Path Data"))
    print(textline.format("ROOT",ROOT_ABS))
    print(textline.format("REPO",REPO_ABS))
    print(textline.format("SOURCE",str(source)))
    print("")

    source = str(source)
    is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
    is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
    webcam = source.isnumeric() or source.endswith('.txt') or (is_url and not is_file)
    if is_url and is_file:
        source = check_file(source)  # download

    # Directories
    save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # increment run
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # Load model
    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  # check image size

    # Dataloader
    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)
    bs = 1  # batch_size

    vid_path, vid_writer = [None] * bs, [None] * bs
    my_vid_path, my_vid_writer = [None] * bs, [None] * bs

    # Run inference
    model.warmup(imgsz=(1 if pt else bs, 3, *imgsz))  # warmup
    seen, windows, dt = 0, [], [0.0, 0.0, 0.0]

    work_path = None
    #run each image or video frame #파일별 동작 
    for path, im, im0s, vid_cap, s in dataset:
        
        #csv maker
        if make_csv == True:
            if work_path != csv_path:
                work_path = csv_path

                filename = os.path.basename(csv_path)
                filename, oper = os.path.splitext(filename)
                
                # SUNJONG EDIT - change the output csv path
                output_csv_path = csv_path

                with open(output_csv_path,'w', newline='') as outcsv:
                    header_wr = csv.DictWriter(outcsv, fieldnames=['frame', 'camnum', 'id', 'team','cls','x', 'y'])
                    header_wr.writeheader()
            else:
                print(header1.format("same file"))
        t1 = time_sync()
        im = torch.from_numpy(im).to(device)
        im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim
        t2 = time_sync()
        dt[0] += t2 - t1

        # Inference
        pred = model(im, augment=augment, visualize=False)
        
        t3 = time_sync()
        dt[1] += t3 - t2

        # NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        dt[2] += time_sync() - t3

        # Process predictions
        if make_csv == True:
            #change write option
            #파일내용 기록
            #f = open(yolo_path + '/runs/yolo_detect.csv','a', newline='') # csv 파일 생성 w: write, a: append
            f = open(output_csv_path,'a', newline='') # csv 파일 생성 w: write, a: append
            wr = csv.writer(f, delimiter=',')
            

        for i, det in enumerate(pred):
            seen += 1
            p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)
            p = Path(p)  # to Path
            save_path = str(save_dir / p.name) 

            s += '%gx%g ' % im.shape[2:]  # print string
            imc = im0.copy() if save_crop else im0  # for save_crop

            annotator = Annotator(im0, line_width=line_thickness, example=str(names))

            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to strinzg

                if make_csv:
                    #csv에 데이터 입력하는 파트
                    det[:, 4]*=100
                    data = np.asarray(det.cpu(), dtype=np.uint16)

                    # Remove cls != 0 (Not Person : Row Index Remove)
                    remover = True
                    for j in range(len(data[:,5])):
                        if remover:
                            k = 0
                            # 클래스 정확도로 거르는 부분
                            if int(data[:,4][j-k]) < 20:
                                #print("j : ", j)
                                data = np.delete(data, j-k, axis=0)
                                remover = False
                                k += 1
                
                    # data x value sorted
                    data = np.array(sorted(data, key = lambda x : x[0]))

                    foot_xy = np.column_stack([(data[:,0]+data[:,2])/2, data[:,3]])
                    foot_xy = np.round(foot_xy).astype(int)
                
                    # remove data rows = data length
                    frame = np.full((len(data[:,5]),1), frame)
                    #cls = data[:,4]
                    cls = data[:,5]

                    # 0 인식안됨, 1팀, 2팀
                    # team, playerid's numpy form
                    team, playerid = create_data_form(len(cls))

                    # Background - Object Subtraction, But runtime is slowing down
                    bg = cv2.createBackgroundSubtractorMOG2(250, 50, False)
                    fg, fgmask = background_subtractor(im0s, bg)

                    # Write in Parameter (Type : String) / color : red, blue, green, orange, yellow
                    lower1, upper1 = get_color_range(vest_color1)
                    lower2, upper2 = get_color_range(vest_color2)

                    mask_vest1, mask_vest2, mask_all = create_color_mask(fg, lower1, upper1, lower2, upper2)
                    detect_team_all, team = create_bbox_detect_color_contours(im0s, mask_all, data, (0,0,255), lower1, upper1, lower2, upper2, team, seen)
                    camnum = np.ones((len(data[:,5]),1), dtype=np.int16)*int(camera_number)

                    try:
                        csv_data = np.column_stack([frame, camnum, playerid, team, cls, foot_xy])
                        print(csv_data)

                    except Exception:
                        team = np.zeros((len(data[:,5]), 1), dtype=np.int16)
                        csv_data = np.column_stack([frame, camnum, playerid, team, cls, foot_xy])

                    csv_data = np.round(csv_data).astype(int)

                    for line in csv_data:
                        wr.writerow(line)

            # Write results on image
            # Stream results
            #my_im0 = annotator2.result() #동영상으로 저장할 이미지 생성
            #초록색 영상 생성
#=================================================================================
            # Save results (image with detections) #비디오, 이미지 나눠지는 부분
            if save_img: 
                if dataset.mode == 'image': # 이미지 저장
                    cv2.imwrite(save_path, im0)
                else:  # 'video' or 'stream'
                    if vid_path[i] != save_path:  # new video
                        vid_path[i] = save_path
                        if isinstance(vid_writer[i], cv2.VideoWriter):
                            vid_writer[i].release()  # release previous video writer
                        if vid_cap:  # video
                            print("vid_cap(write) : ", vid_cap)
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        else:  # stream
                            fps, w, h = 30, im0.shape[1], im0.shape[0]
                        save_path = str(Path(save_path).with_suffix('.mp4'))  # force *.mp4 suffix on results videos
                        vid_writer[i] = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                    vid_writer[i].write(im0)
#============================================================================ 
# critical im0, my_vid_writer, save_path, vid_cap
#그냥 초록색 동영상 생성으로 변경
            if save_birds_eye_image: 
                w = int(200)
                h = int(200)
                my_im0 = np.full((w, h, 3), (71,193,129), dtype = np.uint8)
                if dataset.mode == 'image': # 이미지 저장
                    cv2.imwrite(save_path, my_im0)
                else:  # 'video' or 'stream'
                    if my_vid_path[i] != save_path:  # new video
                        my_vid_path[i] = save_path
                        if isinstance(my_vid_writer, cv2.VideoWriter):
                            my_vid_writer.release()  # release previous video writer
                        if vid_cap:  # video
                            print("vid_cap(write) : ", vid_cap)
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)

                        else:  # stream
                            fps, w, h = 30, my_im0.shape[1], my_im0.shape[0]
                        my_save_path = str(Path(save_path).with_name('my_im0.mp4'))  #이름포함저장# force *.mp4 suffix on results videos
                        print("save_path : ", my_save_path)
                        my_vid_writer = cv2.VideoWriter(my_save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                    my_vid_writer.write(my_im0)
#============================================================================ 

#=============================================================================
        # Print time (inference-only)
        LOGGER.info(f'{s}Done. ({t3 - t2:.3f}s)')
        if make_csv:
            f.close()

    # Print results
    t = tuple(x / seen * 1E3 for x in dt)  # speeds per image
    LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *imgsz)}' % t)
    if save_txt or save_img:
        s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        LOGGER.info(f"Results saved to {colorstr('bold', save_dir)}{s}")
    if update:
        strip_optimizer(weights)  # update model (to fix SourceChangeWarning)
    process()


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default=ROOT / 'yolov5s.pt', help='model path(s)')
    parser.add_argument('--source', type=str, default=REPO / 'input/test_service', help='file/dir/URL/glob, 0 for webcam')
    parser.add_argument('--data', type=str, default=ROOT / 'data/coco128.yaml', help='(optional) dataset.yaml path')
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
    parser.add_argument('--device', default='3', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='show results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', default=[0,32],nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--visualize', action='store_true', help='visualize features')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default=REPO / 'output/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
    parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
    parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    parser.add_argument("--camera-number", type=int, default=2)
    parser.add_argument("--csv-path", type=str, default='')
    parser.add_argument("--video-cap", type=bool, default=True)
    parser.add_argument("--kernel", type=tuple, default=(5,5))
    parser.add_argument("--bbox-area", type=int, default=150)
    parser.add_argument("--bbox-length", type=int, default=120)
    parser.add_argument("--vest-color1", type=str, default='RED')
    parser.add_argument("--vest-color2", type=str, default='BLUE')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
    print_args(vars(opt))
    return opt


def main(opt):
    check_requirements(exclude=('tensorboard', 'thop'))
    run(**vars(opt))


if __name__ == "__main__":
    opt = parse_opt()
    main(opt)