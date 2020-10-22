from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import serial


#arduino = serial.Serial('COM5', 9600)
#time.sleep(2)
print("Connection to arduino...")

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
help="max buffer size")
args = vars(ap.parse_args())

#Kuning
Lower = (0, 133, 89)
Upper = (161, 255, 255)

if not args.get("video", False):
    camera = cv2.VideoCapture(0)
 
# otherwise, grab a reference to the video file
else:
    camera = cv2.VideoCapture(args["video"])
    
def nothing(x):
    pass

hmax = 9
hmin = 0
smax = 255
smin = 85
vmax = 255
vmin = 26


cv2.namedWindow('Control')
cv2.createTrackbar('HMax','Control',hmax,255,nothing)
cv2.createTrackbar('HMin','Control',hmin,255,nothing)
cv2.createTrackbar('SMax','Control',smax,255,nothing)
cv2.createTrackbar('SMin','Control',smin,255,nothing)
cv2.createTrackbar('VMax','Control',vmax,255,nothing)
cv2.createTrackbar('VMin','Control',vmin,255,nothing)


while True:
    #n = arduino.inWaiting()
    #str = arduino.read(n)
    #if str:
     #   print str
    ret, frame = camera.read()
    frame = cv2.blur(frame, (3,3),0)

    h = np.size(frame, 0)
    w = np.size(frame, 1)

    if args.get("video") and not grabbed:
        break
     
    # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    hmax = cv2.getTrackbarPos('HMax','Control')
    hmin = cv2.getTrackbarPos('HMin','Control')
    smax = cv2.getTrackbarPos('SMax','Control')
    smin = cv2.getTrackbarPos('SMin','Control')
    vmax = cv2.getTrackbarPos('VMax','Control')
    vmin = cv2.getTrackbarPos('VMin','Control')

    orangeLower = (hmin, smin, vmin)
    orangeUpper = (hmax, smax, vmax)
     
    mask = cv2.inRange(hsv, orangeLower, orangeUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cv2.imshow('mask',mask)

    params = cv2.SimpleBlobDetector_Params()

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        #print ("nilai C :",c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        #cv2.line(frame,(0,240),(640,240),(0,255,0),2)
        #cv2.line(frame,(220,0),(220,480),(255,0,0),2)
        #cv2.line(frame,(440,0),(440,480),(255,0,0),2)

        if radius > 10 :
                cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                textLine1 = 'Bola ==> X = %d Y = %d Radius = %d'%(x, y, radius)
                cv2.putText(frame,textLine1,(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0,0,255),2)

                #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),5)
                #print ('X :' +str(x))
                #print ('Y :'+str(y))

                PosX = int((x+(x+h))/2)
                PosY = int((y+(y+w))/2)
                        
                data = "X{0:d}Y{1:d}Z".format(PosX, PosY)
                print ("Data sudut = '" +data+ "'")
                #arduino.write(data)
    
            
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
 
    if key == ord("q"):
	    break

while not connected:
    serin = ser.read()
    connected = True

camera.release()
cv2.destroyAllWindows()
