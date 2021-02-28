import pigpio
import time
import board
import busio
import parallel
import util
from queue import Queue
from classify import SimpleMotionClassifier
from rob12859 import ROB12859, BraceMotors
from rob12859 import _PIN_CONFIG_1, _PIN_CONFIG_2 
from i2c import BNO08X_I2C, _BNO08X_DEFAULT_ADDRESS
from bno08x import (
	BNO_REPORT_ACCELEROMETER,
	BNO_REPORT_GYROSCOPE,
	BNO_REPORT_MAGNETOMETER,
	BNO_REPORT_LINEAR_ACCELERATION,
	BNO_REPORT_ROTATION_VECTOR,
	BNO_REPORT_ACTIVITY_CLASSIFIER,
	BNO_REPORT_GRAVITY,
	BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR,
)

# --------- Initialize Queues ---------#

data_q       = Queue()
motormoves_q = Queue() 

# ----------------------------------- #


# --------- Initialize IMUs --------- #

i2c = busio.I2C(board.SCL, board.SDA)
IMU1 = BNO08X_I2C(i2c, address= _BNO08X_DEFAULT_ADDRESS)
IMU2 = BNO08X_I2C(i2c, address= _BNO08X_DEFAULT_ADDRESS+1)

# can't really afford to grab gravity for now. maybe get it once in the beginning?
ENABLED_REPORTS = [
					BNO_REPORT_ROTATION_VECTOR
]

for sensor in [IMU1, IMU2]:
	for report in ENABLED_REPORTS:
		sensor.enable_feature(report)

IMU_t = parallel.IMU_Thread(IMU1, IMU2, queue=data_q)

# ----------------------------------- #


# --------- Initialize Motors --------- #

pi = pigpio.pi()

motor1 = ROB12859(pi, _PIN_CONFIG_1)
motor2 = ROB12859(pi, _PIN_CONFIG_2)
motors = BraceMotors(motor1, motor2)

motor_t = parallel.Motor_Thread(motors, queue=motormoves_q)
 
# ------------------------------------- #


# --------- Initialize Classifier --------- #

classifier = SimpleMotionClassifier()
classifier_t = parallel.Classifier_Thread(classifier, data_q, motormoves_q)

# ----------------------------------- #


# --------- GO GO GO !!! --------- #

motor_t.start()
IMU_t.start()
classifier_t.start()


TEST_PATH = [0, 5, 2, 4, 9, 1, 10, 0]
idx = 0
print("starting")
try:
	while True:

		motor_t.q.put(TEST_PATH[idx%len(TEST_PATH)])
		idx += 1
		time.sleep(4)

except:
	print('CANCELLING')
	IMU_t.cancel()
	motor_t.cancel()





