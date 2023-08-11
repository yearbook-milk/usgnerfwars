import cv2
import numpy as np

# detector stores the aruco marker detector object, dictionary stores the dictionary used to detect aruco markers
# parametrs stores the aruco marker other parameters
# not sure why these are globals but if it aint broke dont fix it i suppose

detector = None
dictionary = None
parameters = None

def _init(other_modules):
    dicti = cv2.aruco.DICT_4X4_250
    global detector, dictionary, parameters
    # init the detector object
    dictionary = cv2.aruco.getPredefinedDictionary(dicti)
    parameters =  cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

def _attempt_detection(image, filterdata = None):
    global detector
    # get a list of all detections
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(image)
    output = []
    
    # for every detection
    for i in corners:
        four_corners = i[0]
        minX = 10000
        minY = 10000
        maxX = 0
        maxY = 0
        # extract the four corners, and convert from (tl,bl,tr,br) to (x,y,w,h) format
        for point in four_corners:
            if   point[0] > maxX: maxX = point[0]
            elif point[0] < minX: minX = point[0]
            
            if   point[1] > maxY: maxY = point[1]
            elif point[1] < minY: minY = point[1]
        output.append( (int(minX), int(minY), int(maxX - minX), int(maxY - minY)) )
        
    # return the list of all the (x,y,w,h) bounding boxes
    return output, image