

# * = this setting is only applied on start up, and changing it/applying changes while main is running will have no fx

# [NETWORKING] *
TCP_port = 10008                                    
UDP_port = 10009                                    
enable_networking = True                           
checkip_command = "ifconfig"                        
restart_command = "start python main.py"
network_image_compression = 0.15



# [HARDWARE SOFTWARE INTERFACE] *
pin_config = {                                      

"leftPin": 18,
"rightPin": 13,
"yawPin": 12,
"afterSpdCmdDelay": 0,                              
"pulse_freq": 50,                                    
"pinsToSet": "leftPin rightPin yawPin",             

"revPin": 23,
"firePin": 24,

"yaw_limits": (-90, 90),
"pitch_limits": (-30, 30),
}



enable_hsi = True                      


# [LOCAL DISPLAY] *
show_local_output = False                           


# [POTENTIAL TARGET DETECTION]
ct2r_hue_lower_tolerance = 10
ct2r_hue_upper_tolerance = 10
ct2r_saturation_lower_tolerance = 10
ct2r_blur_level = 25
ct2r_minpolywidth = 70
ct2r_minpolyht = 70
ct2r_maxpolywidth = 120
ct2r_maxpolyht = 240
ct2r_min_hsv_value = 150

default_camera = 0

failed_tracking_frames_thresh = 200
image_resize_factor = 1.0


# [AUTO REDETECT/RESOLVE/RELOCK AFTER TRACKING FAIL]
attempt_detect_resolve_relock = True
attempt_drr_after = 2

drr_require_neighbor = True
neighbor_box_resize = 1.05
min_neighbor_box_h = 160
min_neighbor_box_w = 160

drr_require_sizematch = True
drr_sizematch_tolerance = 0.45

drr_resolve_using = "SIZE"
assert drr_resolve_using == "SIZE" or drr_resolve_using == "DIST"



# [AUTO AIM VIA SERVO]
centering_tolerance = 55


centering_method = "RATIO"
assert centering_method == "STEP" or centering_method == "RATIO"

yaw_high_step =   (120, 3.15)
yaw_mid_step =    (64, 1.25)
yaw_low_step =    (0, 0.71)
pitch_high_step =   (120, 3.15)
pitch_mid_step =    (64, 1.25)
pitch_low_step =    (0, 0.71)

yaw_to_edge_of_frame_deg = 3.25
pitch_to_edge_of_frame_deg = -2

motion_vector_min_mvmt_mag = 8.5

yaw_exit_frame_detection = True
yaw_exit_frame_continuesweep = False
yaw_exit_frame_detect_by_vector = False
yaw_exit_frame_detect_by_position = True


# FIRE CONTROL
max_seconds_rev = 5
