import pigpio
import time
import board
import busio
import parallel
import util
from rob12859 import ROB12859
from rob12859 import _DEFAULT_PIN_CONFIG
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

IMU_SAMPLING_PERIOD = 0.2

IMU1_t = parallel.IMU_Thread(IMU1, IMU_SAMPLING_PERIOD)
IMU2_t = parallel.IMU_Thread(IMU2, IMU_SAMPLING_PERIOD)

# ----------------------------------- #


# --------- Initialize Motors --------- #

pi = pigpio.pi()
motor = ROB12859(pi, _DEFAULT_PIN_CONFIG)
motor_t = parallel.Motor_Thread(motor)
 
# ------------------------------------- #

# --------- GO GO GO !!! --------- #

motor_t.start()
IMU1_t.start()
IMU2_t.start()


TEST_PATH = [0, 5, 2, 4, 9, 1, 10, 0]
idx = 0
print("starting")
try:
	while True:
		while not IMU1_t.q.empty():
			accel = IMU1_t.q.get()[BNO_REPORT_LINEAR_ACCELERATION]
		while not IMU2_t.q.empty():
			accel = IMU2_t.q.get()[BNO_REPORT_LINEAR_ACCELERATION]

		motor_t.q.put(TEST_PATH[idx%len(TEST_PATH)])
		idx += 1
		time.sleep(1)

except:
	IMU1_t.cancel()
	IMU2_t.cancel()
	motor_t.cancel()





