import servo_relay_interface as sri
import time 

sri.config["leftPin"] = 12
sri.config["rightPin"] = 33
sri.config["yawPin"] = 32
sri.config["afterSpdCmdDelay"] = 0.8
sri.config["pulse_freq"] = 50

sri.__initialize()
sri.centerAllAxes()

while True:
    try:
        sri.pitch(+90)
        time.sleep(1)
        sri.pitch(-90)
        time.sleep(1)
        sri.yaw(-90)
        time.sleep(1)
        sri.yaw(90)
    except KeyboardInterrupt:
        sri.centerAllAxes()
        sri.__shutdown()
        exit()