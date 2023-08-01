import pigpio
import time


config = {
    
"leftPin": 0,
"rightPin": 0,
"yawPin": 0,

"revPin": 0,
"firePin": 0,


"afterSpdCmdDelay": 0,
"pulse_freq": 50,
"pinsToSet": "leftPin rightPin yawPin"    

}

rev = False
fire = False

def legacy_angle_to_percent(angle):
    assert ((angle > 180 or angle < 0) == False)
    start = 4
    end = 12.5
    ratio = (end - start)/180 
    angle_as_percent = angle * ratio
    return start + angle_as_percent

def angle_to_pulse_width(angle):
    #print(500 + ( (2500-500) * float(angle) / 180) )  
    return 500 + ( (2500-500) * float(angle) / 180)

def centerAllAxes():
    global pwmL, pwmR, config, pwmP, pwm
    for i in config["pinsToSet"].split(" "):
        pwm.set_servo_pulsewidth( config[i],  angle_to_pulse_width(90))
    time.sleep(config["afterSpdCmdDelay"])


def pitch(angle):
    global pwmL, pwmR, config, pwmP, pwm
    assert (-90 <= angle <= 90)
    angle += 90
    pwm.set_servo_pulsewidth( config["leftPin"], angle_to_pulse_width(angle) )
    pwm.set_servo_pulsewidth( config["rightPin"], angle_to_pulse_width(180 - angle) )
    time.sleep(config["afterSpdCmdDelay"])
    
def yaw(angle):
    global pwmL, pwmR, config, pwmP, pwm
    assert (-90 <= angle <= 90)
    angle += 90
    pwm.set_servo_pulsewidth( config["yawPin"], angle_to_pulse_width(angle) )
    time.sleep(config["afterSpdCmdDelay"])
    
def toggleFire():
    global pwm, config,  fire
    pwm.write(config["firePin"], int(not fire)) 
    fire = not fire

def toggleRev():
    global pwm, config,  rev
    pwm.write(config["revPin"], int(not rev)) 
    rev = not rev

def __initialize():
    global GPIO, pwmL, pwmR, pwmP, pwm
    global config

    #GPIO.setmode(GPIO.BOARD) #Use Board numerotation mode
    #GPIO.setwarnings(False) #Disable warnings
    
    frequence = config["pulse_freq"]

    pwm = pigpio.pi()
    
    
    for i in config["pinsToSet"].split(" "):
        pwm.set_mode(config[i], pigpio.OUTPUT)
        pwm.set_PWM_frequency( config[i], frequence )


       
    

def __shutdown():
    global pwmL, pwmR, config, pwmP, pwm
    global config
    #Close GPIO & cleanup
    for i in config["pinsToSet"].split(" "):
        pwm.set_PWM_dutycycle( config[i], 0 )
    global fire, rev
    if fire: toggleFire()
    
    if rev: toggleRev()

