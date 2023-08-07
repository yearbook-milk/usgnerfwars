
print("Starting up...")
import cv2
import numpy                         as np
import sys
import os
import pickle
import importlib

sys.path.append(os.path.abspath("computervision"))
sys.path.append(os.path.abspath("hsi"))
sys.path.append(os.path.abspath("net/server"))
os.chdir(os.path.abspath("computervision"))


print(f"-- PATH variable: {sys.path}")

import color_track_return_rectangle  as ct2r
import aruco_marker_return_rectangle as am2r

import cvbuiltin_kcf_tracker         as cvbits_KCF
import cvbuiltin_kcf_tracker_75      as cvbits_KCF_75P
import cvbuiltin_csrt_tracker        as cvbits_CSRT
import cvbuiltin_csrt_tracker_75     as cvbits_CSRT_75P
import aruco_marker_tracker          as amt

import helpers

import config                        as cfg



print("-- Imports complete!")




# FIRST, set up access to webcam and network -------------
device = cfg.default_camera
latch = True
polygons = []

if device == None: device = int(input("--Which device (enter an int)? "))

cap = cv2.VideoCapture(device)
if not cap.isOpened():
    print("-- Webcam entry point failed to initialize!")
    exit(-1)
else:
    print("-- Webcam OK!")
# --------------------------------------------






# SECOND, initialize all the stuff on the pipeline
inuse = []
trackers_inuse = []
filterdata = {}

def updatePipeline():
    global the_tracker, lock, failed_tracks
    the_tracker = None
    lock = "SCAN"
    failed_tracks = 0
    print("updatePipeline: lock released automatically in order to update pipeline...")
    
    # before we update the CV pipline we should also update cfg
    for i in [cfg, ct2r, am2r, cvbits_KCF, cvbits_KCF_75P, amt]:
        importlib.reload(i)
        print(f"RELOADER: reloaded {i}")
        
    global failed_tracks_thresh, rsfactor, compression
    failed_tracks_thresh = cfg.failed_tracking_frames_thresh
    rsfactor = cfg.image_resize_factor
    compression = cfg.network_image_compression
    

        
    ct2r._init(
        lhs               = cfg.ct2r_hue_lower_tolerance,
        lha               = cfg.ct2r_hue_upper_tolerance,
        lss               = cfg.ct2r_saturation_lower_tolerance,
        lblur             = cfg.ct2r_blur_level,
        lminPolygonWidth  = cfg.ct2r_minpolywidth,
        lminPolygonHeight = cfg.ct2r_minpolyht
    )
    am2r._init()


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
        "cvbits_KCF_75P": cvbits_KCF_75P,
        "cvbits_CSRT": cvbits_CSRT,
        "cvbits_CSRT_75P": cvbits_CSRT_75P,
        "amt": amt
    })
    
    print(f"-- OK! Detection pipeline reconfigured. Using detectors {inuse} \n\n with input data {filterdata}. \n\n Tracker: {trackers_inuse}\n\n")

updatePipeline()
# ----------------------------------------







# THIRD, SET UP LOCAL VARIABLES -----------
only_draw_biggest_polygon = True

lock = "SCAN"
the_tracker = None
failed_tracks = 0
last_successful_frame = None
last_success_boxes = []
last_successful_tracks = []
is_moving = False
vector_motion = (0,0)
mag = 0

encoded_text     = []
# (x,y,color,scale,content)

# set up output windows
#cv2.namedWindow("input")
if not cfg.enable_networking or cfg.show_local_output:
    cv2.namedWindow("output")
#cv2.setMouseCallback("input", onclick)
# -----------------------------------------






# FOURTH, we set up our interface with the hardware ----
pitch = 0
yaw = 0
if cfg.enable_hsi:
    import servo_relay_interface         as sri
    sri.config = cfg.pin_config
    sri.__initialize()
    print("-- Hardware-software interface set up!")
else:
    print("-- The hardware-software interface was not set up.")
#------------------------------------------------------





# 5TH, start up the networking wrapper ------------------
if cfg.enable_networking:
    import remote                        as net
    net.setupParameters(cfg.TCP_port, cfg.UDP_port)
    print("-- Networking interface configured. The remote must connect to this device in order to continue startup. Network adapter info:")

    ip = os.system(cfg.checkip_command)

    print(f"-- Using port {cfg.TCP_port}")
    print(f"-- {cfg.checkip_command} exit code: {ip}")
    net.initConnection()
    f = open("../http/.PORT")
    pn = int(f.read())
    f.close()
    print(f"-- CAS Config HTTP should be running on port #"+str(pn))
else:
    print("-- Remote mode has been disabled. An output window will start on the local machine.")
# --------------




# WITH THIS DONE, START THE MAIN LOOP ---
import time
time.sleep(3)
if cfg.enable_networking: net.sendTo("TCP", net.TCP_CONNECTION, b"casconfig " + bytes(str(pn), "ascii"), net.TCP_REMOTE_PEER[0])

print("OK to go!")
while latch:
    
    # TAKE A CAMERA INPUT --------------------------------------
    encoded_text = []
    timer = cv2.getTickCount()
    ret, camera_input = cap.read()
    #camera_input = cv2.rotate(camera_input, cv2.ROTATE_90_CLOCKWISE)
    last_successful_frame = camera_input
    command = None
    # -----------------------------------------------------------

    if (ret):
        camera_input = cv2.resize(camera_input, (0,0), fx=rsfactor, fy=rsfactor)
        camera_input = helpers.increase_brightness(camera_input, value=10)
        #cv2.imshow("input", camera_input)

        # get polygons back out of the detection method if we are scanning
        polygons = []
        for i in inuse:
            polygons += i._attempt_detection(camera_input, filterdata)[0]
        # SCAN FOR CANDIDATES ------------------------------------------------------
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

                    if not cfg.enable_networking or cfg.show_local_output:
                        cv2.putText(
                            camera_input,
                            "detection#"+str(indice),
                            (x, y-10),
                            cv2.FONT_HERSHEY_DUPLEX,
                            0.50,
                            (255,255,0)
                        )
                    else:
                        encoded_text.append( [x, y, (255,255,0), 0.50, "detection#"+str(indice)] )
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
                if not cfg.enable_networking or cfg.show_local_output:
                    cv2.putText(
                        camera_input,
                        "sole detection#"+str(0),
                        (x, y-10),
                        cv2.FONT_HERSHEY_DUPLEX,
                        0.50,
                        (255,255,0)
                    )
                else:
                    encoded_text.append( [x, y, (255,255,0), 0.50, "sole detection#"+str(0)])
                # if only the largest polygon is being drawn, draw in cyan
        #-------------------------------------------------------------------
                
                
                
                
                
        # LOCK ONTO TARGET --------------------------------------------------
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
            # IF SUCCESSFUL TRACK  --------------------------------------------
            if (success):
                x = int(x / successes)
                y = int(y / successes)
                w = int(w / successes)
                h = int(h / successes)
                box = (x, y, w, h)
                last_success_box = box
                keep_going = "STOP"
                cv2.rectangle(camera_input, box, (0, 255, 255), 2)
                camera_input = helpers.line(camera_input, "X=", int(box[0] + 0.5 * box[2]), (0,255,255))
                camera_input = helpers.line(camera_input, "Y=", int(box[1] + 0.5 * box[3]), (0,255,255))
                centerpoint = (int(box[1] + 0.5 * box[3]), int(box[0] + 0.5 * box[2]))
                # if the polygon is being tracked, draw in yellow
                failed_tracks = 0
                # now that we have a center point, we should calculate how much to turn the servo
                screen_center = ( int(camera_input.shape[0] * 0.5), int(camera_input.shape[1] * 0.5) )
                
                # yaw and pitch check
                try:
                    dx = abs(screen_center[0] - centerpoint[0])
                    dy = abs(screen_center[1] - centerpoint[1])
                    cax = (dx / centerpoint[0]) * 90
           
                    if ( \
                        True and centerpoint[0] not in range(screen_center[0] - cfg.centering_tolerance, screen_center[0] + cfg.centering_tolerance)  \
                    ):

                        if centerpoint[0] > screen_center[0]:
                            print(f"target is below the centerline by {dy}px")
                            pitch += cfg.pitch_step
                               
                        if centerpoint[0] < screen_center[0]:
                            print(f"target is above the centerline by {dy}px")
                            pitch -= cfg.pitch_step

                        if (pitch > 90): pitch = 90
                        if (pitch < -35): pitch = -35


                    if ( \
                        True and centerpoint[1] not in range(screen_center[1] - cfg.centering_tolerance, screen_center[1] + cfg.centering_tolerance)  \
                    ):
                        if centerpoint[1] > screen_center[1]:
                            print(f"target is to the right of centerline {dx}px")
                            if dx > cfg.yaw_high_step[0]: yaw += cfg.yaw_high_step[1]
                            elif dx > cfg.yaw_mid_step[0]: yaw += cfg.yaw_mid_step[1]
                            else: yaw += cfg.yaw_low_step[1]
                            
                        if centerpoint[1] < screen_center[1]:
                            print(f"target is to the left of centerline {dx}px")
                            if dx > cfg.yaw_high_step[0]: yaw -= cfg.yaw_high_step[1]
                            elif dx > cfg.yaw_mid_step[0]: yaw -= cfg.yaw_mid_step[1]
                            else: yaw -= cfg.yaw_low_step[1]
                                

                        
                        if (yaw > 90): yaw = 90
                        if (yaw < -90): yaw = -90
                        

                    if cfg.enable_hsi:
                        #sri.pitch(pitch)
                        #sri.yaw(yaw)
                        #print(cax, cyx)
                        
                        #pitch += float(0.05 * cyx)
                        #if (pitch > +90): pitch = +90
                        #if (pitch < -35): pitch = -35
                        
                        #if centerpoint[1] not in range(screen_center[1] - cfg.centering_tolerance, screen_center[1] + cfg.centering_tolerance):
                        #    if centerpoint[1] > screen_center[1]:
                        #        yaw  += 0.01 * cax
                        #    if centerpoint[1] < screen_center[1]:
                        #        yaw  -= 0.01 * cax
                        #if (yaw > 90): yaw = +90
                        #if (yaw < 90): yaw = -90
                        
                        sri.pitch(pitch)
                        sri.yaw(yaw)
                        pass
                    
                    camera_input = helpers.line(camera_input, "X=", int(camera_input.shape[1] * 0.5), (255,0,255))
                    camera_input = helpers.line(camera_input, "Y=", int(camera_input.shape[0] * 0.5), (255,0,255))
                    camera_input = cv2.rectangle(camera_input, (screen_center[1] - cfg.centering_tolerance, screen_center[0] - cfg.centering_tolerance), (screen_center[1] + cfg.centering_tolerance, screen_center[0] + cfg.centering_tolerance), (255,0,255), 2 )
                    
                
                    # check if the target is moving or not
                    last_successful_tracks.append(centerpoint)
                    if len(last_successful_tracks) > 3:
                        last_successful_tracks.pop(0)

                    last_success_boxes.append(box)
                    if len(last_success_boxes) > 25:
                        last_success_boxes.pop(0)
                        
                        
                    motionframes = 0    
                    if len(last_successful_tracks) > 1:
                        for i in range(1, len(last_successful_tracks)):
                            if (((last_successful_tracks[i][0] - last_successful_tracks[i-1][0]) ** 2) + ((last_successful_tracks[i][1] - last_successful_tracks[i-1][1]) ** 2)) > 5:
                                motionframes += 1
                                
                    vector_motion = (last_successful_tracks[-1][0] - last_successful_tracks[0][0], last_successful_tracks[-1][1] - last_successful_tracks[0][1])
                    #cv2.line(camera_input, (last_successful_tracks[0][1], last_successful_tracks[0][0]), (last_successful_tracks[-1][1], last_successful_tracks[-1][0]), (0, 255, 0), thickness=3, lineType=8)
                    cv2.arrowedLine(camera_input, (centerpoint[1], centerpoint[0]), (centerpoint[1] + vector_motion[1], centerpoint[0] + vector_motion[0]), (0, 0, 0), thickness=3)

                    mag = round(((vector_motion[0] ** 2) + (vector_motion[1] ** 2)) ** 0.5, 2) 
                    is_moving = mag >= cfg.motion_vector_min_mvmt_mag
                
                except ZeroDivisionError:
                    print("ZeroDivisionError while attempting to move target to center using servos...")
        # IF SUCCESSFUL TRACK  --------------------------------------------
            
            
            
            
            
            # IF BAD TRACK ----------------------------------------------------
            elif (not success):
                failed_tracks += 1

           
            
             # if the failed tracking frame was on one of the edges, we can turn the thing before declaring that we have lost the lock and starting 3R
            if is_moving or keep_going != "STOP":   # we only start doing this if we know for a fact that the subject is moving around
                if centerpoint[1] in range(0, 150) or keep_going == "LEFT":
                   print("The target departed to the left of the frame")
                   yaw -= cfg.yaw_mid_step[1]
                   if (yaw < -90): 
                       yaw = -90
                       keep_going = "RIGHT"
                   else: 
                       #failed_tracks -= 1
                       keep_going = "LEFT"
                   sri.yaw(yaw)
                elif centerpoint[1] in range(camera_input.shape[1] - 150, camera_input.shape[1]) or keep_going  == "RIGHT":
                   print("The target departed to the right of the frame")
                   yaw += cfg.yaw_mid_step[1]
                   if (yaw > 90): 
                       yaw = 90
                       keep_going = "LEFT"
                   else: 
                       #failed_tracks -= 1
                       keep_going = "RIGHT"
                   sri.yaw(yaw)
			   
               """ if centerpoint[0] in range(0, 150) or keep_going  == "UP":
                   print("The target departed to the top of the frame")
                   pitch -= 1 
                   if (pitch < -35): 
                       pitch = -35
                       keep_going = "STOP"
                   else: 
                       #failed_tracks -= 1
                       keep_going = "UP"
                   sri.pitch(pitch)
                elif centerpoint[0] in range(camera_input.shape[0] - 150, camera_input.shape[0]) or keep_going  == "DOWN":
                   print("The target departed to the bottom of the frame")
                   pitch += 1
                   if (pitch > 90): 
                       pitch = 90
                       keep_going = "STOP"
                   else: 
                       #failed_tracks -= 1
                       keep_going = "DOWN"
                   sri.pitch(pitch)
	      """

            # if the failed track frames have exceeded the unlock limit
            if (failed_tracks >= failed_tracks_thresh):
                the_tracker = None
                lock = "SCAN"
                failed_tracks = 0

                # 3R ATTEMPT -----------------------------------------------------------
            if (failed_tracks >= cfg.attempt_drr_after and cfg.attempt_detect_resolve_relock):
                print("Attempting a redetection after a failed lock...")
                # REDETECT (this is mostly a copy of the code located in the SCAN portion, minus the portions for sorting and LPO
                
                polygons = []
                for i in inuse:
                    polygons += i._attempt_detection(camera_input, filterdata)[0]
                #print(f"{len(polygons)} detections in total,")
                
                  
                  
                  
                # RESOLUTION (this will pick out the detection that is closest to the thing, and only within the bounding box
                the_bbox = None
                
                acceptable = []
                for old_bbox in last_success_boxes:
                    old_bbox = helpers.resizeBox(old_bbox, cfg.neighbor_box_resize)
                    if old_bbox[2] < cfg.min_neighbor_box_w: old_bbox = (old_bbox[0], old_bbox[1], cfg.min_neighbor_box_w, old_bbox[3])
                    if old_bbox[3] < cfg.min_neighbor_box_w: old_bbox = (old_bbox[0], old_bbox[1], old_bbox[2], cfg.min_neighbor_box_h)
                    camera_input = cv2.rectangle(camera_input, old_bbox, (100,0,0), 2)
                
                    for i in polygons:
                        # first, check if the detection is a neighbor of the the original bbox
                        # if not, show it but draw it in red to show that it was rejected
                        if helpers.AtouchesB(i, old_bbox) or not cfg.drr_require_neighbor:
                            if i not in acceptable: acceptable.append(i)
                        else:
                            cv2.rectangle(camera_input, i, (0, 0, 100), 2)
                    #print(f"Of {len(polygons)} detections, {len(acceptable)} are neighboring will be considered,")
                
                if len(acceptable) > 0:
                    acceptable_2 = []
                    for i in acceptable:
                        # second, throw out detections that are not about the same size of the original
                        lower = (1 - cfg.drr_sizematch_tolerance)
                        upper = (1 + cfg.drr_sizematch_tolerance)
                        if ((last_success_box[2] * lower <= i[2] <= last_success_box[2] * upper) and (last_success_box[3] * lower <= i[3] <= last_success_box[3] * upper))  \
                        or ((last_success_box[2] * lower <= i[3] <= last_success_box[2] * upper) and (last_success_box[3] * lower <= i[2] <= last_success_box[3] * upper))  \
                        or (not cfg.drr_require_sizematch): \
                            acceptable_2.append(i)
                        else:
                            cv2.rectangle(camera_input, i, (0, 0, 100), 2)
                    #print(f"Of {len(acceptable)} neighboring detections, {len(acceptable_2)} of approximately correct size profile will be considered,")    
                    if len(acceptable_2) > 0:
                        final = {}
                        for i in acceptable_2:
                            # draw detections
                            camera_input = cv2.rectangle(camera_input, i, (0, 100, 100), 2)
                            if cfg.drr_resolve_using == "DIST":  final[int((((last_success_box[0] - i[0]) ** 2) + ((last_success_box[1] - i[1]) ** 2)) ** 0.5)] = i
                            if cfg.drr_resolve_using == "SIZE":  final[abs((i[0] * i[1]) - (last_success_box[0] * last_success_box[1]))] = i
                        #print(f"Choosing from: {final}")
                        final = final[min(list(final.keys()))]
                        print(f"Finally selected: {final}")
                        cv2.rectangle(camera_input, final, (0, 200, 0), 2)
                        

        
                
                # RELOCKING (indented this way because it should only run when we get a final answer - if there are no detections for instance, we should do nothing)
                        try:
                            for i in trackers_inuse:
                                i._init(last_successful_frame, final)
                                print("auto redetect-resolve-relock: Initialized a tracker "+str(i))
                            lock = "LOCK"
                            failed_tracks = 0
                            vector_motion = (0,0)
                            is_moving = False
                            keep_going = "STOP"
                            print("auto redetect-resolve-relock: Locked on subject with ROI "+str(final))
                        except Exception as e:
                            print("auto redetect-resolve-relock: Failed to lock onto ROI "+str(final)+": "+str(e))
                # 3R ATTEMPT -----------------------------------------------------------

        # -----------------------------------------------------------
 
           
           
           
           
           
    # POST CV PIPELINE ------------------------------------------
        fps = int(cv2.getTickFrequency() / (cv2.getTickCount() - timer))
        if (only_draw_biggest_polygon): polset = "LPONLY"
        else: polset = "ALL"

        if not cfg.enable_networking:
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
                f"""AUTOLOCK: {lock} {polset} {'MVMT' if is_moving else 'STILL'}:{vector_motion} |{mag}| {len(polygons)}d {failed_tracks}/{failed_tracks_thresh}ftfs """.replace("\n", ""),
                (5,55),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255,255,0)
            )
            cv2.putText(
                camera_input,
                f"""CONNECTIVITY: DISABLED""".replace("\n", ""),
                (5,75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (0,0,255)
            )
            cv2.putText(
                camera_input,
                f"""SERVO: {pitch}deg pitch    {yaw}deg yaw""".replace("\n", ""),
                (5,95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (0,0,0)
            )
            cv2.putText(
                camera_input,
                f"""KB: [F]ire [R]ev, [Q]uit, LP[O] [U]nlock Reloa[D]PL [0-9]Select""".replace("\n", ""),
                (5,115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (0,100,0)
            )
        else:
            encoded_text.append( [5, 35, (0, 100, 100), 0.35, f"""CAMERA: {fps}fps  cam#{device}""" ] )
            encoded_text.append( [5, 45, (100, 100, 0), 0.35, f"""AUTOLOCK: {lock} {polset} {'MVMT' if is_moving else 'STILL'}:{vector_motion} |{mag}| {len(polygons)}d {failed_tracks}/{failed_tracks_thresh}ftfs""" ] )
            encoded_text.append( [5, 55, (0, 0, 255), 0.35, f"""CONNECTIVITY: ENABLED [self]:{cfg.TCP_port}<=>{net.TCP_REMOTE_PEER[0]}:{net.TCP_REMOTE_PEER[1]}""" ] )
            encoded_text.append( [5, 65, (0, 0, 0), 0.35, f"""SYSTEM: {pitch}deg pitch  {yaw}deg yaw""" ] )


                
        # either display the image or prepare it for transmission over socket
        if not cfg.enable_networking or cfg.show_local_output:
            cv2.imshow("output",camera_input)
        if cfg.enable_networking:
            old_shape = camera_input.shape
            camera_input = cv2.resize(camera_input, (0,0), fx=compression, fy=compression) 
            d = pickle.dumps(camera_input)
            # encode polygons and text
            text = pickle.dumps(encoded_text)
            shape = pickle.dumps(old_shape)
            # transmit over socket
            net.sendTo("UDP", net.UDP_SOCKET, d + b"::::" + text + b"::::" + shape, net.TCP_REMOTE_PEER[0])
    # ----------------------------------------------


    # WIRELESS NETWORKING/CMD LOGIC (control packets that are sent over the TCP signaling channel) ----------
    if cfg.enable_networking:
        command = net.readFrom("TCP", net.TCP_CONNECTION, 2048)
        if not command:
            command = net.readFrom("UDP", net.UDP_SOCKET, 2048)
    else:
        # if networking is off, we can sub in key presses for TCP/UDP packets containing the same instructions 
        kb = cv2.waitKey(1)
        if   kb == ord("f"):
            command = "dtoggle fire"
        elif kb == ord("r"):
            command = "dtoggle rev"
        elif kb == ord("q"):
            command = "stop 0"
        elif kb == ord("o"):
            command = "toggle_lpo 0"
        elif kb == ord("u"):
            command = "forget 0"
        elif (48 <= kb <= 57):
            command = f"select {kb-48}"
        elif kb == ord("d"):
            updatePipeline()
       
    # ---------------------------------------------------------------------------------------------------------




    # ACT ON COMMAND FROM SOCKET OR KB -------------------------------------------------------------------------
    if command:
            try: multicmd = str(command, "ascii").split(";")
            except: multicmd = command.split(";")
            for i in multicmd:
                command = str(i).split(" ")
                try:
                    if command[0] == "abspitch":
                        print(f"remote cmd: pitch {command[1]}")
                        if cfg.enable_hsi: sri.pitch(float(command[1]))
                        pitch = float(command[1])
                    elif command[0] == "absyaw":
                        print(f"remote cmd: yaw {command[1]}")
                        if cfg.enable_hsi: sri.yaw(float(command[1]))
                        yaw = float(command[1])
                    elif command[0] == "toggle_lpo":
                        print(f"remote cmd: toggle_LPO {only_draw_biggest_polygon}->{not only_draw_biggest_polygon}")
                        only_draw_biggest_polygon = not only_draw_biggest_polygon
                    elif command[0] == "select":
                        kb = int(command[1])
                        try:
                            for i in trackers_inuse:
                                i._init(last_successful_frame, polygons[kb])
                                print("remote cmd: Initialized a tracker "+str(i))
                            lock = "LOCK"
                            failed_tracks = 0
                            vector_motion = (0,0)
                            is_moving = False
                            keep_going = "STOP"
                            print("remote cmd: Locked on subject #"+str(kb)+" at the command of the remote.")
                        except Exception as e:
                            print("remote cmd: Failed to lock onto subject #"+str(kb)+": "+str(e))
                    elif command[0] == "forget":
                        the_tracker = None
                        lock = "SCAN"
                        failed_tracks = 0
                        print("remote cmd: Lock released by remote.")
                    elif command[0] == "updatepipeline":
                        print("remote cmd: Reloading the pipeline at the command of the remote.")
                        updatePipeline()
                    elif command[0] == "stop":
                        latch = False
                        reason = 0
                    elif command[0] == "restart" and cfg.enable_networking:
                        latch = False
                        reason = 1
                    elif command[0] == "dtoggle" and cfg.enable_hsi:
                        if command[1] == "fire":
                            sri.toggleFire()
                            print("remote cmd: dtoggle fire")
                        elif command[1] == "rev":
                            sri.toggleRev()
                            print("remote cmd: dtoggle rev")
                        
                
                except (ValueError, KeyError, IndexError) as e:
                    print(f"Invalid command! No action was taken: "+str(e))
                except AssertionError as e:
                    print("AssertionError! Command: "+str(e))


            # clear the buffers, both the TCP signalling channel and the UDP channel
            if cfg.enable_networking:
                try:
                    while net.UDP_SOCKET.recv(65535): pass
                except:
                    pass

                try:
                    while net.TCP_CONNECTION.recv(65535): pass
                except:
                    pass
    # -------------------------------------------






# release resources when done
print("Gracefully shutting down...")
cv2.destroyAllWindows()
cap.release()
if cfg.enable_hsi:
    sri.__shutdown()
if cfg.enable_networking:
    net.TCP_SOCKET.close()
    net.UDP_SOCKET.close()
if reason == 1:
    os.chdir("..")
    os.system(cfg.restart_command)
    
    
