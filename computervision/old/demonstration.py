print("Starting up...")
import cv2
import numpy as np
import color_track_return_rectangle as ct2r
import helpers

# set up webcam acs
device = None
latch = True
polygons = []

if device == None: device = int(input("--Which device (enter an int)? "))

cap = cv2.VideoCapture(device)
if not cap.isOpened():
    println("--Webcam entry point failed to initialize!")
    exit(-1)


# set up tracker with default parameters
ct2r._init(lhs = 20, lha = 20, lss = 75, lblur = 15, lminPolygonWidth = 50, lminPolygonHeight = 50)
only_draw_biggest_polygon = True


# onlock handler
def onclick(event, x, y, *argv):
    pass
    
# set up output windows
cv2.namedWindow("input")
cv2.namedWindow("output")
cv2.setMouseCallback("input", onclick)


print("Ready!")

while latch:
    timer = cv2.getTickCount()
    ret, camera_input = cap.read()
    if (ret):
        camera_input = helpers.increase_brightness(camera_input, value=10)
        cv2.imshow("input", camera_input)
        
        # get polygons back out of the tracking methods
        polygons, output = ct2r._attempt_detection(camera_input, {"colormasks":
        [
            {"colormask_upper": ct2r.colors["upper_dark_blue"], "colormask_lower": ct2r.colors["lower_dark_blue"]},
            {"colormask_upper": ct2r.colors["upper_light_blue"], "colormask_lower": ct2r.colors["lower_light_blue"]},       
            {"colormask_upper": ct2r.colors["upper_green"], "colormask_lower": ct2r.colors["lower_green"]},            
        ]
        })
        if not only_draw_biggest_polygon:
            for i in polygons:
                x, y, w, h = i
                cv2.rectangle(camera_input, (x,y), (x+w,y+h), (255, 255, 0), 2)
                # if all polygons that were able to be produced are to be drawn, draw in cyan
        else:
            largestPolygon = (-1, -1, -1, -1)
            for i in polygons:
                x, y, w, h = i
                if (w > largestPolygon[2] and h > largestPolygon[3]):
                    largestPolygon = (x, y, w, h)
            x, y, w, h = largestPolygon
            cv2.rectangle(camera_input, (x,y), (x+w,y+h), (255, 0, 255), 2)
            # if only the largest polygon is being drawn, draw in magenta
            
            
           
           # list FPS
            fps = int(cv2.getTickFrequency() / (cv2.getTickCount() - timer))
            cv2.putText(
                camera_input,
                "fps:" + str(fps),
                (5,35),
                cv2.FONT_HERSHEY_DUPLEX,
                0.35,
                (255,255,0)
            )
                
            
        
        cv2.imshow("output", camera_input)
        
    # waitKey so the program doesn't crash
    # press Q to quit
    kb = cv2.waitKey(1)
    if (kb == ord("q")):
        latch = False
    
    
# release resources when done
cv2.destroyAllWindows()
cap.release()
