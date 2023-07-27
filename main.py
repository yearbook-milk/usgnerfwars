print("Starting up...")
import cv2
import numpy                         as np
import sys
import os

sys.path.append(os.path.abspath("computervision"))
sys.path.append(os.path.abspath("hsi"))
sys.path.append(os.path.abspath("net/server"))
os.chdir(os.path.abspath("computervision"))


print(f"-- PATH variable: {sys.path}")

import color_track_return_rectangle  as ct2r
import aruco_marker_return_rectangle as am2r

import cvbuiltin_kcf_tracker         as cvbits_KCF
import aruco_marker_tracker          as amt

import helpers


import servo_relay_interface         as sri

import remote                        as net

import config                        as cfg



print("--Imports complete!")




# FIRST, set up access to webcam and network -------------
device = 0
latch = True
polygons = []

if device == None: device = int(input("--Which device (enter an int)? "))

cap = cv2.VideoCapture(device)
if not cap.isOpened():
    print("--Webcam entry point failed to initialize!")
    exit(-1)
else:
    print("--Webcam OK!")
# --------------------------------------------






# SECOND, initialize all the stuff on the pipeline
ct2r._init(lhs = 20, lha = 20, lss = 75, lblur = 15, lminPolygonWidth = 69, lminPolygonHeight = 69)
am2r._init()

inuse = []
trackers_inuse = []
filterdata = {}

def updatePipeline():
    global inuse, filterdata, trackers_inuse
    inuse = eval(helpers.file_get_contents("detectorpipeline.txt"), {
        "ct2r": ct2r,
        "am2r": am2r,
    })
    filterdata = eval(helpers.file_get_contents("detectorfilterdata.txt"), {
        "ct2r": ct2r,
        "am2r": am2r,
    })
    trackers_inuse = eval(helpers.file_get_contents("tracker.txt"), {
        "cvbits_KCF": cvbits_KCF,
        "amt": amt
    })
    
    print(f"--OK! Detection pipeline reconfigured. Using trackers {inuse} \n\n with input data {filterdata}. \n\n Tracker: {trackers_inuse}\n\n")

updatePipeline()
# ----------------------------------------







# THIRD, SET UP LOCAL VARIABLES -----------
only_draw_biggest_polygon = True

lock = "SCAN"
the_tracker = None

rescan_on_lockbreak = True
failed_tracks = 0
failed_tracks_thresh = 100
rsfactor = 0.75

# set up output windows
#cv2.namedWindow("input")
cv2.namedWindow("output")
#cv2.setMouseCallback("input", onclick)
# -----------------------------------------






# FOURTH, we set up our interface with the hardware ----
sri.config = cfg.pin_config
sri.__initialize()
print("--Hardware-software interface set up!")
#------------------------------------------------------





# 5TH, start up the networking wrapper ------------------
if cfg.enable_config:
    net.setupParameters(cfg.TCP_port, cfg.UDP_port)
    print("--Networking interface configured. The remote must connect to this device in order to continue startup.")

    ip = os.system(cfg.checkip_command)

    print(f"--Using port {cfg.TCP_port}")
    print(f"--Network adapter information: {ip}")
    net.initConnection()
else:
    print("-- Remote mode has been disabled. An output window will start on the local machine.")
# --------------




# WITH THIS DONE, START THE MAIN LOOP ---
print("OK to go!")
while latch:
    
    # TAKE A CAMERA INPUT --------------------------------------
    timer = cv2.getTickCount()
    ret, camera_input = cap.read()
    camera_input = cv2.resize(camera_input, (0,0), fx=rsfactor, fy=rsfactor) 
    if (ret):
        camera_input = helpers.increase_brightness(camera_input, value=10)
        #cv2.imshow("input", camera_input)

        # get polygons back out of the detection method if we are scanning
        polygons = []
        for i in inuse:
            polygons += i._attempt_detection(camera_input, filterdata)[0]
            
        if (lock == "SCAN"):

            if not only_draw_biggest_polygon:
                indice = 0
                polycopy = {}
                # we sort the polygons by top left coordinate so that way we the boxes dont switch numbers constantly
                for i in polygons:
                    polycopy[ i[1] + i[0] ] = i

                minY = -1

                myKeys = list(polycopy.keys())
                myKeys.sort()
                polygons = []
                for i in myKeys:
                    polygons.append(polycopy[i])

                
                for i in polygons:
                    x, y, w, h = i
                    cv2.rectangle(camera_input, (x,y), (x+w,y+h), (255, 255, 0), 2)
                    cv2.putText(
                        camera_input,
                        "detection#"+str(indice),
                        (x, y-10),
                        cv2.FONT_HERSHEY_DUPLEX,
                        0.50,
                        (255,255,0)
                    )
                    indice += 1
                    # if all polygons that were able to be produced are to be drawn, draw in cyan
            else:
                largestPolygon = (-1, -1, -1, -1)
                for i in polygons:
                    x, y, w, h = i
                    if (w > largestPolygon[2] and h > largestPolygon[3]):
                        largestPolygon = (x, y, w, h)
                x, y, w, h = largestPolygon
                polygons = [largestPolygon]
                cv2.rectangle(camera_input, (x,y), (x+w,y+h), (255, 255, 0), 2)
                cv2.putText(
                        camera_input,
                        "sole detection#"+str(0),
                        (x, y-10),
                        cv2.FONT_HERSHEY_DUPLEX,
                        0.50,
                        (255,255,0)
                )
                # if only the largest polygon is being drawn, draw in cyan

                
        elif (lock == "LOCK"):
            if (the_tracker == None):
                lock == "SCAN"
            
            successes = 0
            x = 0
            y = 0
            w = 0
            h = 0
            
            for i in trackers_inuse:
                success, box = i._update(camera_input)
                if success:
                    x += box[0]; y += box[1]; w += box[2]; h += box[3]
                    successes += 1
                
            success = (successes > 0)
            if (success):
                x = int(x / successes)
                y = int(y / successes)
                w = int(w / successes)
                h = int(h / successes)
                box = (x, y, w, h)
                cv2.rectangle(camera_input, box, (0, 255, 255), 2)
                camera_input = helpers.line(camera_input, "X=", int(box[0] + 0.5 * box[2]), (0,255,255))
                camera_input = helpers.line(camera_input, "Y=", int(box[1] + 0.5 * box[3]), (0,255,255))
                centerpoint = (int(box[1] + 0.5 * box[3]), int(box[0] + 0.5 * box[2]))
                # if the polygon is being tracked, draw in yellow
                failed_tracks = 0
            
            elif (not success) and (rescan_on_lockbreak):
                failed_tracks += 1

            if (failed_tracks >= failed_tracks_thresh):
                the_tracker = None
                lock = "SCAN"
                failed_tracks = 0
            
           
       # list FPS
        fps = int(cv2.getTickFrequency() / (cv2.getTickCount() - timer))
        if (only_draw_biggest_polygon): polset = "LargestPolygonOnly"
        else: polset = "AllPolygonsIncluded"
        cv2.putText(
            camera_input,
            f"""CAMERA: {fps}fps  cam#{device}""".replace("\n", ""),
            (5,35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (0,255,255)
        )
        cv2.putText(
            camera_input,
            f"""AUTOLOCK: {lock} {polset} {len(polygons)}d {failed_tracks}/{failed_tracks_thresh}ftfs""".replace("\n", ""),
            (5,55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (255,255,0)
        )
        cv2.putText(
            camera_input,
            f"""[0-9] Choose Tgt, [F] Forget Tgt, [O] Toggle LPO, [Q] Quit, [P] Pipln Update""".replace("\n", ""),
            (5,75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0,0,255)
        )
                
            
        
        cv2.imshow("output", camera_input)
        
    # waitKey so the program doesn't crash
    kb = cv2.waitKey(1)
    # ----------------------------------------------






# release resources when done
cv2.destroyAllWindows()
cap.release()
