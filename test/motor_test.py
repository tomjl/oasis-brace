import pigpio
import time


STEP=12
DIR=17
MS1=27
MS2=22
MS3=23
ENABLE=24

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

lister = []
for i in range(10000):
	t0 = time.time()
	start()
	stop()
	lister.append(time.time()-t0)

