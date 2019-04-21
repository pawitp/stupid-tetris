# -*- coding: utf-8 -*-
"""
Created on Thu Mar  23 01:01:43 2017

@author: abhisheksingh
"""

#%%
import cv2
import numpy as np
import os
import time

import gestureCNN as myNN
from inputtracker import InputTracker
import tetris

minValue = 70

x0 = 100
y0 = 200

x1 = 400
y1 = 200

height = 200
width = 200

saveImg = False

counter = 0

# This parameter controls number of image samples to be taken PER gesture
numOfSamples = 301
gestname = ""
path = "./images/"
model = 0

#%%
def saveROIImg(img, flip):
    global counter, gestname, path, saveImg
    if counter > (numOfSamples - 1):
        # Reset the parameters
        saveImg = False
        gestname = ''
        counter = 0
        return
    
    counter = counter + 1
    name = gestname + "_" + str(flip) + "_" + str(counter)
    print("Saving img: ", name)
    cv2.imwrite(path + name + ".png", img)
    time.sleep(0.04)

#%%
def binaryMask(frame, x0, y0, width, height, flip, framecount, plot):
    global model, saveImg
    
    cv2.rectangle(frame, (x0,y0),(x0+width,y0+height),(0,255,0),1)
    #roi = cv2.UMat(frame[y0:y0+height, x0:x0+width])
    roi = frame[y0:y0+height, x0:x0+width]
    
    if flip:
        roi = cv2.flip(roi, 1)
    
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),2)
    
    th3 = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
    ret, res = cv2.threshold(th3, minValue, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    res = cv2.resize(res, (40, 40))
    guess = ""
    
    if saveImg == True:
        saveROIImg(res, flip)

    guess = myNN.guessGesture(model, res)
    plot = np.zeros((512,512,3), np.uint8)
    plot = myNN.update(plot)

    return res, guess, plot
	
#%%
def main():
    global model, binaryMode, x0, y0, x1, y1, width, height, saveImg, gestname, path
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    size = 0.5
    fx = 10
    fy = 350
    fh = 18
    
    tracker1 = InputTracker()
    tracker2 = InputTracker()

    model = myNN.loadCNN(0)
        
    ## Grab camera input
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('Original', cv2.WINDOW_NORMAL)

    # set rt size as 640x480
    ret = cap.set(3,640)
    ret = cap.set(4,480)

    framecount = 0
    fps = ""
    start = time.time()

    plot = np.zeros((512,512,3), np.uint8)
    plot2 = np.zeros((512,512,3), np.uint8)
    
    while(True):
        ret, frame = cap.read()
        max_area = 0
        
        frame = cv2.flip(frame, 3)
        frame = cv2.resize(frame, (640,480))
                      
        if ret == True:
            timestamp = time.time()
            roi, guess, plot = binaryMask(frame, x0, y0, width, height, False, framecount, plot)
            roi2, guess2, plot2 = binaryMask(frame, x1, y1, width, height, True, framecount, plot2)

            cv2.putText(frame, guess, (x0, y0), font, 0.7, (0, 255, 0), 2, 1)
            cv2.putText(frame, guess2, (x1, y1), font, 0.7, (0, 255, 0), 2, 1)

            action = tracker1.update(guess, timestamp)
            action2 = tracker2.update(guess2, timestamp)
            
            if action != "":
                cv2.putText(frame, action, (x0 + 100, y0), font, 0.7, (0, 255, 0), 2, 1)
                if action == "DOWN":
                    tetris.action("down")
                elif action == "FLIP":
                    tetris.action("flip")
                elif action == "MOVE":
                    tetris.action("right")
            if action2 != "":
                cv2.putText(frame, action2, (x1 + 100, y1), font, 0.7, (0, 255, 0), 2, 1)
                if action2 == "DOWN":
                    tetris.action("down")
                elif action2 == "FLIP":
                    tetris.action("flip")
                elif action2 == "MOVE":
                    tetris.action("left")
            
            framecount = framecount + 1
            timediff = timestamp - start
            if( timediff >= 1):
                #timediff = end - start
                fps = 'FPS:%s' %(framecount)
                start = time.time()
                framecount = 0

        cv2.putText(frame,fps,(10,20), font, 0.7,(0,255,0),2,1)
        cv2.putText(frame,'n - To enter name of new gesture folder',(fx,fy + 5*fh), font, size,(0,255,0),1,1)
        cv2.putText(frame,'s - To start capturing new gestures for training',(fx,fy + 6*fh), font, size,(0,255,0),1,1)
        cv2.putText(frame,'ESC - Exit',(fx,fy + 7*fh), font, size,(0,255,0),1,1)
        
        cv2.imshow('Original',frame)
        cv2.imshow('ROI', roi)
        cv2.imshow('ROI2', roi2)
        # cv2.imshow('Gesture Probability', plot)
        # cv2.imshow('Gesture Probability 2', plot2)
        
        ############## Keyboard inputs ##################
        key = cv2.waitKey(5) & 0xff
        
        ## Use Esc key to close the program
        if key == 27:
            break

        ## Use s key to start/pause/resume taking snapshots
        ## numOfSamples controls number of snapshots to be taken PER gesture
        elif key == ord('s'):
            if gestname != '':
                saveImg = True
            else:
                print("Enter a gesture group name first, by pressing 'n'")
                saveImg = False
        
        ## Use n key to enter gesture name
        elif key == ord('n'):
            gestname = input("Enter the gesture name: ")

    # Release & destroy
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

