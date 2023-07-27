import cv2
import numpy as np

"""
Detector Module Interface:

* _init              (*argv)                                          -> <bool> indicating success or failure to start up the tracker
* _attempt_detection (ndarray img, dict filterdata)                   -> <list> with polygons of detections (x, y, w, h) format and a <ndarray> with the resultant image
* _attempt_lock      (ndarray img, event, x, y, list polygons, *argv) -> <dict> with information that will be reinserted into filterdata

PIPELINE 2: COLOR TRACKER
"""

colors = {}
available_colors = "black white red green yellow light_blue orange dark_pink pink cyan dark_blue".split(" ")
hs = 0
ha = 0
ss = 0
blur = 0
minPolygonWidth = 0
minPolygonHeight = 0

# hs is for lower hue leniency, ha is for upper hue leniency, ss is for desaturation tolerance, blur is for how
# much blur to apply to remove noise (more blur = less noise but also worse detections far away
def _init(lhs = hs, lha = ha, lss = ss, lblur = blur, lminPolygonWidth = minPolygonWidth, lminPolygonHeight = minPolygonHeight):
    global colors, available_colors, hs, ha, ss, blur, minPolygonHeight, minPolygonWidth
    hs = lhs
    ha = lha
    ss = lss
    blur = lblur
    minPolygonWidth = lminPolygonWidth
    minPolygonHeight = lminPolygonHeight
    # helper constants i got from https://cppsecrets.com/users/252310097107115104971051159911111110864103109971051084699111109/DETECTION-OF-COLOR-OF-AN-IMAGE-USING-OpenCV.php
    """colors["lower_black"] = [0,0,0] 
    colors["upper_black"] = [50,50,100] 
    colors["lower_white"] = [0,0,0] 
    colors["upper_white"] = [0,0,255]"""
    colors["lower_red"] = [0,150-ss,50] 
    colors["upper_red"] = [10+ha,255,255] 
    colors["lower_green"] = [45-hs,150-ss,50] 
    colors["upper_green"] = [65+ha,255,255] 
    colors["lower_yellow"] = [25-hs,150-ss,50] 
    colors["upper_yellow"] = [35+ha,255,255] 
    colors["lower_light_blue"] = [95-hs,150-ss,0] 
    colors["upper_light_blue"] = [110+ha,255,255] 
    colors["lower_orange"] = [15-hs,150-ss,0] 
    colors["upper_orange"] = [25+ha,255,255] 
    colors["lower_dark_pink"] = [160-hs,150-ss,0] 
    colors["upper_dark_pink"] = [170+ha,255,255] 
    colors["lower_pink"] = [145-hs,150-ss,0]
    colors["upper_pink"] = [155+ha,255,255] 
    colors["lower_cyan"] = [85-hs,150-ss,0] 
    colors["upper_cyan"] = [95+ha,255,255] 
    colors["lower_dark_blue"] = [115-hs,150-ss,0] 
    colors["upper_dark_blue"] = [125+ha,255,255]

def colorMasksGenerator(names):
    global available_colors
    output = []
    for i in names.split(" "):
        if i in available_colors: output.append({"colormask_upper": colors[f"upper_{i}"], "colormask_lower": colors[f"lower_{i}"]})
    return output

def _attempt_detection(image, filterdata):
    try:
        colormasks = filterdata["colormasks"]
    except Exception:
        print("Invalid filterdata given to ct2r.py!")
        return image
    
    height, width, _ = image.shape
    output = np.zeros((height,width,3), np.uint8)
    polygons = []
    
    # FIRST STEP IN THIS PIPELINE: APPLY COLOR MASKS
    for i in colormasks:
        global colors, available_colors, blur, minPolygonHeight, minPolygonWidth
        
        image2 = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_bound = np.array(i["colormask_lower"])
        upper_bound = np.array(i["colormask_upper"])
        mask = cv2.inRange(image2, lower_bound, upper_bound)
        # if multiple color masks have been specified, use bitwise OR to combine their results
        # for instance, if there are two blobs, orange and blue, and there is a mask for orange and blue,
        # the resultant binary image would have two blobs
        done = cv2.bitwise_and(image, image, mask=mask)
        output = cv2.bitwise_or(output, done)
        
    # SECOND STEP IN THIS PIPELINE: REMOVE NOISE
    output = cv2.GaussianBlur(output, (blur, blur), 0)
    
    # THIRD STEP IN THIS PIPELINE: APPLY BASIC CONTOUR DETECTION
    ret, thresh = cv2.threshold(cv2.cvtColor(output, cv2.COLOR_BGR2GRAY), 15, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
    
    # FOURTH STEP IN THIS PIPELINE: COMPILE AND RETURN THE BOUNDING BOXES FOR THESE COUNTOURS
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)
        if (w > minPolygonWidth and h > minPolygonHeight):
            cv2.rectangle(output, (x,y), (x+w,y+h), (255, 0, 0), 2)
            polygons.append( (x, y, w, h) )
    
    return (polygons, output)


    