# The Main scripts that run on nodes

import socket
import lib
import cv2
import numpy as np


cf = open('config') 
server = cf.read() # Point it to server
cf.close()

lib.printSerin()

def movementEvent():
	vc = cv2.VideoCapture(0)
	ret, frame = vc.read()
	prev = 0 #Stores previous position
	direction = 0
	firstframe = 1 #Is the current frame first ?
	trigger = 0
	while ret:
		# Changing Color space
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		# Threshold Values. Use the hsv_filter.py to tune
		hmin = 0
		hmax = 28
		smin = 48
		smax = 180
		vmin = 0
		vmax = 250
		min = np.array([hmin, smin, vmin], np.uint8)
		max = np.array([hmax, smax, vmax], np.uint8)

		# Morphological Transformations to detect hand
		# Successive kernel enlargement (experimental technique)
		img = cv2.inRange(hsv, min, max)
		kernel = np.ones((20, 20), np.uint8)
		morph = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
		morph2 = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel)
		kernel = np.ones((30, 30), np.uint8)
		morph3 = cv2.erode(morph2, kernel, iterations=2)
		kernel = np.ones((40, 40), np.uint8)
		morph4 = cv2.dilate(morph3, kernel, iterations=2)

		# Finding contours
		contours, hierarchy = cv2.findContours(morph4, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
		cv2.drawContours(morph4, contours, -1, (0, 255, 0), 3)

		# If atleast one contour is there
		if len(contours) > 0:
			# Find the property of the largest contour
			moments = cv2.moments(contours[0])
			area = moments['m00']
			# Area should represent a significant contour
			if area > 50000:
				# Centroid position on X-axis
				centx = int(moments['m10']/moments['m00'])
				if prev != 0:
					disp = (centx - prev)
					direction = direction + disp
					if direction < -100 or direction > 100:
						trigger = 1
						direction = 0
						break
				if firstframe == 1:
					firstframe = 0
				prev = centx
		rval, frame = vc.read()
		key = cv2.waitKey(20)
		if key == 27:
			break
	return trigger



# Program Flow here
#--------------------------
eventHappened = 0 # Set it to 1 when event happens

while True:
	eventHappened = movementEvent()
	if eventHappened == 1:
		lib.act(server)

#--------------------------