# NETWORKING SETTINGS:
TCP_port = 10007                                    # TCP signaling channel port number
UDP_port = 10009                                    # UDP data channel port number
enable_networking = True                            # Whether or not to enable networking at all (or operate locally)

checkip_command = "ipconfig"                        # On startup, this cmd will run and its result printed out in console
                                                    # This should be your OS' network adapter info command, so you can see 
                                                    # its current IP address.

# HARDWARE SOFTWARE INTERFACE SETTINGS:
pin_config = {                                      # These control which pins on the RPi do what.
    
"leftPin": 12,
"rightPin": 33,
"yawPin": 32,
"afterSpdCmdDelay": 0,                              # This should be set to 0, in order to make the pitch and yaw cmds nonblocking.
"pulse_freq": 50                                    # Pulse frequency, in hZ. 
    
}

enable_hsi = False                                  # Whether or not to enable the hardware-software interface (setting for developers
                                                    # to be able to test on a non-RPi device)


#

