import pigpio
import time
import board
import busio
import parallel
import util
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



# --------- Initialize IMUs --------- #

i2c = busio.I2C(board.SCL, board.SDA)
IMU1 = BNO08X_I2C(i2c, address= _BNO08X_DEFAULT_ADDRESS)
IMU2 = BNO08X_I2C(i2c, address= _BNO08X_DEFAULT_ADDRESS+1)

# can't really afford to grab gravity for now. maybe get it once in the beginning?
ENABLED_REPORTS = [
					BNO_REPORT_LINEAR_ACCELERATION,
					BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR
]

for sensor in [IMU1, IMU2]:
	for report in ENABLED_REPORTS:
		sensor.enable_feature(report)

IMU_SAMPLING_PERIOD = 0.0001

IMU_t = parallel.IMU_Thread(IMU1, IMU2, IMU_SAMPLING_PERIOD)

# ----------------------------------- #


# --------- Initialize Motors --------- #

pi = pigpio.pi()

motor1 = ROB12859(pi, _PIN_CONFIG_1)
motor2 = ROB12859(pi, _PIN_CONFIG_2)
motors = BraceMotors(motor1, motor2)

motor_t = parallel.Motor_Thread(motors)
 
# ------------------------------------- #

# --------- GO GO GO !!! --------- #

motor_t.start()
IMU_t.start()


TEST_PATH = [0, 5, 2, 4, 9, 1, 10, 0]
idx = 0
print("starting")
try:
	while True:
		while not IMU_t.q.empty():
			accel = IMU_t.q.get()[1][BNO_REPORT_LINEAR_ACCELERATION]

		motor_t.q.put(TEST_PATH[idx%len(TEST_PATH)])
		idx += 1
		time.sleep(4)

except:
	IMU_t.cancel()
	motor_t.cancel()





