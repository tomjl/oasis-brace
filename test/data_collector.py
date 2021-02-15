import csv
import math
import time
import board
import busio
import adafruit_bno08x
from adafruit_bno08x.i2c import BNO08X_I2C, _BNO08X_DEFAULT_ADDRESS
from adafruit_bno08x import (
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


bno1.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)
bno1.enable_feature(BNO_REPORT_ROTATION_VECTOR)

bno2.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)
bno2.enable_feature(BNO_REPORT_ROTATION_VECTOR)

def dict_2_list(d):
	l = []
	for key,value in d.items():
		l.append(value)
	return(l)

out_file = 'walkstairwalkstair3.csv'
idx = 0

t0 = time.time()

SAMPLING_PERIOD = 0.15

with open(out_file,'w') as file:
	writer = csv.writer(file)
	while True:
		while time.time()-t0 < SAMPLING_PERIOD:
			continue
		print(time.time()-t0)
		t0 = time.time()

		a1 = list(bno1.quaternion)
		thing1 = dict_2_list(bno1._readings)
		# g1 = list(bno1.gyro)
		# m1 = list(bno1.magnetic)
		# la1= list(bno1.linear_acceleration)
		# rv1=list(bno1.quaternion)
		# aclas1 = [bno1.activity_classification['most_likely']]

		a2 = list(bno2.quaternion)
		thing2 = dict_2_list(bno2._readings)
		# g2 = list(bno2.gyro)
		# m2 = list(bno2.magnetic)
		# la2= list(bno2.linear_acceleration)
		# rv2=list(bno2.quaternion)
		# aclas2 = [bno2.activity_classification['most_likely']]

		data_line = [idx]+thing1+thing2
		writer.writerow(data_line)
		idx += 1
		