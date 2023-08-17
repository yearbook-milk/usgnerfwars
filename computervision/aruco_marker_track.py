import cv2
import numpy as np
import helpers

# this variable keeps track of the selected aruco marker id 
# (so if other markers show up in frame, it will ignore them and only follow the one it was initially following
aruco_id = None

def _init(frame, ROI, dicti = cv2.aruco.DICT_4X4_250):
    # init aruco marker detector obj
    global aruco_id, aruco_detector
    dictionary = cv2.aruco.getPredefinedDictionary(dicti)
    parameters =  cv2.aruco.DetectorParameters()
    aruco_detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    global aruco_id
    
    # read the initial frame passed by main.py and look in the ROI passed in
    newROI = helpers.resizeBox(ROI, 1.20)
    corners, ids, _ = aruco_detector.detectMarkers(frame)
    
    # note down what ID the marker is
    if len(ids) > 0:
        aruco_id = ids[0][0]
        print(f"[aruco tag detector] Just locked onto an aruco marker with ID {ids[0][0]}")
    
    
def _update(frame):
    global aruco_id, aruco_detector
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = aruco_detector.detectMarkers(frame)
    output = None
    
    # for every marker found in frame
    for i in range(0, len(corners)):
        # if it was the same one we were following
        if ids[i] == aruco_id:
            four_corners = corners[i][0]
            minX = 10000
            minY = 10000
            maxX = 0
            maxY = 0
            # figure out which of the corners returned is the top left 
            # we do this to convert from (tl, tr, bl, br) or whatever format to (x, y, w, h)
            for point in four_corners:
                if   point[0] > maxX: maxX = point[0]
                elif point[0] < minX: minX = point[0]
                if   point[1] > maxY: maxY = point[1]
                elif point[1] < minY: minY = point[1]

            return (True, (int(minX), int(minY), int(maxX - minX), int(maxY - minY)))
        
    return (False, None)
            
            
