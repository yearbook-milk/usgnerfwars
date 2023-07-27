import cv2
import numpy as np

"""
Detector Module Interface:

* _init              (*argv)                                          -> <bool> indicating success or failure to start up the tracker
* _attempt_detection (ndarray img, dict filterdata)                   -> <list> with polygons of detections (x, y, w, h) format and a <ndarray> with the resultant image
* _attempt_lock      (ndarray img, event, x, y, list polygons, *argv) -> <dict> with information that will be reinserted into filterdata

PIPELINE 3: SIMPLE ARUCO MARKER DETECTION
"""

detector = None
dictionary = None
parameters = None

def _init(dicti = cv2.aruco.DICT_4X4_250):
    global detector, dictionary, parameters
    dictionary = cv2.aruco.getPredefinedDictionary(dicti)
    parameters =  cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

def _attempt_detection(image, filterdata = None):
    global detector
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(image)
    output = []
    for i in corners:
        four_corners = i[0]
        minX = 10000
        minY = 10000
        maxX = 0
        maxY = 0
        for point in four_corners:
            if   point[0] > maxX: maxX = point[0]
            elif point[0] < minX: minX = point[0]
            
            if   point[1] > maxY: maxY = point[1]
            elif point[1] < minY: minY = point[1]
        output.append( (int(minX), int(minY), int(maxX - minX), int(maxY - minY)) )
    return output, image