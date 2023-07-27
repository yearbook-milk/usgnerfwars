import cv2
import numpy as np

"""
Tracker Module Interface:

_init(frame, ROI, **kwargs)
_update(frame, **kwargs) -> tuple [2] (success,bbox)

"""

the_tracker = None

def _init(frame, ROI):
    global the_tracker
    the_tracker = cv2.TrackerKCF_create()
    the_tracker.init(frame, ROI)
    return None

def _update(frame):
    success, box = the_tracker.update(frame)
    return (success, box)