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
    xo, yo, wo, ho = inputbox
    return (int(xo + (wo * 0.25 * scale)), int(yo + (ho * 0.25 * scale)), int(scale * wo), int(scale * ho))

def _init(frame, ROI):
    global the_tracker
    the_tracker = cv2.TrackerKCF_create()
    ROI = resizeBox(ROI, 0.65)
    the_tracker.init(frame, ROI)
    return None

def _update(frame):
    success, box = the_tracker.update(frame)
    return (success, box)
