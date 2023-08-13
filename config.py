if True:
# * = this setting is only applied on start up, and changing it/applying changes while main is running will have no fx

# [NETWORKING] *
    TCP_port = 10008                                    
    UDP_port = 10009                         
    enable_networking = False            

    # what command to run on startup to show network adapter info (ipconfig on windows, ifconfig on linux)               
    checkip_command = "ifconfig"                        
    restart_command = "start python main.py" 

    # how much to compress the image to when sending over UDP_port
    # i.e. 0.20 compresses the image to 20% of its original size before serializing and sending
    network_image_compression = 0.15 



# [HARDWARE SOFTWARE INTERFACE] *
    pin_config = {                                      

    # which pins do that (note that the left, right and yaw pins need to be PWM enabled on your device)
    "leftPin": 18,
    "rightPin": 13,
    "yawPin": 12,
    "revPin": 23,
    "firePin": 24,

    # set this to 0
    "afterSpdCmdDelay": 0,    

    # pwm wave properties                          
    "pulse_freq": 50,    
    "min_pulse_length": 500,
    "max_pulse_length": 2500,  # these depend on the specified pulse lengths of your servos

    # DONT CHANGE THIS                               
    "pinsToSet": "leftPin rightPin yawPin",             

    # limits for pitch and yaw commands
    # if you know for a fact that turning the pitch past 45 for example might cause damage, set a software 
    # limit/safety for that there
    "yaw_limits": (-90, 90),
    "pitch_limits": (-30, 30),


    }


    # whether or not to even use the hardware software interface
    enable_hsi = False                      


# [LOCAL DISPLAY]
    show_local_output = False    
    # this setting does nothing                        

# [POTENTIAL TARGET DETECTION]
    default_camera = 0

    # how many frames can go by with the tracker not seeing any targets before automatically going back to redetecting
    failed_tracking_frames_thresh = 200

    # how much to resize the image to prior to running detection and tracking
    image_resize_factor = 1.0


# [AUTO REDETECT/RESOLVE/RELOCK AFTER TRACKING FAIL]

    # whether or not to do auto redetections and relocking when tracker can't see the target anymore
    attempt_detect_resolve_relock = True
    # DONT CHANGE
    attempt_drr_after = 1


    # require that redetections found after a tracking fail to be close to where the target was last seen by the tracker
    drr_require_neighbor = True

    # "what is considered a neighbor of the target?" bounding box size
    neighbor_box_resize = 1.05
    # if your target was tiny, chances are auto redetect will also fail, so if that's the case you'll want to expand that box
    min_neighbor_box_h = 160
    min_neighbor_box_w = 160

    # require that redetections be close in size to the original target
    drr_require_sizematch = True
    # how much size deviation is tolerable. the more this number the more tolerance
    drr_sizematch_tolerance = 0.45

    # when choosing a target from multiple automatic redetections, use the following method to decide which one to relock to:
    drr_resolve_using = "SIZE"

    # SIZE will choose the target closest in size to the original, and DIST will choose the target closest in position to the original target
    assert drr_resolve_using == "SIZE" or drr_resolve_using == "DIST"



# [AUTO AIM VIA SERVO]
            
    # controls the size of the purple box in the middle
    # that's the "tolerance" box, which essentially means, "if the center of the target is in that box, don't try to make corrections even if its slightly off"
    centering_tolerance = 55

    # RATIO mode does some math to figure out how much to turn, whereas STEP simply says, "OK, if its a little to the left, turn X deg, if its a lot to the left, turn Y deg"
    centering_method = "RATIO"
    assert centering_method == "STEP" or centering_method == "RATIO"

    # each of these tuples is in the format (threshold, degrees_to_turn)
    # if you have yaw_high_step = (100, 3.15), this means that the servos will turn 3.15 degrees left or right when the center of the target is more than 100 px away from the center line
    yaw_high_step =   (120, 3.15)
    yaw_mid_step =    (64, 1.25)
    yaw_low_step =    (0, 0.71)
    pitch_high_step =   (120, 3.15)
    pitch_mid_step =    (64, 1.25)
    pitch_low_step =    (0, 0.71)

    # these numbers are supposed to represent how many degrees the servos should turn to take an object from the edge (either top or left) of the frame to the middle
    # but in actuality we just guessed and these numbers work
    yaw_to_edge_of_frame_deg = 3.25
    pitch_to_edge_of_frame_deg = -2

    # the mininum magnitude of the motion vector (calculated using the last 3ish frames) to be considered moving
    motion_vector_min_mvmt_mag = 8.5

    # these settings control the "if the person was last seen moving to the right and is no longer visible, assume that they went right and turn right 
    # even if the person isn't in frame (essentially a basic form of object permeance)
    # they don't work that well though so I suggest disable them
    yaw_exit_frame_detection = True
    yaw_exit_frame_continuesweep = False
    yaw_exit_frame_detect_by_vector = False
    yaw_exit_frame_detect_by_position = True


# FIRE CONTROL

    # This setting doesn't work anymore, but it's the max amount of time 
    # the rev can be active for (as to avoid damage to the launching apparatus)
    max_seconds_rev = 5
