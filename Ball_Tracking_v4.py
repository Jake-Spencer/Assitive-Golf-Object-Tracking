# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
from math import sqrt
import math 


#to check if the two drawn circles touch or intersect at any point.
def circle(xy1, xy2, r1, r2): 
   
	(x1, y1) = xy1
	(x2, y2) = xy2
	distSq = sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2));  
 
	if (distSq <= 30): #if the ball is in the hole
		return 1 
		
	elif( ((distSq <= 110) & (distSq >= 90)) & (x1 >= 360) ): #the distance between them is very close	 
		return 2											  #and to the right side of the hole
		
	elif ( (x1 >= 360) & (distSq > 115) ): #shot went to the right
		return 3
		
	elif ( (x1 <= 240) & (distSq > 115) ): #shot went to the left
		return 4

	elif ( ((distSq <= 110) & (distSq >= 90)) & (x1 <= 240) ): #the distance between them is very close 
		return 5											   #and to the left side of the hole
		
	elif ( y1 >= 300 ):	#the shot was too short
		return 6
	 
global last_t
global t
last_t = 0
t = 0

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
pinkLower = (135,95,205)
pinkUpper = (235,225,250)

#define the color of the black hole
blackLower = (84,40,16)
blackUpper = (200,110,65)


pts = deque(maxlen=args["buffer"])
pts_black = deque(maxlen=args["buffer"]) 
 
# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False): #if not video file was given
	vs = VideoStream(src= 0).start() #access the default webcam here
	
# otherwise, grab a reference to the video file
else:
	vs = VideoStream(src= 0).start()	#access the next available webcam
	#vs = cv2.VideoCapture(args["video"])
 
# allow the camera or video file to warm up
time.sleep(2.0)

# keep looping
while True:
	# grab the current frame
	frame = vs.read()
 
	# handle the frame from VideoCapture or VideoStream
	frame = frame[1] if args.get("video", False) else frame
 
	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if frame is None:
		break
 
	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=600) #new win size -> 600, 400
	blurred = cv2.GaussianBlur(frame, (15, 15), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
 
#-------------------Black Mask--------------------------------------------------------------------------
	# construct a mask_pink for the color "black", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask_black
	mask_black = cv2.inRange(hsv, blackLower, blackUpper)
	mask_black = cv2.erode(mask_black, None, iterations=1)
	mask_black = cv2.dilate(mask_black, None, iterations=3)
	
	#find contours in the mask_black and init the center of the hole
	cnts_black = cv2.findContours(mask_black.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts_black = imutils.grab_contours(cnts_black)
	center_black = None
#-------------------Black Mask--------------------------------------------------------------------------
	
#===================Pink Mask============================================================================

	# construct a mask_pink for the color "pink", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask_pink
	mask_pink = cv2.inRange(hsv, pinkLower, pinkUpper)
	mask_pink = cv2.erode(mask_pink, None, iterations=1)
	mask_pink = cv2.dilate(mask_pink, None, iterations=3)


	# find contours in the mask_pink and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask_pink.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None
	
#===================Pink Mask============================================================================
	
		# only proceed if at least one contour was found
	if len(cnts_black) > 0 | len(cnts) > 0:
		
		#-----------Black--------------------------------------------------
		# find the largest contour in the mask_pink, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c_black = max(cnts_black, key=cv2.contourArea)
		(x_black, y_black), radius_black = cv2.minEnclosingCircle(c_black)
		M_black = cv2.moments(c_black)
		center_black = (int(M_black["m10"] / M_black["m00"]), int(M_black["m01"] / M_black["m00"]))
		
		
		# find the largest contour in the mask_pink
		#===========Pink===================================================
		c = max(cnts, key=cv2.contourArea)
		(x, y), radius = cv2.minEnclosingCircle(c)
		radius_pink = radius
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		
		#Calculate the distance between the ball and hole
		t = circle(center, center_black, radius_pink, radius_black)
		
		
		if (last_t != t):	#if the value of t has changed run through these if statements
		
			#if the ball is in the hole
			if (t == 1):	
				print('Nice Job')
				
			#if the ball is close but not in the hole
			elif (t == 2):	
				print('So Close! A little more the left next time.')
			
			#if the ball is no where near the hole
			elif (t == 3):
				print ('Ball went wide right, aim more to the left')
				
			elif (t == 4):
				print('Ball went wide left, aim more to the right.')
			
			elif (t == 5):
				print('So Close! A little more the right next time.')
			
			elif (t == 6):
				print('Shoot it a little bit harder.')
		
		#===========Pink===================================================	
		
		# only proceed if the radius meets a minimum size
		if ( (radius_black > 10) | (radius > 1) ):
			# draw the circle and centroid on the frame,
			cv2.circle(frame, (int(x_black), int(y_black)), int(radius_black),(0, 255, 0), 2)
			
			
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
		
		
		
	# update the points queue
	pts_black.appendleft(center_black)
	
		# loop over the set of tracked points
	for i in range(1, len(pts_black)):
		# if either of the tracked points are None, ignore
		# them
		if pts_black[i - 1] is None or pts_black[i] is None:
			continue
  
 	# update the points queue
	pts.appendleft(center)
	
	# loop over the set of tracked points
	for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue
 
		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

 
	#mirroredIMG = cv2.flip(frame, 1)		#make the video stream flipped to act like a mirror	
	cv2.imshow("Shot Camera", frame)	#show the video stream in a window

	cv2.imshow("Pink Search", mask_pink)	#show the masked video stream in a window
	
	cv2.imshow("Hole Search", mask_black)	#show the masked video stream in a window

	key = cv2.waitKey(1) & 0xFF
 
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		cv2.destroyAllWindows()
		break
		
	last_t = t

 
# close all windows
cv2.destroyAllWindows()
