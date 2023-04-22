# Tecsclub - webapp-refutsal-openapi

## Components of open_api_v2

1. RefutsalVideoAnalysis - analysis engine
   1.1 refutsal - main code of analysis engine
   1.2 refutsal_config - futsal stadium config
   1.3 refutasl_util - util code of analysis engine (Protected)
   1.4 yolov5 - open source object detector -> https://github.com/ultralytics/yolov5

2. resources - video of uploaded the youtube & csv or image file of analysis result
3. static - set the image of homepage
4. templates - collect input information from the user & download and analyze the video
5. app - main code of application
   5.1 input_info - request the user to input the requirements information
   5.2 download_video - download the video from the YouTube URL and display a progress bar showing the download process
   5.3 analyze_video - analyze the video and display a progress bar showing the analyze process

6. config - DB & Path config

## Install & Build

Follow the link and install requirements.txt in a Python>=3.8.0 environments, including PyTorch>=1.12.0+cu116.

WINDOWS : https://95mkr.tistory.com/entry/DD1
LINUX : https://95mkr.tistory.com/entry/LINUX5

'''python
git clone https://github.com/yasun95/webapp-refutsal-openapi.git
cd webapp-refutsal-openapi
pip install -r requiremetns.txt
'''
