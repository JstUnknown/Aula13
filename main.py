import cv2
import mediapipe as mp
import pyautogui
import math
from pynput.keyboard import Key,Controller
import time

keyboard=Controller()

cap = cv2.VideoCapture(0)

width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

screen_width,screen_height=pyautogui.size()

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    min_detection_confidence=0.8,
    min_tracking_confidence=0.5
)

tips = [4, 8, 12, 16, 20]
state=None

# FUNÇÃO PRA CONTAR DEDOS
def count_fingers(hand_landmarks):
    fingers = []
    landmarks=hand_landmarks.landmark

    for lm_index in tips:
        
        if lm_index!=4:
            fingers_tip_y=landmarks[lm_index].y
            fingers_bottom_y=landmarks[lm_index-2].y
            if fingers_tip_y<fingers_bottom_y:
                fingers.append(1)
            if fingers_tip_y>fingers_bottom_y:
                fingers.append(0)

    return fingers.count(1)
        

while True:
    success, image = cap.read()

    image = cv2.flip(image, 1)
    h,w,c=image.shape
    # IMPORTANTE (MediaPipe precisa RGB)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    # hand_landmarks = results.multi_hand_landmarks
    # drawHandLanMarks(image,hand_landmarks)
    # count_fingers(image,hand_landmarks)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks=hand_landmarks.landmark
            totalFingers=count_fingers(hand_landmarks)
            #play
            if totalFingers==4:
                state="Play"
            #pause
            if totalFingers==0 and state=="Play":
                state="Pause"
                keyboard.press("K")
                keyboard.release("K")
            #indicador
            index_y=int(landmarks[8].y*h)
            index_x=int(landmarks[8].x*w)
            #polegar
            thumb_y=int(landmarks[4].y*h)
            thumb_x=int(landmarks[4].x*w)

            screen_x=screen_width/w*index_x
            screen_y=screen_height/h*index_y
            
            pyautogui.moveTo(screen_x,screen_y)
            dist=math.hypot(index_x-thumb_x,index_y-thumb_y)
            cv2.line(image,(index_x,index_y),(thumb_x,thumb_y),(255,0,0),3)
            cv2.circle(image,(index_x,index_y),10,(0,255,0),-1)
            cv2.circle(image,(thumb_x,thumb_y),10,(0,255,0),-1)

            if dist<20 and not clicking:
                cv2.line(image,(index_x,index_y),(thumb_x,thumb_y),(255,0,0),5)
                pyautogui.click()
                clicking=True
            if dist>40:
                clicking=False

            if totalFingers==1:
                if index_x<150:
                    keyboard.press(Key.left)
                    keyboard.release(Key.left)
                   
                if index_x>w-150:
                    keyboard.press(Key.right)
                    keyboard.release(Key.right)
                   

    cv2.imshow("Controlador de Midia", image)

    key = cv2.waitKey(1)
    if key == 32:
        break

cap.release()
cv2.destroyAllWindows()