import cv2
import sys
import mediapipe as mp
import time

class handDetector():
    def __init__(self,mode=False,maxHands=2,model_complexity=1,min_detection_confidence=0.5,min_tracking_confidence=0.5):
        self.mode=mode
        self.maxHands=maxHands
        self.model_complexity=model_complexity
        self.min_detection_confidence=min_detection_confidence
        self.min_tracking_confidence=min_tracking_confidence
        

        self.mphands = mp.solutions.hands
        self.hands = self.mphands.Hands(self.mode,self.maxHands,self.model_complexity,self.min_detection_confidence, self.min_tracking_confidence)
        self.mpdraw = mp.solutions.drawing_utils

    def findHands(self, frame, draw=True):
        imgrgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.res = self.hands.process(imgrgb)

        #print(res.multi_hand_landmarks)
        if self.res.multi_hand_landmarks:
            for hand in self.res.multi_hand_landmarks:
                if draw:
                    self.mpdraw.draw_landmarks(frame, hand, self.mphands.HAND_CONNECTIONS)
                
        return frame
    
    def findPosition(self,frame,hand_num=0, draw=True):
        xlst=[]
        ylst=[]
        box=[]
        self.lmlst = []
        if self.res.multi_hand_landmarks:
            hand = self.res.multi_hand_landmarks[hand_num]
            for id, lm in enumerate(hand.landmark):
                    #print(id, lm)
                    height,width,channel = frame.shape
                    cx,cy = int(lm.x*width), int(lm.y*height)
                    xlst.append(cx)
                    ylst.append(cy)
                    self.lmlst.append([id,cx,cy])

                    if draw:
                        cv2.circle(frame,(cx,cy),5,(0,0,255),cv2.FILLED)
            
            
            xmin,xmax = min(xlst), max(xlst)
            ymin,ymax = min(ylst), max(ylst)
            box = xmin, ymin, xmax, ymax

            # if draw:
            #     cv2.rectangle(frame, (box[0] - 20, box[1]-20), (box[2]+20,box[3]+20),(0,255,0),2)
        return self.lmlst, box


    

def main():
    prev_time = 0
    curr_time = 0
    s = 0
    # if len(sys.argv) > 1:
    #     s = sys.argv[1]

    win_name = 'Camera Preview'
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)

    source = cv2.VideoCapture(0)
    detect = handDetector()
    while True: # Escape
        has_frame, frame = source.read()    
        frame = detect.findHands(frame)
        lmList = detect.findPosition(frame)

        if len(lmList) != 0:
            #print(lmList[4])
            pass

        curr_time = time.time()
        fps = 1/(curr_time-prev_time)
        prev_time = curr_time

        cv2.putText(frame, str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (0,255,0),3)

        # if not has_frame:
        #     break
        cv2.imshow(win_name, frame)
        key = cv2.waitKey(1)
        if key == 27 or key == ord('x'):
            break

    # source.release()
    # cv2.destroyWindow(win_name)


if __name__ == "__main__":
    main()