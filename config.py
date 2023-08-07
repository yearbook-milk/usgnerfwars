# * = this setting is only applied on start up, and changing it/applying changes while main is running will have no fx

# [NETWORKING] *
TCP_port = 10007                                    
UDP_port = 10009                                    
enable_networking = False                           
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

}

enable_hsi = False                                  


# [LOCAL DISPLAY] *
show_local_output = False                           


# [POTENTIAL TARGET DETECTION]
ct2r_hue_lower_tolerance = 25
ct2r_hue_upper_tolerance = 25
ct2r_saturation_lower_tolerance = 69
ct2r_blur_level = 15
ct2r_minpolywidth = 40
ct2r_minpolyht = 40

default_camera = 0

failed_tracking_frames_thresh = 1100
image_resize_factor = 1.0


# [AUTO REDETECT/RESOLVE/RELOCK AFTER TRACKING FAIL]
attempt_detect_resolve_relock = True
attempt_drr_after = 1

drr_require_neighbor = True

drr_require_sizematch = False
drr_sizematch_tolerance = 0.35





# [AUTO AIM VIA SERVO]
centering_tolerance = 50

pitch_step =      1

yaw_high_step =   (85, 3)
yaw_mid_step =    (45, 2.75)
yaw_low_step =    (0, 1.3)

yaw_exit_frame_detection = True
yaw_exit_frames_thresh = 5

