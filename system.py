import RPi.GPIO as GPIO
import time
from picamera import PiCamera

led_red = 15
led_green = 16
motion = 12           # motion detector
servo = 10            # door engine
dist_eco = 7          # input
dist_t = 8            # out
buzzer = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_red, GPIO.OUT)
GPIO.setup(led_green, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(servo, GPIO.OUT)
GPIO.setup(dist_t, GPIO.OUT)
GPIO.setup(dist_eco, GPIO.IN)
GPIO.setup(motion, GPIO.IN)

servo = GPIO.PWM(servo, 50)
servo.start(7.5)

# turn on and off the green/red led
def lightStatus(state):
    if state == 'close':
        GPIO.output(led_red, GPIO.HIGH)
        GPIO.output(led_green, GPIO.LOW)
    else:
        GPIO.output(led_red, GPIO.LOW)
        GPIO.output(led_green, GPIO.HIGH)

# turn on buzzer for 5 seconds  
def buzzOn():
    GPIO.output(buzzer, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(buzzer, GPIO.LOW)

# used to take photo of the client
def video(state):
    my_camera = PiCamera()
    
    if state:
        camera.start_recording('/home/pi/Desktop/video.h264')
    else:
        camera.stop_recording()
        my_camera.close()

# door commands
def doorStatus(state):
    if state == 'open':
        # open
        servo.ChangeDutyCycle(12.5)
    else:
        # close
        servo.ChangeDutyCycle(2.5)
      
# used to detected motion
def motionDetection(userIn):

    # current is used to make the sensor work for 0.5 sec
    current = time.time()
    
    # works in two conditions
        # if !userIn, if something detected call ultrasonic
        # if userIn, if something detected buzzOn
    while not (GPIO.input(motion)) or (userIn and time.time() > current + 0.5):
        if GPIO.input(motion):
            if userIn:
                buzzOn()
                return False
            else:     
                return True
      
# detect the distance of the user
def ultrasonic_read(trig_pin, echo_pin):
    GPIO.output(trig_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trig_pin, GPIO.LOW)
    
    while GPIO.input(echo_pin)==0:
        pulse_start = time.time()
    
    while GPIO.input(echo_pin)==1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150

    # userClose is used to check that the user got close to the 
    userClose = False
    # userDone is used to check that the user left the atm (break the loop)
    userDone = False

    enteredTime = time.time()

    while not (userDone) or (time.time() > enteredTime + 10 and not (userClose)):
        if distance < 40 and not (userClose):       # user is close to the atm
            # take pic once
            if not (userClose):
                video(True)
            
            userClose = True
            lightStatus('close')
            doorStatus('close')
            
        if distance > 40 and userClose:             # user left the atm
            video(False)
            time.sleep(10)
            lightStatus = 'open'
            doorStatus('open')
            userDone = True
            
        # called as long as the user is close
        if userClose:
            motionDetection(True)


while True:
    lightStatus('open')
    if motionDetection(False):
        ultrasonic_read(dist_t, dist_eco) 
