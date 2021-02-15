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
    BNO_REPORT_ROTATION_VECTOR,
    BNO_REPORT_RAW_ACCELEROMETER,
    BNO_REPORT_ACTIVITY_CLASSIFIER
)

def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.degrees(math.atan2(t0, t1))
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.degrees(math.asin(t2))
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.degrees(math.atan2(t3, t4))
     
        return roll_x, pitch_y, yaw_z

i2c = busio.I2C(board.SCL, board.SDA)
bno1 = BNO08X_I2C(i2c, address= _BNO08X_DEFAULT_ADDRESS)
bno2 = BNO08X_I2C(i2c, address= _BNO08X_DEFAULT_ADDRESS+1)

bno1.enable_feature(BNO_REPORT_ACCELEROMETER)
bno1.enable_feature(BNO_REPORT_ROTATION_VECTOR)

bno2.enable_feature(BNO_REPORT_ACCELEROMETER)
bno2.enable_feature(BNO_REPORT_ROTATION_VECTOR)

while True:
	time.sleep(0.1)
	x1, y1, z1 = bno1.acceleration
	# qw1, qx1, qy1, qz1 = bno1.quaternion
	roll1, pitch1, yaw1 = euler_from_quaternion(*bno1.quaternion)

	x2, y2, z2 = bno2.acceleration
	# qw2, qx2, qy2, qz2 = bno2.quaternion
	roll2, pitch2, yaw2 = euler_from_quaternion(*bno2.quaternion)


	print('accel1: %1.2f %1.2f %1.2f ang1: %.3f %.3f %.3f ------ accel2: %1.2f %1.2f %1.2f ang2: %.3f %.3f %.3f' %(x1, y1, z1, roll1, pitch1, yaw1, x2, y2, z2, roll2, pitch2, yaw2))



