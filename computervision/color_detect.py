import cv2
import numpy as np
import helpers

colors = {}
available_colors = "black white red green yellow light_blue orange dark_pink pink cyan dark_blue".split(" ")

# hs is for how much a certain pixel can deviate from the specified color range, in HSV deg, in the negative direction
# ha is for how much a certain pixel can deviate from the specified color range, in HSV deg, in the positive direction
# ss is for the mininum saturation of a pixel, in HSV
# minval is for the mininum value/brightness level of a pixel, in HSV

# blur controls how much blur to apply to remove noise and potential false positives

# the last four variables control the min and max detection size (i.e. if you're tracking blue but the walls are blue, 
# you can set a max limit to prevent the whole wall from being seen as a detection

# these variables however SHOULD be loaded from a config file and not hardcoded
 
hs = 0
ha = 0
ss = 0
blur = 0

minval = 0

minPolygonWidth = 0
minPolygonHeight = 0

maxPolygonWidth = 0
maxPolygonHeight = 0


def _init(other_modules):
    global colors, available_colors, hs, ha, ss, blur, minPolygonHeight, minPolygonWidth, maxPolygonWidth, maxPolygonHeight
    
    # helper constants i got from https://cppsecrets.com/users/252310097107115104971051159911111110864103109971051084699111109/DETECTION-OF-COLOR-OF-AN-IMAGE-USING-OpenCV.php
    f = eval(helpers.file_get_contents("detectorfilterdata.txt"), other_modules)
    hs = f["color_detect"]["other_parameters"]["lower_hue_tolerance"]
    ha = f["color_detect"]["other_parameters"]["upper_hue_tolerance"]
    ss = f["color_detect"]["other_parameters"]["min_hsv_saturation"]
    minval = f["color_detect"]["other_parameters"]["min_hsv_value"]
    blur = f["color_detect"]["other_parameters"]["blur_level"]
    minPolygonWidth = f["color_detect"]["other_parameters"]["minPolygonWidth"]
    minPolygonHeight = f["color_detect"]["other_parameters"]["minPolygonHeight"]
    maxPolygonWidth = f["color_detect"]["other_parameters"]["maxPolygonWidth"]
    maxPolygonHeight = f["color_detect"]["other_parameters"]["maxPolygonHeight"]

    # adjust the color masks to the tolerances acc. to the global variables
    """colors["lower_black"] = [0,0,0] 
    colors["upper_black"] = [50,50,100] 
    colors["lower_white"] = [0,0,0] 
    colors["upper_white"] = [0,0,255]"""
    colors["lower_red"] =        [0,ss,minval] 
    colors["upper_red"] =        [10+ha,255,255] 
    colors["lower_green"] =      [45-hs,ss,minval] 
    colors["upper_green"] =      [65+ha,255,255] 
    colors["lower_yellow"] =     [25-hs,ss,minval] 
    colors["upper_yellow"] =     [35+ha,255,255] 
    colors["lower_light_blue"] = [95-hs,ss,minval] 
    colors["upper_light_blue"] = [110+ha,255,255] 
    colors["lower_orange"] =     [15-hs,ss,minval] 
    colors["upper_orange"] =     [25+ha,255,255] 
    colors["lower_dark_pink"] =  [160-hs,ss,minval] 
    colors["upper_dark_pink"] =  [170+ha,255,255] 
    colors["lower_pink"] =       [145-hs,ss,minval]
    colors["upper_pink"] =       [155+ha,255,255] 
    colors["lower_cyan"] =       [85-hs,ss,minval] 
    colors["upper_cyan"] =       [95+ha,255,255] 
    colors["lower_dark_blue"] =  [115-hs,ss,minval] 
    colors["upper_dark_blue"] =  [125+ha,255,255]
    print(f"[color detector] On _init(), colors: {colors}")


def colorMasksGenerator(names):
    global colors
    print(f"[color detector] Generating colormasks with data {colors}")
    try:
        global available_colors
        output = []
        for i in names.split(" "):
            if i in available_colors: output.append({"colormask_upper": colors[f"upper_{i}"], "colormask_lower": colors[f"lower_{i}"]})
        return output
    except:
        print("[color detector] Error on generating colormasks! Did you run _init() at least once?")
        return []
        
        
def _attempt_detection(image, filterdata):
    global colors
    try:
        colormasks = filterdata["color_detect"]["colormasks"]
    except Exception:
        print("[color detector] Invalid filterdata given to ct2r.py!")
        return image
    
    height, width, _ = image.shape
    output = np.zeros((height,width,3), np.uint8)
    polygons = []
    
    # FIRST STEP: APPLY COLOR MASKS
    for i in colormasks:
        global available_colors, blur, minPolygonHeight, minPolygonWidth
        
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
        if (w > minPolygonWidth and h > minPolygonHeight) and (w < maxPolygonWidth and h < maxPolygonHeight):
            cv2.rectangle(output, (x,y), (x+w,y+h), (255, 0, 0), 2)
            polygons.append( (x, y, w, h) )
    
    return (polygons, output)




    
