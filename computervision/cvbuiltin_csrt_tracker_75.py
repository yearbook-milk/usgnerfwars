import cv2
import numpy as np

"""
Tracker Module Interface:

_init(frame, ROI, **kwargs)
_update(frame, **kwargs) -> tuple [2] (success,bbox)


* this is the 75% bboxversion of the KCF tracker
"""

the_tracker = None

def resizeBox(inputbox, scale):
    print(inputbox)
    cp = ( \
    int(inputbox[0] + (0.5 * (inputbox[2]))), \
    int(inputbox[1] + (0.5 * (inputbox[3]))) \
    )
    print(cp)
    
    nb = ( \
    cp[0] - (0.5 * scale * inputbox[2]), \
    cp[1] - (0.5 * scale * inputbox[3]), \
    (scale * inputbox[2]), \
    (scale * inputbox[3]) \
    )
    
    x, y, w, h = nb
    print(nb)
    
    return (cp, int(x), int(y), int(w), int(h))
    

def _init(frame, ROI):
    global the_tracker
    the_tracker = cv2.TrackerCSRT_create()
    ROI = resizeBox(ROI, 0.75)
    the_tracker.init(frame, ROI[1:])
    return None

def _update(frame):
    success, box = the_tracker.update(frame)
    if box[0] == 0 or box[1] == 0: return (False, None)
    return (success, box)



