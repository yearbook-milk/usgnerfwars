# NETWORKING SETTINGS:
TCP_port = 10007                                    # TCP signaling channel port number
UDP_port = 10009                                    # UDP data channel port number
enable_networking = True                            # Whether or not to enable networking at all (for dev/debug only)

checkip_command = "ifconfig"                        # On startup, this cmd will run and its result printed out in console
                                                    # This should be your OS' network adapter info command, so you can see 
                                                    # its current IP address.

restart_command = "start python main.py"            # What command to run if the remote tells the RPi to restart this program.

# HARDWARE SOFTWARE INTERFACE SETTINGS:
pin_config = {                                      # These control which pins on the RPi do what.
    
"leftPin": 18,
"rightPin": 13,
"yawPin": 12,
"afterSpdCmdDelay": 0,                              # This should be set to 0, in order to make the pitch and yaw cmds nonblocking.
"pulse_freq": 50,                                    # Pulse frequency, in hZ.
"pinsToSet": "leftPin rightPin yawPin",             # DONT CHANGE THIS 


"revPin": 23,
"firePin": 24,

}

enable_hsi = True                                   # Whether or not to enable the hardware-software interface (setting for developers
                                                    # to be able to test on a non-RPi device)



# DISPLAY SETTINGS:
show_local_output = False                           # Whether or not to display a video feed locally.





# COMPUTER VISION SETTINGS
ct2r_hue_lower_tolerance = 20
ct2r_hue_upper_tolerance = 20
ct2r_saturation_lower_tolerance = 0
ct2r_blur_level = 15
ct2r_minpolywidth = 40
ct2r_minpolyht = 40

default_camera = 0


# AUTO TARGET SETTINGS
centering_tolerance = 50

pitch_step =      1

yaw_high_step =   (85, 3)
yaw_mid_step =    (65, 2.25)
yaw_low_step =    (0, 1.2)



