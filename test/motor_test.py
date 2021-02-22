import pigpio
import time


STEP=13
DIR=10
MS1=9
MS2=11
MS3=25
ENABLE=8

pi = pigpio.pi()

pi.write(MS1,0)
pi.write(MS2,0)
pi.write(MS3,0)

pi.write(DIR,1)
pi.write(ENABLE,0)

pi.set_PWM_dutycycle(STEP,0)
pi.set_PWM_frequency(STEP,1000)

def stop():
	pi.set_PWM_dutycycle(STEP,0)

def start():
	pi.set_PWM_dutycycle(STEP,128)

