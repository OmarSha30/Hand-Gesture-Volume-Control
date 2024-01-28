import cv2
import time
import numpy as np
import HTModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


camWidth, camHeight = 1280, 720

win_name = 'Camera Preview'
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)

source = cv2.VideoCapture(0)
source.set(3, camWidth)
source.set(4, camHeight)
prev_time = 0

detect = htm.handDetector(min_detection_confidence=0.7, maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()


#volume bar 
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (255, 0, 0)


while True:
    is_frame, frame = source.read()

    curr_time = time.time()
    fps = 1/(curr_time-prev_time)
    prev_time = curr_time
    cv2.putText(frame, f'FPS:{int(fps)}', (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (0,255,0),3)
    #find hand
    frame = detect.findHands(frame)
    lmlst, box = detect.findPosition(frame, draw=True)
    
    if len(lmlst)!=0:
        #print(lmlst[4], lmlst[8])

        x1, y1 = lmlst[4][1], lmlst[4][2]
        x2, y2 = lmlst[8][1], lmlst[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv2.circle(frame, (x1,y1), 15, (255,0,255), cv2.FILLED)
        cv2.circle(frame, (x2,y2), 15, (255,0,255), cv2.FILLED)
        cv2.line(frame, (x1,y1), (x2,y2), (255,0,255), 3)
        cv2.circle(frame, (cx,cy), 15, (255,0,255), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)

        # hand_range = 50 to 300
        # vol_range = -65 to 0

        vol = np.interp(length, [50,300], [minVol, maxVol])
        volBar = np.interp(length, [50,300], [400, 150])
        volPer = np.interp(length, [50,300], [0, 100])
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
           cv2.circle(frame, (cx,cy), 15, (0, 255, 0), cv2.FILLED) 

        cv2.rectangle(frame, (50, 150), (85, 400), (250,0,0),3)
        cv2.rectangle(frame, (50, (int(volBar))), (85, 400), (250,0,0),cv2.FILLED)
        cv2.putText(frame, f'{int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (250,0,0), 3)

        #filter
        # area = (box[2] - box[0]) * (box[3] - box[1]) // 100
        # if 250 < area < 1000:
        #     length, frame, lineinfo = detect.findDistance(4,8,frame)

    cv2.imshow(win_name, frame)
    key = cv2.waitKey(1)
    if key == 27 or key == ord('x'):
        break

