import cv2
import numpy as np

"""
Tracker Module Interface:

_init(frame, ROI, **kwargs)
_update(frame, **kwargs) -> tuple [2] (success,bbox)

"""

aruco_id = 45
aruco_detector = None

def _init(frame, ROI, dicti = cv2.aruco.DICT_4X4_250):
    global aruco_id, aruco_detector
    dictionary = cv2.aruco.getPredefinedDictionary(dicti)
    parameters =  cv2.aruco.DetectorParameters()
    aruco_detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    
def _update(frame):
    global aruco_id, aruco_detector
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = aruco_detector.detectMarkers(frame)
    output = None
    for i in range(0, len(corners)):
        if ids[i] == aruco_id:
            four_corners = corners[i][0]
            minX = 10000
            minY = 10000
            maxX = 0
            maxY = 0
            for point in four_corners:
                if   point[0] > maxX: maxX = point[0]
                elif point[0] < minX: minX = point[0]
                if   point[1] > maxY: maxY = point[1]
                elif point[1] < minY: minY = point[1]

            return (True, (int(minX), int(minY), int(maxX - minX), int(maxY - minY)))
        
    return (False, None)
            
            
