# import all the stuff we need
print("Starting up...")
import cv2
from collections import Counter
import numpy as np
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings("ignore")
print("--Imported all libraries")

# this controls whether or not the image is scaled down to make detection faster (it will become less accurate by doing so)
do_image_scaledown = 1.0

# this variable tells us whether we're scanning for people or locked onto a single person
# this will start out scanning for people, and when the user locks onto someone, this will change to "LOCK"
# if the camera loses sight of the person, it will go back to scan
currently_locked = "SCAN"

# however, if the person goes out of frame, the variable IDD will remember information about their shirt color or something (idk haven't decided yet)
# so if the camera finds another person with similar features, it will know to re lock onto that person
idd = "EMPTY"

# if you don't want to enable auto relocking, set this to false
relock = True

# the object cv2 uses to represent a person being tracked will be stored here
the_tracker = None

# because we don't run the detection alg every frame, we run it at a detect_every_x_frames frame interval
detect_every_x_frames = 20



# helpers
def println(toPrint):
    print(toPrint)
    # this comes from when the program was in cpp

def most_frequent(List):
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]

def mean(List):
    return sum(List) / len(List)

def rectContains(rect,pt):
    logic = rect[0] < pt[0] < rect[0]+rect[2] and rect[1] < pt[1] < rect[1]+rect[3]
    return logic

def dominantcolor(a, b):
    # https://towardsdatascience.com/finding-most-common-colors-in-python-47ea0767a06a
    cluster = KMeans(n_clusters = 3)
    cluster.fit(a.reshape(-1,3))
    return cluster.cluster_centers_[b]

# when a user hits one of the number keys, it will call this callback (it isn't triggered by clicking on the frame anymore)
def onclick(i, frame):
            (xb, yb, wb, hb) = [int(j) for j in people.tolist()[i]]
            hasSelected = i
            global the_tracker, trackers
            the_tracker = trackers[i]
            print("--OK! Locked onto subject "+str(i))
            global currently_locked
            currently_locked = "LOCK"
            # if we ever lose the lock on target, we note down their shirt color so that if they ever come back they can be reidentified
            # and relocked
            global camera_input
            return None

# store the bounding boxes of the people that are detected
people = []

# store the tracker objects used to represent tracked people
trackers = []

# initialize the person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# open up windows and start the webcam
cv2.namedWindow("final")
cv2.namedWindow("dbg1")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    println("--Webcam entry point failed to initialize!")
    exit(-1)

latch = True
frame_number = 0
println("--Webcam entry point initialized")


# start looping, perpetually taking frames from the camera
print("Ready!")
while latch:
    timer = cv2.getTickCount()
    ret, camera_input = cap.read()

    if ret:
        # scale the image down or up if needed
        oldWidth, oldHeight = camera_input.shape[0], camera_input.shape[1]
        if do_image_scaledown > 0:
            camera_input = cv2.resize(camera_input, None, fx=do_image_scaledown, fy=do_image_scaledown, interpolation=cv2.INTER_LINEAR)

        # if on scan mode
        if currently_locked != "LOCK":
            # we only run detection every 20 frames, and have a tracking alg take its place in the other 19 frames
            if frame_number >= detect_every_x_frames or frame_number == 0:
                people, _ = hog.detectMultiScale(camera_input, winStride=(4, 4), padding=(4, 4), scale=1.05, groupThreshold=2)
                trackers = []
                for i in people:
                    # people is populated with an array of bounding boxes with people within
                    # each bounding box is given a corresponding
                    trackers.append(cv2.TrackerCSRT_create())
                    trackers[-1].init(camera_input, i)
                frame_number = 0

            # The other 19 frames, we use a tracking algorithm to essentially guess where each person who was in frame is
            ifn = 0
            for i in trackers:
                success, box = i.update(camera_input)
                if success:
                    # draw a rectangle around where the alg thinks the person is
                    (x, y, w, h) = [int(v) for v in box]
                    people[ifn] = box
                    cv2.rectangle(camera_input, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(camera_input, "human "+str(ifn), (x, y), cv2.FONT_HERSHEY_DUPLEX, 0.50, (0,0,255))

                    # if auto relock is on, check to see if the detected person matches the stored profile, and if it does,
                    # lock onto that person specifically
                    if relock:
                        try:
                            compositecolor = dominantcolor( camera_input[y:y+h,x:x+w], 1)
                            if (idd != "EMPTY" and relock and (\
                                idd[0] * 0.89 < compositecolor[0] < idd[0] * 1.12 and \
                                idd[1] * 0.89 < compositecolor[1] < idd[1] * 1.12 and \
                                idd[2] * 0.89 < compositecolor[2] < idd[2] * 1.12)):
                                print(f"Redetected: {compositecolor} within range of {idd}")
                                onclick(ifn, camera_input)
                        except:
                            pass

                    ifn += 1


        # if locked onto a specific person
        elif currently_locked == "LOCK":
            # if tracker object reports error or is somehow missing
            if the_tracker == None:
                currently_locked = "SCAN"
            else:
                # use that person's tracking object to estimate where they are
                success, box = the_tracker.update(camera_input)
                if success:
                    # if the alg can find them, draw a yellow box around them and take down their shirt color
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(camera_input, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    cv2.putText(camera_input, "LOCK", (x, y), cv2.FONT_HERSHEY_DUPLEX, 0.50, (0,255,255))
                    try: cv2.imshow("dbg1", camera_input[y:y+h,x:x+w])
                    except: pass
                    if idd == "EMPTY" and relock:
                        idd = dominantcolor( camera_input[y:y+h,x:x+w], 1)
                        print("Shirt color:",idd)
                else:
                    # if the alg has lost sight of the person, start scanning again, with the person's profile in memory
                    currently_locked = "SCAN"
                    pass
                    

        # get fps
        fps = int(cv2.getTickFrequency() / (cv2.getTickCount() - timer));
        
        # print out some information
        cv2.putText(
            camera_input,
            "nW:" + str(int(do_image_scaledown * oldWidth))
            + " nH:" + str(int(do_image_scaledown * oldHeight))
            + " fn:" + str(frame_number) + "/" + str(detect_every_x_frames)
            + " dtd:" + str(len(people))
            + " mode:" + currently_locked
            + " fps:" + str(fps),
            (5, 15),
            cv2.FONT_HERSHEY_DUPLEX,
            0.35,
            (255, 255, 0)
        )
        cv2.putText(
            camera_input,
            " p/id:" + str(idd),
            (5,35),
            cv2.FONT_HERSHEY_DUPLEX,
            0.35,
            (255,255,0)
        )
        cv2.putText(
            camera_input,
            "[R] Release lock, [1-9] Lock onto target, [F] Freeze frame, [Q] Quit",
            (5,55),
            cv2.FONT_HERSHEY_DUPLEX,
            0.35,
            (255,255,0)
        )

        # At last, show the finished image
        camera_input = cv2.resize(camera_input, (oldHeight, oldWidth), interpolation=cv2.INTER_LINEAR)
        cv2.imshow("final", camera_input)
        frame_number += 1
    else:
        continue


    # if the user has pressed a key, do something (such as undo a lock/release person profile or lock onto the person labeled "0")
    kb = cv2.waitKey(20)
    if kb == ord('r'):
            currently_locked = "SCAN"
            the_tracker = None
            idd = "EMPTY"
            print("Unlocked from target and deleted target profile")
    if kb == ord('1'):
        print("Attempting to lock onto target#0")
        try:
            the_tracker = None
            onclick(0, camera_input)
            idd = "EMPTY"
            print("Done!")
        except Exception as e:
            print("Could not lock onto target: "+str(e))
    if kb == ord('f'):
        print("Frame frozen! <ENTER> to unfreeze")
        input()
    if kb == ord('q'):
        exit()


# release cam acs resource after done
cap.release()
cv2.destroyAllWindows()
