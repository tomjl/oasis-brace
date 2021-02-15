import time
from threading import Thread, Event
from queue import Queue
from i2c import BNO08X_I2C
from i2c import _BNO08X_DEFAULT_ADDRESS


class IMU_Thread(Thread):
	"""
	The wrapper that lets us order motors to do things and not wait for it to complete 
	
	Repeats every sampling period
			t = IMU_Thread(imu, 3)
			t.start()
			t.cancel()     # stop the thread's action if it's still waiting

	modified from https://github.com/python/cpython/blob/master/Lib/threading.py
	to repeat instead of being one-off.

	"""

	def __init__(self, imu, sample_period, queue=Queue()):
		Thread.__init__(self)
		self.sample_period = sample_period
		self.imu = imu
		self.q = queue
		self.finished = Event()
		self.t0 = time.time()

	def cancel(self):
		"""Stop the timer if it hasn't finished yet."""
		self.finished.set()

	def run(self):
		while not self.finished.is_set():
			self.finished.wait(self.sample_period)
			
			readings = self.imu.all_readings
			readings['dt'] = time.time()-self.t0
			print(readings['dt'])
			self.t0 = time.time()

			self.q.put(readings)




class Motor_Thread(Thread):
	"""
	The wrapper that lets us order motors to do things and not wait for it to complete 
	Runs until you stop it
	Accepts motor position commands into a queue.
	"""
	def __init__(self, motor, queue=Queue()):
		Thread.__init__(self)
		self.motor = motor
		self.q = queue
		self.finished = Event()

	def cancel(self):
		self.finished.set()

	def run(self):
		while not self.finished.is_set():
			if not self.q.empty():
				position = self.q.get()
				self.motor.movetoPosition(position)
				
				# safety wait seems to make threads share better :)
				time.sleep(1)
				# otherwise this thread seems to hog cpu time.











