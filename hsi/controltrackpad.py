import cv2
import helpers
import numpy as np
import servo_relay_interface as sri

bgd = np.zeros((300,300,3), np.uint8)
unlockControls = True
pitch = 0
yaw = 0

sri.config["leftPin"] = 12
sri.config["rightPin"] = 33
sri.config["yawPin"] = 32
sri.config["afterSpdCmdDelay"] = 0.0
sri.config["pulse_freq"] = 50

sri.__initialize()
sri.centerAllAxes()

def redoImage():
    global bgd
    bgd = np.zeros((300,300,3), np.uint8)
    cv2.putText(bgd,"-90", (0,10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
    cv2.putText(bgd,"0", (150,10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
    cv2.putText(bgd,"+90", (270,10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))

    cv2.putText(bgd,"0", (270,150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
    cv2.putText(bgd,"-90", (270,270), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))

    bgd = helpers.line(bgd, "X=", 150, (255,255,255))
    bgd = helpers.line(bgd, "Y=", 150, (255,255,255))

def onClick(event, x, y, f, p):
    global unlockControls, bgd, pitch, yaw
    if unlockControls:
        redoImage()
        bgd = helpers.line(bgd, "X=", x, (255,0,255))
        bgd = helpers.line(bgd, "Y=", y, (255,0,255))
        pitch = -1 * (int((y/300) * 180) - 90)
        yaw   = +1 * (int((x/300) * 180) - 90)
        sri.pitch(pitch)
        sri.yaw(yaw)
    if event == cv2.EVENT_LBUTTONDOWN:
        unlockControls = not unlockControls

    cv2.putText(bgd, f"{pitch}deg pitch, {yaw}deg yaw", (30,270), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255))
    cv2.putText(bgd, f"controls unlocked: {unlockControls}", (30,290), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255))
    cv2.imshow("manualcontroltrackpad", bgd)


try:
    redoImage()
    cv2.namedWindow("manualcontroltrackpad")
    cv2.setMouseCallback('manualcontroltrackpad', onClick)
    while True:
        cv2.imshow("manualcontroltrackpad", bgd)
        cv2.waitKey(0)
except KeyboardInterrupt:
    sri.__shutdown()
    exit()
    
    
exit()
