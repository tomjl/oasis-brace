import csv
import math
import time
import board
import busio
import bno08x
import parallel
import util
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

imu_thread = parallel.IMU_Thread(IMU1, IMU2, IMU_SAMPLING_PERIOD)

imu_thread.start()

while True:
	if not imu_thread.q.empty():
		print(imu_thread.q.get())
	

	print("smile :)")
	time.sleep(0.5)
		