import sys
import csv
import math
import time
import board
import busio
import adafruit_bno08x
import util
from i2c import BNO08X_I2C, _BNO08X_DEFAULT_ADDRESS
from bno08x import (
	BNO_REPORT_ACCELEROMETER,
	BNO_REPORT_GYROSCOPE,
	BNO_REPORT_MAGNETOMETER,
	BNO_REPORT_LINEAR_ACCELERATION,
	BNO_REPORT_ROTATION_VECTOR,
	BNO_REPORT_ACTIVITY_CLASSIFIER,
)


i2c = busio.I2C(board.SCL, board.SDA)
bno1 = BNO08X_I2C(i2c, address= _BNO08X_DEFAULT_ADDRESS)
bno2 = BNO08X_I2C(i2c, address= _BNO08X_DEFAULT_ADDRESS+1)


bno1.enable_feature(BNO_REPORT_ROTATION_VECTOR)
bno2.enable_feature(BNO_REPORT_ROTATION_VECTOR)

def dict_2_list(d):
	l = []
	for key,value in d.items():
		l.append(value)
	return(l)

assert len(sys.argv) > 1 # make sure a name was passed
out_file = sys.argv[-1]

t0 = time.time()

with open(out_file,'w') as file:
	writer = csv.writer(file)
	while True:

		readings1 = bno1.all_readings[BNO_REPORT_ROTATION_VECTOR]
		readings2 = bno2.all_readings[BNO_REPORT_ROTATION_VECTOR]

		angle1 = util.euler_from_quaternion(*readings1)
		angle2 = util.euler_from_quaternion(*readings2)

		data_line = [time.time()]+list(readings1)+list(readings2)+list(angle1)+list(angle2)
		print(time.time()-t0)
		t0 = time.time()
		writer.writerow(data_line)
		