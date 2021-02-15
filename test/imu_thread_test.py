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
imu = BNO08X_I2C(i2c, address= _BNO08X_DEFAULT_ADDRESS)


imu.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)
imu.enable_feature(BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR)
imu.enable_feature(BNO_REPORT_GRAVITY)


SAMPLING_PERIOD = 0.2

imu_thread = parallel.IMU_Thread(imu)
dataQ = imu_thread.q 

timer = parallel.Timer(3,imu_thread)
timer.start()

while True:
	if not dataQ.empty():
		print(dataQ.get())
	

	print("smile :)")
	time.sleep(0.5)
		